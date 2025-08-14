from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.__core__.domain.entity.base_domain_object import BaseDomainObject
from app.__core__.domain.exception.exception import ValidationError


@dataclass(frozen=True, slots=True, kw_only=True)
class Review:
    rate: float
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateProductProps:
    title: str
    image_url: str
    price: Decimal
    review: Optional[Review] = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Product(BaseDomainObject):
    title: str = field(compare=False)
    image_url: str = field(compare=False)
    price: Decimal = field(compare=False)
    review: Review = field(compare=False)

    def __post_init__(self):
        if not isinstance(self.title, str):
            raise ValidationError("invalid_title_data_type")
        if not isinstance(self.image_url, str):
            raise ValidationError("invalid_image_url_data_type")
        if not isinstance(self.price, Decimal):
            raise ValidationError("invalid_pric_data_typee")
        if self.review is not None and not isinstance(self.review, Review):
            raise ValidationError("invalid_review_data_type")

    @classmethod
    def to_domain(cls, raw_product: dict) -> Product:
        return cls(
            id=UUID(raw_product["id"]),
            title=raw_product["title"],
            image_url=raw_product["image_url"],
            price=Decimal(raw_product["price"]),
            review=Review(
                rate=float(raw_product["rating"]["rate"]),
                count=int(raw_product["rating"]["count"]),
            ),
        )
