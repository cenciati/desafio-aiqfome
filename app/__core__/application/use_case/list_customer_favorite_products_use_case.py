import asyncio
from abc import ABC, abstractmethod
from datetime import timedelta
from math import ceil
from typing import List, Optional

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.application.task_manager import TaskManager
from app.__core__.application.use_case.base_product_cache_use_case import \
    BaseProductCacheUseCase
from app.__core__.domain.entity.product import Product, Review
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.pagination import (PaginationInput,
                                                       PaginationOutput)
from app.__core__.domain.repository.repository import (
    ICustomerFavoriteProductRepository, IProductCacheRepository)
from app.__core__.domain.strict_record import strict_record
from app.__core__.domain.value_object.customer_favorite_product import \
    CustomerFavoriteProduct


@strict_record
class ListCustomerFavoriteProductsInput:
    customer_id: str
    page: int
    per_page: int


@strict_record
class ProductOutput:
    id: int
    title: str
    image_url: str
    price: float
    review: Optional[Review]


@strict_record
class ListCustomerFavoriteProductsOutput:
    data: List[ProductOutput]
    pagination: PaginationOutput


class IListCustomerFavoriteProductsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, input_dto: ListCustomerFavoriteProductsInput
    ) -> ListCustomerFavoriteProductsOutput: ...


class ListCustomerFavoriteProductsUseCase(
    BaseProductCacheUseCase, IListCustomerFavoriteProductsUseCase
):
    def __init__(
        self,
        customer_favorite_product_repository: ICustomerFavoriteProductRepository,
        product_cache_repository: IProductCacheRepository,
        product_catalog: IProductCatalog,
        task_manager: TaskManager,
    ):
        super().__init__(product_cache_repository, product_catalog)
        self.customer_favorite_product_repository = customer_favorite_product_repository
        self.task_manager = task_manager

    async def execute(
        self, input_dto: ListCustomerFavoriteProductsInput
    ) -> ListCustomerFavoriteProductsOutput:
        pagination = PaginationInput(page=input_dto.page, per_page=input_dto.per_page)

        async with asyncio.TaskGroup() as tg:
            list_customer_favorite_products_task = tg.create_task(
                self.customer_favorite_product_repository.fetch_many(
                    input_dto.customer_id, pagination
                )
            )
            total_items_task = tg.create_task(
                self.customer_favorite_product_repository.count_all(
                    input_dto.customer_id
                )
            )

        customer_favorite_products = list_customer_favorite_products_task.result()
        total_items = total_items_task.result()

        data = await self._hydrate_products(customer_favorite_products)
        pagination = self._map_pagination_to_output(pagination, total_items)

        return ListCustomerFavoriteProductsOutput(data=data, pagination=pagination)

    async def _hydrate_products(
        self, customer_favorite_products: List[CustomerFavoriteProduct]
    ) -> List[Product]:
        product_ids = [cfp.product_id for cfp in customer_favorite_products]
        cached_products = await self.product_cache_repository.fetch_many(product_ids)
        cached_by_id = {p.id: p for p in cached_products}

        output_data: List[Optional[Product]] = [None] * len(customer_favorite_products)
        tasks: List[asyncio.Task] = []

        # o índice é importante para manter a ordem dos produtos no output_data,
        # ou seja, cada produto favoritad tem um tratamento diferente
        for idx, cfp in enumerate(customer_favorite_products):
            product_id = cfp.product_id
            cached = cached_by_id.get(product_id)

            if cached:
                age = self._get_cache_age(cached)

                if self._is_cache_fresh(age):
                    output_data[idx] = cached

                elif not self._is_cache_stale(age):
                    output_data[idx] = cached
                    self.task_manager.create(  # disparo em background do refresh
                        self._refresh_cache(product_id),
                        name=f"refresh_cache_for_product_{product_id}",
                    )

                else:
                    tasks.append(
                        asyncio.create_task(
                            self._fetch_and_refresh_with_index(
                                product_id, idx, output_data
                            )
                        )
                    )

            else:
                tasks.append(
                    asyncio.create_task(
                        self._fetch_and_insert_with_index(product_id, idx, output_data)
                    )
                )

        if len(tasks) > 0:
            await asyncio.gather(*tasks)

        return [value for value in output_data if value is not None]

    def _is_cache_stale(self, age: timedelta) -> bool:
        return age > self.hard_ttl

    async def _fetch_and_insert_with_index(
        self, product_id: int, idx: int, output_data: List[Optional[Product]]
    ):
        product = await self._fetch_and_insert(product_id)
        output_data[idx] = product

    async def _fetch_and_refresh_with_index(
        self, product_id: int, idx: int, output_data: List[Optional[Product]]
    ):
        async with self._catalog_semaphore:
            product = await self.product_catalog.fetch_one(product_id)

        if product is None:
            raise ValidationError("product_not_found")

        await self.product_cache_repository.refresh(product)
        output_data[idx] = product

    def _map_pagination_to_output(
        self, pagination: PaginationInput, total_items: int
    ) -> PaginationOutput:
        total_pages = ceil(total_items / pagination.per_page) if total_items > 0 else 0
        return PaginationOutput(
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages=total_pages,
            total_items=total_items,
        )
