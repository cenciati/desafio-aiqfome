from abc import abstractmethod
import asyncio
from dataclasses import dataclass
from math import ceil
from typing import List

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.domain.entity.product import Product
from app.__core__.domain.repository.pagination import PaginationInput, PaginationOutput
from app.__core__.domain.repository.repository import (
    ICustomerFavoriteProductRepository,
)
from app.__core__.domain.strict_record import strict_record
from app.__core__.domain.value_object.customer_favorite_product import (
    CustomerFavoriteProduct,
)


@strict_record
class ListCustomerFavoriteProductsInput:
    customer_id: str
    page: int
    per_page: int


@strict_record
class ListCustomerFavoriteProductsOutput:
    data: List[Product]
    pagination: PaginationOutput


class IListCustomerFavoriteProductsUseCase:
    @abstractmethod
    async def execute(
        self, input_dto: ListCustomerFavoriteProductsInput
    ) -> ListCustomerFavoriteProductsOutput: ...


class ListCustomerFavoriteProductsUseCase(IListCustomerFavoriteProductsUseCase):
    def __init__(
        self,
        customer_favorite_product_repository: ICustomerFavoriteProductRepository,
        product_catalog: IProductCatalog,
    ):
        self.customer_favorite_product_repository = customer_favorite_product_repository
        self.product_catalog = product_catalog

    async def execute(
        self, input_dto: ListCustomerFavoriteProductsInput
    ) -> ListCustomerFavoriteProductsOutput:
        pagination = PaginationInput(page=input_dto.page, per_page=input_dto.per_page)
        async with asyncio.TaskGroup() as tg:
            list_customer_favorite_products_task = tg.create_task(
                self.customer_favorite_product_repository.fetch_many(pagination)
            )
            total_items_task = tg.create_task(
                self.customer_favorite_product_repository.count_all()
            )

        customer_favorite_products: List[CustomerFavoriteProduct] = (
            list_customer_favorite_products_task.result()
        )
        total_items = total_items_task.result()

        data = [
            await self._map_customer_favorite_product_to_output(
                customer_favorite_product
            )
            for customer_favorite_product in customer_favorite_products
        ]
        pagination = self._map_pagination_to_output(pagination, total_items)

        return ListCustomerFavoriteProductsOutput(data=data, pagination=pagination)

    async def _map_customer_favorite_product_to_output(
        self, customer_favorite_product: CustomerFavoriteProduct
    ) -> Product:
        product = await self.product_catalog.fetch_one(
            customer_favorite_product.product_id
        )
        return product

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
