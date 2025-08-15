import asyncio
from abc import abstractmethod
from dataclasses import dataclass
from math import ceil
from typing import List

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.application.use_case.fetch_customer_use_case import \
    FetchCustomerOutput
from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.repository.pagination import (PaginationInput,
                                                       PaginationOutput)
from app.__core__.domain.repository.repository import ICustomerRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class ListCustomersInput:
    page: int
    per_page: int


@dataclass(slots=True, frozen=True, kw_only=True)
class ListCustomersOutput:
    data: List[FetchCustomerOutput]
    pagination: PaginationOutput


class IListCustomersUseCase:
    @abstractmethod
    async def execute(self, input_dto: ListCustomersInput) -> ListCustomersOutput: ...


class ListCustomersUseCase(IListCustomersUseCase):
    def __init__(
        self,
        customer_repository: ICustomerRepository,
        product_catalog: IProductCatalog,
    ):
        self.customer_repository = customer_repository
        self.product_catalog = product_catalog

    async def execute(self, input_dto: ListCustomersInput) -> ListCustomersOutput:
        pagination = PaginationInput(page=input_dto.page, per_page=input_dto.per_page)
        async with asyncio.TaskGroup() as tg:
            list_customers_task = tg.create_task(
                self.customer_repository.fetch_many(pagination)
            )
            total_items_task = tg.create_task(self.customer_repository.count_all())

        customers: List[Customer] = list_customers_task.result()
        total_items = total_items_task.result()

        data = [await self._map_customer_to_output(customer) for customer in customers]
        pagination = self._map_pagination_to_output(pagination, total_items)

        return ListCustomersOutput(data=data, pagination=pagination)

    async def _map_customer_to_output(self, customer: Customer) -> FetchCustomerOutput:
        favorite_products = await self.product_catalog.fetch_many(
            customer.favorite_products_ids
        )
        return FetchCustomerOutput(
            id=customer.str_id,
            name=customer.name,
            email=customer.email,
            favorite_products=favorite_products,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )

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
