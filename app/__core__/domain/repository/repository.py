from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.entity.product import Product
from app.__core__.domain.entity.user import User
from app.__core__.domain.repository.pagination import PaginationInput

T = TypeVar("T")


class IBaseRepository(Generic[T], ABC):
    @abstractmethod
    async def insert_one(self, entity: T) -> None: ...

    @abstractmethod
    async def fetch_one(self, id: str) -> Optional[T]: ...


class IUserRepository(IBaseRepository[User]):
    @abstractmethod
    async def fetch_one_by_slug(self, slug: str) -> Optional[User]: ...


class ICustomerRepository(IBaseRepository[Customer]):
    @abstractmethod
    async def fetch_one_by_email(self, email: str) -> Optional[Customer]: ...

    @abstractmethod
    async def fetch_many(self, pagination: PaginationInput) -> List[Customer]: ...

    @abstractmethod
    async def count_all(self) -> int: ...

    @abstractmethod
    async def update_one(self, entity: Customer) -> None: ...

    @abstractmethod
    async def delete_one(self, id: str) -> None: ...


class IProductRepository(IBaseRepository[Product]): ...
