from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.__core__.domain.entity.customer import UpdateCustomerProps
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import ICustomerRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCustomerRequestInput:
    name: Optional[str] = None
    email: Optional[str] = None


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateCustomerInput:
    customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None


class IUpdateCustomerUseCase:
    @abstractmethod
    async def execute(self, input_dto: UpdateCustomerInput) -> None: ...


class UpdateCustomerUseCase(IUpdateCustomerUseCase):
    def __init__(self, customer_repository: ICustomerRepository):
        self.customer_repository = customer_repository

    async def execute(self, input_dto: UpdateCustomerInput) -> None:
        customer = await self.customer_repository.fetch_one(input_dto.customer_id)
        if not customer:
            raise ValidationError("customer_not_found")

        updated_customer = customer.update_info(
            UpdateCustomerProps(
                name=input_dto.name,
                email=input_dto.email,
            )
        )

        await self.customer_repository.update_one(updated_customer)
