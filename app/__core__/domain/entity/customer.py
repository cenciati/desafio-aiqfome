from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID

from app.__core__.domain.entity.base_domain_object import BaseDomainObject
from app.__core__.domain.exception.exception import ValidationError
from app.infra.postgres.orm.customer_orm import CustomerORM

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateCustomerProps:
    name: str
    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Customer(BaseDomainObject):
    name: str = field(compare=False)
    email: str = field(compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    updated_at: datetime = field(default_factory=datetime.now, compare=False)

    def __post_init__(self):
        if not EMAIL_REGEX.match(self.email):
            raise ValidationError("invalid_email")

    @classmethod
    def create(cls, props: CreateCustomerProps) -> Self:
        return cls(
            name=props.name,
            email=props.email.lower(),
        )

    @classmethod
    def to_domain(cls, raw_customer: dict) -> Customer:
        return cls(
            id=UUID(raw_customer["id"]),
            name=raw_customer["name"],
            email=raw_customer["email"],
            created_at=raw_customer["created_at"],
            updated_at=raw_customer["updated_at"],
        )

    def to_orm(self) -> CustomerORM:
        return CustomerORM(
            id=self.id,
            name=self.name,
            email=self.email,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
