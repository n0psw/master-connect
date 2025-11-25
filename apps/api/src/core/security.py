"""
Модуль безопасности для работы с JWT токенами и паролями.
"""
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

from .config import settings
from .exceptions import AuthenticationError
from .logging import get_logger

logger = get_logger(__name__)

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Алгоритм JWT
ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Создание JWT access токена."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """Создание JWT refresh токена."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32),  # Unique token ID
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Проверка JWT токена."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # Проверяем тип токена
        if payload.get("type") != token_type:
            raise AuthenticationError("Неверный тип токена")
        
        # Проверяем наличие subject
        token_subject = payload.get("sub")
        if token_subject is None:
            raise AuthenticationError("Токен не содержит subject")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Токен истек")
    except jwt.JWTError as e:
        logger.warning("JWT decode error", error=str(e), token_type=token_type)
        raise AuthenticationError("Неверный токен")


def get_password_hash(password: str) -> str:
    """Хеширование пароля."""
    # Bcrypt ограничивает длину пароля 72 байтами
    # Обрезаем пароль до 72 байт, если он длиннее
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    try:
        # Bcrypt ограничивает длину пароля 72 байтами
        # Обрезаем пароль до 72 байт, если он длиннее (как при хешировании)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning("Password verification error", error=str(e))
        return False


def generate_password_reset_token(email: str) -> str:
    """Генерация токена для сброса пароля."""
    delta = timedelta(hours=1)  # Токен действует 1 час
    now = datetime.utcnow()
    expires = now + delta
    
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": email,
            "type": "password_reset"
        },
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Проверка токена для сброса пароля."""
    try:
        decoded_token = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        
        if decoded_token.get("type") != "password_reset":
            return None
            
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def generate_api_key() -> str:
    """Генерация API ключа."""
    return secrets.token_urlsafe(32)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Маскировка чувствительных данных для логов."""
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars)

