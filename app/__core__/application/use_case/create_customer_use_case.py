from abc import abstractmethod
from dataclasses import dataclass

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import (
    ICustomerRepository,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateCustomerInput:
    name: str
    email: str


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateCustomerOutput:
    id: str


class ICreateCustomerUseCase:
    @abstractmethod
    async def execute(self, input_dto: CreateCustomerInput) -> CreateCustomerOutput: ...


class CreateCustomerUseCase(ICreateCustomerUseCase):
    def __init__(self, customer_repository: ICustomerRepository):
        self.customer_repository = customer_repository

    async def execute(self, input_dto: CreateCustomerInput) -> CreateCustomerOutput:
        if await self.customer_repository.fetch_one_by_email(input_dto.email):
            raise ValidationError("email_already_exists")

        customer = Customer.create(input_dto)
        await self.customer_repository.insert_one(customer)
        return CreateCustomerOutput(id=customer.str_id)
