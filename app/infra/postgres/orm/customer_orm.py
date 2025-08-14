from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.infra.postgres.orm.customer_favorite_product_orm import \
        CustomerFavoriteProductORM


class CustomerORM(SQLModel, table=True):
    __tablename__ = "customers"

    id: UUID = Field(primary_key=True, index=True)
    name: str
    email: str = Field(unique=True, index=True)
    created_at: datetime
    updated_at: datetime

    favorite_products: List[CustomerFavoriteProductORM] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
