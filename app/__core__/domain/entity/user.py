from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from app.__core__.domain.entity.base_domain_object import BaseDomainObject
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.value_object.password import Password
from app.__core__.domain.value_object.permission import Permission
from app.infra.postgres.orm.user_orm import UserORM


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserProps:
    username: str
    password: str
    permissions: List[Permission]


@dataclass(frozen=True, slots=True, kw_only=True)
class User(BaseDomainObject):
    slug: str = field(compare=True)
    password: Password = field(compare=False)
    permissions: List[Permission] = field(compare=False)
    created_at: datetime = field(compare=False, default_factory=datetime.now)
    updated_at: datetime = field(compare=False, default_factory=datetime.now)

    def __post_init__(self):
        if not isinstance(self.slug, str):
            raise ValidationError("invalid_slug_data_type")
        if not isinstance(self.password, Password):
            raise ValidationError("invalid_password_data_type")
        if not isinstance(self.permissions, List):
            raise ValidationError("invalid_permissions_data_type")

    @classmethod
    def create(cls, props: CreateUserProps) -> "User":
        return cls(
            slug=props.username,
            password=Password.create(props.password),
            permissions=props.permissions,
        )

    @classmethod
    def to_domain(cls, raw_user: UserORM) -> User:
        return cls(
            id=raw_user.id,
            slug=raw_user.slug,
            password=Password(hash=raw_user.password_hash),
            permissions=raw_user.permissions,
        )

    def to_orm(self) -> UserORM:
        return UserORM(
            id=self.id,
            slug=self.slug,
            password_hash=self.password.hash,
            permissions=self.permissions,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions
