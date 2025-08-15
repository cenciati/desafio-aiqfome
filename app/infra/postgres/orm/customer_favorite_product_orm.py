from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


class CustomerFavoriteProductORM(SQLModel, table=True):
    __tablename__ = "customer_favorite_products"

    customer_id: UUID = Field(foreign_key="customers.id", primary_key=True)
    product_id: UUID = Field(primary_key=True)
    favorited_at: datetime

    customer: Mapped[Optional["CustomerORM"]] = Relationship(
        back_populates="favorite_products"
    )


from app.infra.postgres.orm.customer_orm import CustomerORM  # noqa: E402
