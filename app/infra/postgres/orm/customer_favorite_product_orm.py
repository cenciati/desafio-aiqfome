from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.infra.postgres.orm.customer_orm import CustomerORM


class CustomerFavoriteProductORM(SQLModel, table=True):
    __tablename__ = "customer_favorite_products"

    customer_id: UUID = Field(foreign_key="customers.id", primary_key=True)
    product_id: UUID = Field(primary_key=True)
    favorited_at: datetime

    customer: CustomerORM = Relationship(back_populates="favorite_products")
