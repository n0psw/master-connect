from typing import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.domain.models import User, UserRole


async def get_admin_user_ids(db: AsyncSession) -> Iterable[UUID]:
    stmt = select(User.id).where(User.role == UserRole.ADMIN, User.is_active.is_(True))
    res = await db.execute(stmt)
    return [row[0] for row in res.fetchall()]

