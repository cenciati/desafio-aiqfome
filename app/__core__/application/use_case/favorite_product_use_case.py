from abc import ABC, abstractmethod

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.application.use_case.base_product_cache_use_case import \
    BaseProductCacheUseCase
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import (
    ICustomerFavoriteProductRepository, IProductCacheRepository)
from app.__core__.domain.strict_record import strict_record
from app.__core__.domain.value_object.customer_favorite_product import \
    CustomerFavoriteProduct


@strict_record
class FavoriteProductInput:
    customer_id: str
    product_id: int


class IFavoriteProductUseCase(ABC):
    @abstractmethod
    async def execute(self, input_dto: FavoriteProductInput) -> None: ...


class FavoriteProductUseCase(BaseProductCacheUseCase, IFavoriteProductUseCase):
    def __init__(
        self,
        customer_favorite_product_repository: ICustomerFavoriteProductRepository,
        product_cache_repository: IProductCacheRepository,
        product_catalog: IProductCatalog,
    ):
        super().__init__(product_cache_repository, product_catalog)
        self.customer_favorite_product_repository = customer_favorite_product_repository

    async def execute(self, input_dto: FavoriteProductInput) -> None:
        existing_customer_favorite_product = (
            await self.customer_favorite_product_repository.fetch_one(
                input_dto.customer_id, input_dto.product_id
            )
        )
        if existing_customer_favorite_product:
            raise ValidationError("product_already_in_favorites")

        await self._hydrate_product(input_dto.product_id)

        customer_favorite_product = CustomerFavoriteProduct.create(input_dto)
        await self.customer_favorite_product_repository.insert_one(
            customer_favorite_product
        )

    async def _hydrate_product(self, product_id: int) -> None:
        cached = await self.product_cache_repository.fetch_one(product_id)

        if cached:
            age = self._get_cache_age(cached)

            if not self._is_cache_fresh(age):
                await self._refresh_cache(product_id)

        else:
            await self._fetch_and_insert(product_id)
