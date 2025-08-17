from abc import ABC, abstractmethod

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
    created_at: str
    updated_at: str


class IFetchCustomerUseCase(ABC):
    @abstractmethod
    async def execute(self, input_dto: FetchCustomerInput) -> FetchCustomerOutput: ...


class FetchCustomerUseCase(IFetchCustomerUseCase):
    def __init__(
        self,
        customer_repository: ICustomerRepository,
    ):
        self.customer_repository = customer_repository

    async def execute(self, input_dto: FetchCustomerInput) -> FetchCustomerOutput:
        customer = await self.customer_repository.fetch_one(input_dto.customer_id)
        if not customer:
            raise ValidationError("customer_not_found")

        return FetchCustomerOutput(
            id=customer.str_id,
            name=customer.name,
            email=customer.email,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
