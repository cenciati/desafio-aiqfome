from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.__core__.domain.exception.exception import ValidationError
from app.infra.postgres.orm.product_cache_orm import ProductCacheORM


@dataclass(frozen=True, slots=True, kw_only=True)
class Review:
    rate: float
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateProductProps:
    title: str
    image_url: str
    price: int | float
    review: Optional[Review] = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Product:
    id: int
    title: str = field(compare=False)
    image_url: str = field(compare=False)
    price: float = field(compare=False)
    review: Optional[Review] = field(compare=False)
    fetched_at: datetime = field(default_factory=datetime.now, compare=False)

    def __post_init__(self):
        if not isinstance(self.title, str):
            raise ValidationError("invalid_title_data_type")
        if not isinstance(self.image_url, str):
            raise ValidationError("invalid_image_url_data_type")
        if not isinstance(self.price, float):
            raise ValidationError("invalid_price_data_type")
        if self.review is not None and not isinstance(self.review, Review):
            raise ValidationError("invalid_review_data_type")

    @classmethod
    def to_domain(cls, raw_product: ProductCacheORM | dict) -> Product:
        if isinstance(raw_product, dict):
            return cls(
                id=raw_product["id"],
                title=raw_product["title"],
                image_url=raw_product["image"],
                price=float(raw_product["price"]),
                review=(
                    Review(
                        rate=float(raw_product["rating"]["rate"]),
                        count=int(raw_product["rating"]["count"]),
                    )
                    if raw_product["rating"]
                    else None
                ),
            )

        return cls(
            id=raw_product.id,
            title=raw_product.title,
            image_url=raw_product.image_url,
            price=float(raw_product.price),
            review=(
                Review(
                    rate=float(raw_product.review_rate),
                    count=int(raw_product.review_count),
                )
                if raw_product.review_rate
                else None
            ),
        )

    def to_orm(self) -> ProductCacheORM:
        return ProductCacheORM(
            id=self.id,
            title=self.title,
            image_url=self.image_url,
            price=self.price,
            review_rate=self.review.rate,
            review_count=self.review.count,
            fetched_at=self.fetched_at,
        )
