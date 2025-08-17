from abc import ABC, abstractmethod

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import ICustomerRepository
from app.__core__.domain.strict_record import strict_record


@strict_record
class SignUpInput:
    name: str
    email: str
    password: str


@strict_record
class SignUpOutput:
    id: str


class ISignUpUseCase(ABC):
    @abstractmethod
    async def execute(self, input_dto: SignUpInput) -> SignUpOutput: ...


class SignUpUseCase(ISignUpUseCase):
    def __init__(self, customer_repository: ICustomerRepository):
        self.customer_repository = customer_repository

    async def execute(self, input_dto: SignUpInput) -> SignUpOutput:
        # Criando a entidade primeiro, pois se os dados forem inválidos,
        # nem chegamos a estressar o banco
        customer = Customer.create(input_dto)

        if await self.customer_repository.fetch_one_by_email(customer.email):
            raise ValidationError("email_already_exists")

        await self.customer_repository.insert_one(customer)

        return SignUpOutput(id=customer.str_id)
