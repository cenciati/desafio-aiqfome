from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.__core__.domain.entity.user import User
from app.__core__.domain.repository.repository import IUserRepository
from app.infra.postgres.orm.user_orm import UserORM


class PostgresUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_one(self, entity: User) -> None:
        user = UserORM.model_validate(entity.to_orm())
        self.session.add(user)
        await self.session.commit()

    async def fetch_one(self, id: str) -> Optional[User]:
        result = await self.session.execute(select(UserORM).where(UserORM.id == id))
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            return None
        return User.to_domain(user_orm)

    async def fetch_one_by_slug(self, slug: str) -> Optional[User]:
        result = await self.session.execute(select(UserORM).where(UserORM.slug == slug))
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            return None
        return User.to_domain(user_orm)
