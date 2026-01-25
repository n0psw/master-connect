"""
Модуль безопасности для работы с JWT токенами и паролями.
"""
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
import bcrypt

from .config import settings
from .exceptions import AuthenticationError
from .logging import get_logger

logger = get_logger(__name__)

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
    except Exception as e:
        logger.warning("JWT decode error", error=str(e), token_type=token_type)
        raise AuthenticationError("Неверный токен")


def get_password_hash(password: str) -> str:
    """Хеширование пароля используя прямой bcrypt."""
    # Bcrypt ограничивает длину пароля 72 байтами
    # Обрезаем пароль до 72 байт, если он длиннее
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        logger.debug("Password truncated for hashing", original_length=len(password.encode('utf-8')), truncated_length=72)
    
    # Генерируем соль и хешируем пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля используя прямой bcrypt."""
    try:
        # Bcrypt ограничивает длину пароля 72 байтами
        # Обрезаем пароль до 72 байт, если он длиннее (как при хешировании)
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            logger.debug("Password truncated for verification", original_length=len(plain_password.encode('utf-8')), truncated_length=72)
        
        # Проверяем формат хеша
        if not hashed_password or len(hashed_password) < 10:
            logger.warning("Invalid hash format", hash_length=len(hashed_password) if hashed_password else 0)
            return False
        
        # Используем прямой bcrypt для проверки
        hashed_bytes = hashed_password.encode('utf-8')
        result = bcrypt.checkpw(password_bytes, hashed_bytes)
        
        if not result:
            logger.debug("Password verification failed", hash_prefix=hashed_password[:20] if hashed_password else None)
        
        return result
    except Exception as e:
        logger.error("Password verification error", error=str(e), error_type=type(e).__name__)
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
    except Exception:
        return None


def generate_api_key() -> str:
    """Генерация API ключа."""
    return secrets.token_urlsafe(32)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Маскировка чувствительных данных для логов."""
    if len(data) <= visible_chars:
        return "*" * len(data)
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars)

