"""
Сервисы для модуля пользователей.
"""
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import NotFoundError
from core.logging import get_logger
from modules.users.domain.models import Student, User, UserRole
from modules.users.domain.schemas import (
    StudentProfileCreate,
    StudentProfileResponse,
    StudentProfileUpdate,
    UserCreate,
    UserResponse,
    UserStatsOverview,
    UserUpdate,
    UserWithProfile,
)

logger = get_logger(__name__)


class UserService:
    """Сервис для управления пользователями."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_user_by_id(self, user_id: UUID, include_profile: bool = False):
        """Получение пользователя по ID.
        include_profile: загружать ли связанные профили (student/mentor) для model_validate.
        """
        query = select(User).where(User.id == user_id)
        if include_profile:
            query = query.options(
                selectinload(User.student_profile),
                selectinload(User.mentor_profile),
            )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if include_profile:
            user_data = UserResponse.model_validate(user, from_attributes=True)
            student_profile = None
            if user.student_profile:
                student_profile = StudentProfileResponse.model_validate(
                    user.student_profile, from_attributes=True
                )
            return UserWithProfile(
                **user_data.model_dump(),
                student_profile=student_profile
            )
        
        return UserResponse.model_validate(user, from_attributes=True)
    
    async def get_all_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        role_filter: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[UserResponse], int]:
        """Получение списка всех пользователей с фильтрацией."""
        query = select(User)
        count_query = select(func.count(User.id))
        
        conditions = []
        
        # Фильтр по поиску
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")
            )
            conditions.append(search_filter)
        
        # Фильтр по роли
        if role_filter:
            conditions.append(User.role == role_filter)
        
        # Фильтр по активности
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        
        # Применяем условия
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Подсчет общего количества
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Пагинация и сортировка
        offset = (page - 1) * page_size
        query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
        
        # Выполнение запроса
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        # Преобразуем в ответы
        user_responses = [UserResponse.model_validate(user, from_attributes=True) for user in users]
        
        return user_responses, total

    # Совместимость с роутом /users: сигнатура, которую ожидает API слой
    async def get_users_list(
        self,
        page: int,
        page_size: int,
        role: Optional[UserRole],
        is_active: Optional[bool],
        search_query: Optional[str],
    ) -> Tuple[List[UserResponse], int]:
        return await self.get_all_users(
            page=page,
            page_size=page_size,
            search=search_query,
            role_filter=role,
            is_active=is_active,
        )
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Создание нового пользователя (только для админов)."""
        user = User(
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            is_active=user_data.is_active,
            timezone=user_data.timezone,
            language=user_data.language,
            phone=user_data.phone,
            avatar_url=user_data.avatar_url
        )
        
        # Устанавливаем пароль если он предоставлен
        if user_data.password:
            from core.security import get_password_hash
            user.password_hash = get_password_hash(user_data.password)
        
        self.db.add(user)
        await self.db.commit()
        
        logger.info("User created by admin", user_id=user.id, email=user.email, role=user.role)
        
        return UserResponse.model_validate(user, from_attributes=True)
    
    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
        updated_by: UUID
    ) -> UserWithProfile:
        """Обновление пользователя."""
        user = await self._get_user_or_404(user_id)
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password" and value:
                from core.security import get_password_hash
                user.password_hash = get_password_hash(value)
            else:
                setattr(user, field, value)
        
        await self.db.commit()
        
        logger.info("User updated", user_id=user_id, updated_by=updated_by)
        
        query = select(User).where(User.id == user_id).options(
            selectinload(User.student_profile),
            selectinload(User.mentor_profile),
        )
        result = await self.db.execute(query)
        updated_user = result.scalar_one()
        
        user_data_response = UserResponse.model_validate(updated_user, from_attributes=True)
        student_profile = None
        if updated_user.student_profile:
            student_profile = StudentProfileResponse.model_validate(
                updated_user.student_profile, from_attributes=True
            )
        return UserWithProfile(
            **user_data_response.model_dump(),
            student_profile=student_profile
        )
    
    async def activate_deactivate_user(
        self,
        user_id: UUID,
        is_active: bool,
        admin_id: UUID
    ) -> UserResponse:
        """Активация/деактивация пользователя."""
        user = await self._get_user_or_404(user_id)
        
        old_status = user.is_active
        user.is_active = is_active
        
        await self.db.commit()
        await self.db.refresh(user)
        
        action = "activated" if is_active else "deactivated"
        logger.info(f"User {action}", user_id=user_id, admin_id=admin_id, old_status=old_status)
        
        return UserResponse.model_validate(user, from_attributes=True)
    
    async def get_student_profile(self, user_id: UUID) -> Optional[StudentProfileResponse]:
        """Получение профиля студента."""
        query = select(Student).where(Student.user_id == user_id)
        result = await self.db.execute(query)
        student = result.scalar_one_or_none()
        
        if not student:
            return None
        
        return StudentProfileResponse.model_validate(student, from_attributes=True)
    
    async def update_student_profile(
        self,
        user_id: UUID,
        profile_data: StudentProfileUpdate
    ) -> StudentProfileResponse:
        """Обновление профиля студента."""
        # Ищем существующий профиль
        query = select(Student).where(Student.user_id == user_id)
        result = await self.db.execute(query)
        student = result.scalar_one_or_none()
        
        if not student:
            # Создаем новый профиль если его нет
            student = Student(user_id=user_id)
            self.db.add(student)
        
        # Обновляем поля
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        
        await self.db.commit()
        
        logger.info("Student profile updated", user_id=user_id)
        
        return StudentProfileResponse.model_validate(student, from_attributes=True)
    
    async def get_user_stats_overview(self) -> UserStatsOverview:
        """Получение общей статистики пользователей."""
        # Общее количество пользователей
        total_query = select(func.count(User.id))
        total_result = await self.db.execute(total_query)
        total_users = total_result.scalar()
        
        # Количество по ролям
        students_query = select(func.count(User.id)).where(User.role == UserRole.STUDENT)
        students_result = await self.db.execute(students_query)
        total_students = students_result.scalar()
        
        mentors_query = select(func.count(User.id)).where(User.role == UserRole.MENTOR)
        mentors_result = await self.db.execute(mentors_query)
        total_mentors = mentors_result.scalar()
        
        admins_query = select(func.count(User.id)).where(User.role == UserRole.ADMIN)
        admins_result = await self.db.execute(admins_query)
        total_admins = admins_result.scalar()
        
        # Активные пользователи
        active_query = select(func.count(User.id)).where(User.is_active == True)
        active_result = await self.db.execute(active_query)
        active_users = active_result.scalar()
        
        # Новые пользователи за последние 30 дней
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        new_query = select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
        new_result = await self.db.execute(new_query)
        new_users_30d = new_result.scalar()
        
        return UserStatsOverview(
            total_users=total_users,
            total_students=total_students,
            total_mentors=total_mentors,
            total_admins=total_admins,
            active_users=active_users,
            new_users_30d=new_users_30d
        )
    
    async def _get_user_or_404(self, user_id: UUID) -> User:
        """Получение пользователя или исключение 404."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User", str(user_id))
        
        return user
