"""
Сервисы для модуля аутентификации.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.config import settings
from core.exceptions import AuthenticationError, BusinessLogicError, NotFoundError
from core.logging import get_logger
from core.security import (
    create_access_token,
    create_refresh_token,
    generate_password_reset_token,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
    verify_token,
)
from modules.auth.domain.models import RefreshToken
from modules.auth.domain.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    TokenPair,
    UserInfo,
)
from modules.users.domain.models import User, Student, UserRole
from modules.mentors.domain.models import Mentor

logger = get_logger(__name__)


class AuthService:
    """Сервис аутентификации."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def register_user(self, register_data: RegisterRequest) -> AuthResponse:
        """Регистрация нового пользователя (только студенты)."""
        logger.info("User registration attempt", email=register_data.email, role=register_data.role)
        
        # Менторы создаются только через админку
        if register_data.role == UserRole.MENTOR:
            raise BusinessLogicError("Регистрация менторов недоступна. Менторы создаются администратором.")
        
        # Админы не могут регистрироваться
        if register_data.role == UserRole.ADMIN:
            raise BusinessLogicError("Регистрация администраторов недоступна")
        
        # Проверяем, не существует ли пользователь с таким email
        existing_user = await self._get_user_by_email(register_data.email)
        if existing_user:
            raise BusinessLogicError("Пользователь с таким email уже существует")
        
        # Создаем пользователя (только студент)
        user = User(
            email=register_data.email,
            password_hash=get_password_hash(register_data.password),
            name=register_data.name,
            role=UserRole.STUDENT,  # Всегда студент
            phone=register_data.phone,
            timezone=register_data.timezone,
            locale=register_data.locale,
            is_active=True
        )
        
        self.db.add(user)
        await self.db.flush()
        
        # Создаем профиль студента
        student_profile = Student(user_id=user.id)
        self.db.add(student_profile)
        
        # Коммитим изменения
        await self.db.commit()
        
        logger.info("User registered successfully", user_id=user.id, email=user.email, role=user.role)
        
        # Создаем токены
        access_token = create_access_token(subject=str(user.id))
        refresh_token_str = create_refresh_token(subject=str(user.id))
        
        # Сохраняем refresh токен в базе
        await self._save_refresh_token(
            user_id=user.id,
            token=refresh_token_str,
            device_info=None  # TODO: Получать из User-Agent
        )
        
        return AuthResponse(
            user=UserInfo.from_orm(user),
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token_str,
                token_type="bearer",
                expires_in=settings.JWT_EXPIRES_MINUTES * 60,
            ),
        )
    
    async def login_user(self, login_data: LoginRequest) -> AuthResponse:
        """Аутентификация пользователя через ORM (AsyncSession)."""
        logger.info("User login attempt", email=login_data.email)

        # Ищем пользователя через ORM
        stmt = select(User).where(User.email == login_data.email.lower())
        result = await self.db.execute(stmt)
        user: User | None = result.scalar_one_or_none()

        if not user:
            raise AuthenticationError("Неверный email или пароль")

        # Проверяем пароль
        if not verify_password(login_data.password, user.password_hash):
            logger.warning("Failed login attempt - invalid password", email=login_data.email)
            raise AuthenticationError("Неверный email или пароль")

        # Проверяем активность
        if not user.is_active:
            raise AuthenticationError("Аккаунт деактивирован")

        # Создаем токены
        access_token = create_access_token(subject=str(user.id))
        refresh_token_str = create_refresh_token(subject=str(user.id))

        # Сохраняем refresh токен в базе
        await self._save_refresh_token(user_id=user.id, token=refresh_token_str, device_info=None)

        return AuthResponse(
            user=UserInfo.from_orm(user),
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token_str,
                token_type="bearer",
                expires_in=settings.JWT_EXPIRES_MINUTES * 60,
            ),
        )
    
    async def refresh_access_token(self, refresh_token_str: str) -> TokenPair:
        """Обновление access токена через refresh токен."""
        logger.info("Token refresh attempt")
        
        # Проверяем refresh токен
        try:
            payload = verify_token(refresh_token_str, token_type="refresh")
            user_id = UUID(payload["sub"])
            token_jti = payload.get("jti")
        except Exception as e:
            logger.warning("Invalid refresh token", error=str(e))
            raise AuthenticationError("Неверный refresh токен")
        
        # Ищем токен в базе данных
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.token == refresh_token_str,
            RefreshToken.is_revoked == False
        )
        result = await self.db.execute(stmt)
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            logger.warning("Refresh token not found in database", user_id=user_id)
            raise AuthenticationError("Неверный refresh токен")
        
        # Проверяем, не истек ли токен
        if db_token.expires_at < datetime.utcnow():
            logger.warning("Refresh token expired", user_id=user_id)
            raise AuthenticationError("Refresh токен истек")
        
        # Проверяем, существует ли пользователь
        user = await self._get_user_by_id(user_id)
        if not user or not user.is_active:
            logger.warning("User not found or inactive", user_id=user_id)
            raise AuthenticationError("Пользователь не найден или деактивирован")
        
        # Создаем новый access токен и обновляем refresh токен
        access_token = create_access_token(subject=str(user_id))
        new_refresh = create_refresh_token(subject=str(user_id))
        # Сохраняем новый refresh токен (старый можно оставить валидным до истечения)
        await self._save_refresh_token(user_id=user_id, token=new_refresh, device_info=None)
        
        logger.info("Token refreshed successfully", user_id=user_id)
        
        return TokenPair(
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRES_MINUTES * 60,
        )
    
    async def revoke_refresh_token(self, refresh_token_str: str) -> bool:
        """Отзыв refresh токена (logout)."""
        logger.info("Revoking refresh token")
        
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        result = await self.db.execute(stmt)
        db_token = result.scalar_one_or_none()
        
        if db_token:
            db_token.is_revoked = True
            await self.db.commit()
            logger.info("Refresh token revoked", token_id=db_token.id, user_id=db_token.user_id)
            return True
        
        return False
    
    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """Отзыв всех refresh токенов пользователя."""
        logger.info("Revoking all user tokens", user_id=user_id)
        
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
        result = await self.db.execute(stmt)
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.is_revoked = True
            count += 1
        
        if count > 0:
            await self.db.commit()
        
        logger.info("Revoked user tokens", user_id=user_id, count=count)
        return count
    
    async def get_current_user(self, access_token: str) -> User:
        """Получение текущего пользователя по access токену."""
        try:
            payload = verify_token(access_token, token_type="access")
            user_id = UUID(payload["sub"])
        except Exception as e:
            logger.warning("Invalid access token", error=str(e))
            raise AuthenticationError("Неверный access токен")
        
        user = await self._get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("Пользователь не найден")
        
        if not user.is_active:
            raise AuthenticationError("Аккаунт деактивирован")
        
        return user
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email."""
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _save_refresh_token(
        self, 
        user_id: UUID, 
        token: str, 
        device_info: Optional[str] = None
    ) -> RefreshToken:
        """Сохранение refresh токена в базе данных."""
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
        
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            device_info=device_info,
            is_revoked=False
        )
        
        self.db.add(db_token)
        await self.db.commit()
        
        return db_token
    
    async def request_password_reset(self, email: str) -> str:
        """Запрос на сброс пароля."""
        logger.info("Password reset requested", email=email)
        
        # Проверяем существует ли пользователь (но не раскрываем эту информацию)
        user = await self._get_user_by_email(email)
        
        if not user:
            # Возвращаем успех даже если пользователь не существует (безопасность)
            logger.info("Password reset requested for non-existent email", email=email)
            return "fake_token"  # Фейковый токен для безопасности
        
        if not user.is_active:
            logger.warning("Password reset requested for inactive user", user_id=user.id)
            return "fake_token"
        
        # Генерируем токен для сброса пароля
        reset_token = generate_password_reset_token(user.email)
        
        # TODO: Отправить email с токеном
        # Пока логируем токен для тестирования
        logger.info(
            "Password reset token generated",
            user_id=user.id,
            email=user.email,
            token=reset_token,
            reset_link=f"http://localhost:5173/reset-password?token={reset_token}"
        )
        
        return reset_token
    
    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Подтверждение сброса пароля по токену."""
        logger.info("Password reset confirmation attempt")
        
        # Проверяем и извлекаем email из токена
        email = verify_password_reset_token(token)
        
        if not email:
            logger.warning("Invalid password reset token")
            raise AuthenticationError("Неверный или истекший токен сброса пароля")
        
        # Находим пользователя
        user = await self._get_user_by_email(email)
        
        if not user:
            logger.error("User not found for password reset", email=email)
            raise NotFoundError("Пользователь не найден")
        
        if not user.is_active:
            logger.warning("Password reset for inactive user", user_id=user.id)
            raise BusinessLogicError("Аккаунт деактивирован")
        
        # Обновляем пароль
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Отзываем все существующие refresh токены для безопасности
        await self.revoke_all_user_tokens(user.id)
        
        await self.db.commit()
        
        logger.info("Password reset successful", user_id=user.id, email=user.email)
        
        return True
    
    async def change_password(
        self, 
        user_id: UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Смена пароля авторизованным пользователем."""
        logger.info("Password change attempt", user_id=user_id)
        
        # Получаем пользователя
        user = await self._get_user_by_id(user_id)
        
        if not user:
            logger.error("User not found for password change", user_id=user_id)
            raise NotFoundError("Пользователь не найден")
        
        # Проверяем текущий пароль
        if not verify_password(current_password, user.password_hash):
            logger.warning("Invalid current password", user_id=user_id)
            raise AuthenticationError("Неверный текущий пароль")
        
        # Проверяем что новый пароль отличается от старого
        if verify_password(new_password, user.password_hash):
            raise BusinessLogicError("Новый пароль должен отличаться от текущего")
        
        # Обновляем пароль
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Отзываем все refresh токены кроме текущего (опционально)
        # Для дополнительной безопасности можно отозвать все
        await self.revoke_all_user_tokens(user.id)
        
        await self.db.commit()
        
        logger.info("Password changed successfully", user_id=user_id)
        
        return True
    
    async def cleanup_expired_tokens(self) -> int:
        """Очистка истекших refresh токенов."""
        logger.info("Starting refresh token cleanup")
        
        # Помечаем истекшие токены как отозванные
        stmt = select(RefreshToken).where(
            RefreshToken.expires_at < datetime.utcnow(),
            RefreshToken.is_revoked == False
        )
        result = await self.db.execute(stmt)
        expired_tokens = result.scalars().all()
        
        count = 0
        for token in expired_tokens:
            token.is_revoked = True
            count += 1
        
        if count > 0:
            await self.db.commit()
        
        logger.info("Refresh token cleanup completed", cleaned_count=count)
        return count

