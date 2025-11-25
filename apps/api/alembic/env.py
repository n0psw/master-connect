"""
Alembic environment configuration.
"""
import asyncio
import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Добавляем src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Убеждаемся, что .env файл загружается из корня проекта
# Alembic запускается из apps/api/alembic/, а .env в корне проекта
alembic_dir = Path(__file__).parent.parent.parent.parent  # apps/api/alembic -> project root
env_file = alembic_dir / ".env"
if env_file.exists():
    # Устанавливаем переменную окружения для pydantic-settings
    os.environ.setdefault("ENV_FILE", str(env_file))

from core.config import settings
from db.base import Base

# Импортируем все модели для автогенерации миграций
from modules.users.domain.models import User, Student
from modules.auth.domain.models import RefreshToken
from modules.mentors.domain.models import Mentor, MentorUniversity
from modules.availability.domain.models import AvailabilityRule, TimeOff, MentorSettings
from modules.bookings.domain.models import Booking
from modules.reviews.domain.models import Review
from modules.chat.domain.models import Dialog, Message
from modules.support.domain.models import SupportTicket
from modules.payments.domain.models import PaymentEvidence
from modules.settings.domain.models import GlobalSettings
from modules.admin.domain.models import AuditLog
from modules.notifications.domain.models import Notification

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    """Получение URL базы данных."""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with provided connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

