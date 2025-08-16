from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import delete, func, select, update

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.repository.pagination import PaginationInput
from app.__core__.domain.repository.repository import ICustomerRepository
from app.infra.postgres.orm.customer_orm import CustomerORM


class PostgresCustomerRepository(ICustomerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_one(self, entity: Customer) -> None:
        customer = entity.to_orm()
        self.session.add(customer)
        await self.session.commit()

    async def fetch_one(self, id: str) -> Optional[Customer]:
        return await self._fetch_one_by_field("id", id)

    async def fetch_one_by_email(self, email: str) -> Optional[Customer]:
        return await self._fetch_one_by_field("email", email)

    async def _fetch_one_by_field(self, field: str, value: Any) -> Optional[Customer]:
        query = (
            select(CustomerORM)
            .where(getattr(CustomerORM, field) == value)
            .options(selectinload(CustomerORM.favorite_products))
        )
        result = await self.session.execute(query)
        customer_orm = result.scalar_one_or_none()
        if customer_orm is None:
            return None
        return Customer.to_domain(customer_orm)

    async def fetch_many(self, pagination: PaginationInput) -> List[Customer]:
        query = select(CustomerORM).options(selectinload(CustomerORM.favorite_products))

        offset = (pagination.page - 1) * pagination.per_page
        query = query.offset(offset)
        query = query.limit(pagination.per_page)

        result = await self.session.execute(query)
        raw_customers = result.scalars().all()
        return [Customer.to_domain(raw_customer) for raw_customer in raw_customers]

    async def count_all(self) -> int:
        query = select(func.count()).select_from(CustomerORM)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def update_one(self, new_entity: Customer) -> None:
        query = (
            update(CustomerORM)
            .where(CustomerORM.id == new_entity.id)
            .values(new_entity.to_orm().model_dump(exclude_unset=True))
        )
        await self.session.execute(query)
        await self.session.commit()

    async def delete_one(self, id: str) -> None:
        query = delete(CustomerORM).where(CustomerORM.id == id)
        await self.session.execute(query)
        await self.session.commit()
