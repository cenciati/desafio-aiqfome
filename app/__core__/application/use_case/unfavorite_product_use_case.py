from abc import ABC, abstractmethod

from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import \
    ICustomerFavoriteProductRepository
from app.__core__.domain.strict_record import strict_record


@strict_record
class UnfavoriteProductInput:
    customer_id: str
    product_id: int


class IUnfavoriteProductUseCase(ABC):
    @abstractmethod
    async def execute(self, input_dto: UnfavoriteProductInput) -> None: ...


class UnfavoriteProductUseCase(IUnfavoriteProductUseCase):
    def __init__(
        self,
        customer_favorite_product_repository: ICustomerFavoriteProductRepository,
    ):
        self.customer_favorite_product_repository = customer_favorite_product_repository

    async def execute(self, input_dto: UnfavoriteProductInput) -> None:
        customer_favorite_product = (
            await self.customer_favorite_product_repository.fetch_one(
                input_dto.customer_id, input_dto.product_id
            )
        )
        if not customer_favorite_product:
            raise ValidationError("product_not_in_favorites")

        await self.customer_favorite_product_repository.delete_one(
            input_dto.customer_id, input_dto.product_id
        )
