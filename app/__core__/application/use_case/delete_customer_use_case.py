from abc import abstractmethod
from dataclasses import dataclass

from app.__core__.domain.repository.repository import ICustomerRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteCustomerInput:
    customer_id: str


class IDeleteCustomerUseCase:
    @abstractmethod
    async def execute(self, input_dto: DeleteCustomerInput) -> None: ...


class DeleteCustomerUseCase(IDeleteCustomerUseCase):
    def __init__(self, customer_repository: ICustomerRepository):
        self.customer_repository = customer_repository

    async def execute(self, input_dto: DeleteCustomerInput) -> None:
        await self.customer_repository.delete_one(input_dto.customer_id)
