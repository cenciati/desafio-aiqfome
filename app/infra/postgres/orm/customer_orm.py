from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class CustomerORM(SQLModel, table=True):
    __tablename__ = "customers"

    id: UUID = Field(primary_key=True, index=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime
    updated_at: datetime

    favorite_products: Mapped[List["CustomerFavoriteProductORM"]] = Relationship(
        back_populates="customer",
        cascade_delete=True,
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )


from app.infra.postgres.orm.customer_favorite_product_orm import (  # noqa: E402
    CustomerFavoriteProductORM,
)
