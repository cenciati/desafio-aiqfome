from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.entity.product import Product
from app.__core__.domain.entity.user import User
from app.__core__.domain.repository.pagination import Pagination

T = TypeVar("T")


class IBaseRepository(Generic[T], ABC):
    @abstractmethod
    async def insert_one(self, entity: T) -> None: ...

    @abstractmethod
    async def fetch_one_by_id(self, id: str) -> Optional[T]: ...

    @abstractmethod
    def update_one(self, entity: T) -> None: ...

    @abstractmethod
    def delete_one(self, entity: T) -> None: ...


class IUserRepository(IBaseRepository[User]):
    @abstractmethod
    async def fetch_one_by_slug(self, slug: str) -> Optional[User]: ...


class ICustomerRepository(IBaseRepository[Customer]):
    @abstractmethod
    def fetch_many(
        self, pagination: Pagination, filters: Optional[Dict[str, Any]]
    ) -> List[Customer]: ...


class IProductRepository(IBaseRepository[Product]): ...
