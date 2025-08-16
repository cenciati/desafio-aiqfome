from abc import abstractmethod

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import (
    ICustomerFavoriteProductRepository,
)
from app.__core__.domain.strict_record import strict_record
from app.__core__.domain.value_object.customer_favorite_product import (
    CustomerFavoriteProduct,
)


@strict_record
class FavoriteProductInput:
    customer_id: str
    product_id: int


class IFavoriteProductUseCase:
    @abstractmethod
    async def execute(self, input_dto: FavoriteProductInput) -> None: ...


class FavoriteProductUseCase(IFavoriteProductUseCase):
    def __init__(
        self,
        customer_favorite_product_repository: ICustomerFavoriteProductRepository,
        product_catalog: IProductCatalog,
    ):
        self.customer_favorite_product_repository = customer_favorite_product_repository
        self.product_catalog = product_catalog

    async def execute(self, input_dto: FavoriteProductInput) -> None:
        product = await self.product_catalog.fetch_one(input_dto.product_id)
        if not product:
            raise ValidationError("product_not_found")

        customer_favorite_product = (
            await self.customer_favorite_product_repository.fetch_one(
                input_dto.customer_id, input_dto.product_id
            )
        )
        if customer_favorite_product:
            raise ValidationError("product_already_in_favorites")

        customer_favorite_product = CustomerFavoriteProduct.create(input_dto)
        await self.customer_favorite_product_repository.insert_one(
            customer_favorite_product
        )
