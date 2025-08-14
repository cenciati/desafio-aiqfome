from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from sqlmodel import Field, SQLModel


class ProductCacheORM(SQLModel, table=True):
    __tablename__ = "products_cache"

    id: int = Field(primary_key=True, index=True)
    title: str
    image_url: str
    price: Decimal
    review_rate: Decimal
    review_count: int
    fetched_at: datetime
    soft_ttl: timedelta
    hard_ttl: timedelta
