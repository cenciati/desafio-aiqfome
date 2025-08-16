from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.infra.postgres.orm.customer_favorite_product_orm import (
    CustomerFavoriteProductORM,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCustomerFavoriteProductProps:
    customer_id: str
    product_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CustomerFavoriteProduct:
    customer_id: UUID = field(compare=True)
    product_id: int = field(compare=True)
    favorited_at: datetime = field(default_factory=datetime.now, compare=False)

    @classmethod
    def create(
        cls, props: CreateCustomerFavoriteProductProps
    ) -> "CustomerFavoriteProduct":
        return cls(
            customer_id=UUID(props.customer_id),
            product_id=props.product_id,
        )

    @classmethod
    def to_domain(
        cls, raw_customer_favorite_product: CustomerFavoriteProductORM
    ) -> "CustomerFavoriteProduct":  # noqa: F821
        return cls(
            customer_id=raw_customer_favorite_product.customer_id,
            product_id=raw_customer_favorite_product.product_id,
            favorited_at=raw_customer_favorite_product.favorited_at,
        )

    def to_orm(self) -> CustomerFavoriteProductORM:
        return CustomerFavoriteProductORM(
            customer_id=self.customer_id,
            product_id=self.product_id,
            favorited_at=self.favorited_at,
        )
