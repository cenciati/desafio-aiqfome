from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from sqlmodel import ARRAY, Column, Enum, Field, SQLModel

from app.__core__.domain.value_object.permission import Permission


class UserORM(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True, index=True)
    slug: str = Field(unique=True, index=True)
    password_hash: str
    permissions: List[Permission] = Field(
        sa_column=Column(
            ARRAY(
                Enum(
                    Permission,
                    values_callable=lambda obj: [e.value for e in obj],
                    name="permission",
                )
            )
        )
    )
    created_at: datetime
    updated_at: datetime
