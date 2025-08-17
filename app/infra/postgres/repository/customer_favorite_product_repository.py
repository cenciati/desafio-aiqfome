from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, func, select

from app.__core__.domain.repository.pagination import PaginationInput
from app.__core__.domain.repository.repository import \
    ICustomerFavoriteProductRepository
from app.__core__.domain.value_object.customer_favorite_product import \
    CustomerFavoriteProduct
from app.infra.postgres.orm.customer_favorite_product_orm import \
    CustomerFavoriteProductORM


class PostgresCustomerFavoriteProductRepository(ICustomerFavoriteProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_one(self, entity: CustomerFavoriteProduct) -> None:
        customer_favorite_product = entity.to_orm()
        self.session.add(customer_favorite_product)
        await self.session.commit()

    async def fetch_one(
        self, customer_id: str, product_id: int
    ) -> Optional[CustomerFavoriteProduct]:
        query = (
            select(CustomerFavoriteProductORM)
            .where(CustomerFavoriteProductORM.customer_id == customer_id)
            .where(CustomerFavoriteProductORM.product_id == product_id)
        )
        result = await self.session.execute(query)
        customer_favorite_product_orm = result.scalar_one_or_none()
        if customer_favorite_product_orm is None:
            return None
        return CustomerFavoriteProduct.to_domain(customer_favorite_product_orm)

    async def fetch_many(
        self, customer_id: str, pagination: PaginationInput
    ) -> List[CustomerFavoriteProduct]:
        query = (
            select(CustomerFavoriteProductORM)
            .where(CustomerFavoriteProductORM.customer_id == customer_id)
            .order_by(CustomerFavoriteProductORM.favorited_at.desc())
        )
        offset = (pagination.page - 1) * pagination.per_page
        query = query.offset(offset)
        query = query.limit(pagination.per_page)

        result = await self.session.execute(query)
        customer_favorite_product_orms = result.scalars().all()
        return [
            CustomerFavoriteProduct.to_domain(customer_favorite_product_orm)
            for customer_favorite_product_orm in customer_favorite_product_orms
        ]

    async def count_all(self, customer_id: str) -> int:
        query = (
            select(func.count())
            .select_from(CustomerFavoriteProductORM)
            .where(CustomerFavoriteProductORM.customer_id == customer_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one()

    async def delete_one(self, customer_id: str, product_id: int) -> None:
        query = (
            delete(CustomerFavoriteProductORM)
            .where(CustomerFavoriteProductORM.customer_id == customer_id)
            .where(CustomerFavoriteProductORM.product_id == product_id)
        )
        await self.session.execute(query)
        await self.session.commit()
