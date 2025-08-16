from abc import abstractmethod
from typing import List

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.domain.entity.product import Product
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import ICustomerRepository
from app.__core__.domain.strict_record import strict_record


@strict_record
class FetchCustomerInput:
    customer_id: str


@strict_record
class FetchCustomerOutput:
    id: str
    name: str
    email: str
    favorite_products: List[Product]
    created_at: str
    updated_at: str


class IFetchCustomerUseCase:
    @abstractmethod
    async def execute(self, input_dto: FetchCustomerInput) -> FetchCustomerOutput: ...


class FetchCustomerUseCase(IFetchCustomerUseCase):
    def __init__(
        self,
        customer_repository: ICustomerRepository,
        product_catalog: IProductCatalog,
    ):
        self.customer_repository = customer_repository
        self.product_catalog = product_catalog

    async def execute(self, input_dto: FetchCustomerInput) -> FetchCustomerOutput:
        customer = await self.customer_repository.fetch_one(input_dto.customer_id)
        if not customer:
            raise ValidationError("customer_not_found")

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
