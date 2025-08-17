from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.entity.product import Product
from app.__core__.domain.repository.pagination import PaginationInput
from app.__core__.domain.value_object.customer_favorite_product import \
    CustomerFavoriteProduct

T = TypeVar("T")


class IBaseRepository(Generic[T], ABC):
    @abstractmethod
    async def insert_one(self, entity: T) -> None: ...

    @abstractmethod
    async def fetch_one(self, id: str) -> Optional[T]: ...


class ICustomerRepository(IBaseRepository[Customer]):
    @abstractmethod
    async def fetch_one_by_email(self, email: str) -> Optional[Customer]: ...

    @abstractmethod
    async def fetch_many(self, pagination: PaginationInput) -> List[T]: ...

    @abstractmethod
    async def count_all(self) -> int: ...

    @abstractmethod
    async def update_one(self, entity: Customer) -> None: ...

    @abstractmethod
    async def delete_one(self, id: str) -> None: ...


class IProductCacheRepository(IBaseRepository[Product]):
    @abstractmethod
    async def fetch_many(self, ids: List[int]) -> List[Product]: ...

    @abstractmethod
    async def refresh(self, entity: Product) -> None: ...


class ICustomerFavoriteProductRepository(IBaseRepository[CustomerFavoriteProduct]):
    @abstractmethod
    async def fetch_one(
        self, customer_id: str, product_id: int
    ) -> Optional[CustomerFavoriteProduct]: ...

    @abstractmethod
    async def fetch_many(
        self, customer_id: str, pagination: PaginationInput
    ) -> List[CustomerFavoriteProduct]: ...

    @abstractmethod
    async def count_all(self, customer_id: str) -> int: ...

    @abstractmethod
    async def delete_one(self, customer_id: str, product_id: int) -> None: ...
