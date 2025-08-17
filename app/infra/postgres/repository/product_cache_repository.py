from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.__core__.domain.entity.product import Product
from app.__core__.domain.repository.repository import IProductCacheRepository
from app.infra.postgres.orm.product_cache_orm import ProductCacheORM


class PostgresProductCacheRepository(IProductCacheRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_one(self, entity: Product) -> None:
        product_cache = entity.to_orm()
        self.session.add(product_cache)
        await self.session.commit()

    async def fetch_one(self, id: int) -> Optional[Product]:
        query = select(ProductCacheORM).where(ProductCacheORM.id == id)
        result = await self.session.execute(query)
        product_orm = result.scalar_one_or_none()
        if product_orm is None:
            return None
        return Product.to_domain(product_orm)

    async def fetch_many(self, ids: List[int]) -> List[Product]:
        query = select(ProductCacheORM).where(ProductCacheORM.id.in_(ids))
        result = await self.session.execute(query)
        product_orms = result.scalars().all()
        return [Product.to_domain(product_orm) for product_orm in product_orms]

    async def refresh(self, entity: Product) -> None:
        query = (
            update(ProductCacheORM)
            .where(ProductCacheORM.id == entity.id)
            .values(
                title=entity.title,
                image_url=entity.image_url,
                price=entity.price,
                review_rate=entity.review.rate if entity.review else None,
                review_count=entity.review.count if entity.review else None,
                fetched_at=datetime.now(),
            )
        )
        await self.session.execute(query)
        await self.session.commit()
