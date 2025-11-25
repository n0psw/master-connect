"""
Модуль для работы с базой данных.
"""
from .base import Base
from .session import get_db, get_session

__all__ = ["Base", "get_db", "get_session"]

