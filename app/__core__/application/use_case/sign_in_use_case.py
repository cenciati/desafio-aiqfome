from abc import abstractmethod

from app.__core__.application.gateways.jwt_service import IJWTService
from app.__core__.domain.exception.exception import AuthenticationError
from app.__core__.domain.repository.repository import ICustomerRepository
from app.__core__.domain.strict_record import strict_record


@strict_record
class SignInInput:
    email: str
    password: str


@strict_record
class SignInOutput:
    access_token: str


class ISignInUseCase:
    @abstractmethod
    async def execute(self, input_dto: SignInInput) -> SignInOutput: ...


class SignInUseCase(ISignInUseCase):
    def __init__(
        self, customer_repository: ICustomerRepository, jwt_service: IJWTService
    ):
        self.customer_repository = customer_repository
        self.jwt_service = jwt_service

    async def execute(self, input_dto: SignInInput) -> SignInOutput:
        customer = await self.customer_repository.fetch_one_by_email(input_dto.email)

        if customer is None or not customer.password.verify(input_dto.password):
            # Mensagem genérica para mascarar o erro real do sign in
            raise AuthenticationError("invalid_credentials")

        access_token = self.jwt_service.create_token(customer.str_id)
        return SignInOutput(access_token=access_token)
