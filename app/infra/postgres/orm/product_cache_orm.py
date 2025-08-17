from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class ProductCacheORM(SQLModel, table=True):
    __tablename__ = "products_cache"

    id: int = Field(primary_key=True, index=True)
    title: str
    image_url: str
    price: Decimal
    review_rate: Optional[Decimal]
    review_count: Optional[int]
    fetched_at: datetime
