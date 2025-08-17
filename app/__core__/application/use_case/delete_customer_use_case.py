from abc import ABC, abstractmethod

from app.__core__.domain.repository.repository import ICustomerRepository
from app.__core__.domain.strict_record import strict_record


@strict_record
class DeleteCustomerInput:
    customer_id: str


class IDeleteCustomerUseCase(ABC):
    @abstractmethod
    async def execute(self, input_dto: DeleteCustomerInput) -> None: ...


class DeleteCustomerUseCase(IDeleteCustomerUseCase):
    def __init__(self, customer_repository: ICustomerRepository):
        self.customer_repository = customer_repository

    async def execute(self, input_dto: DeleteCustomerInput) -> None:
        await self.customer_repository.delete_one(input_dto.customer_id)
