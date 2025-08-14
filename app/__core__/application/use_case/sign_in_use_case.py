from abc import abstractmethod
from dataclasses import dataclass

from app.__core__.application.gateways.jwt_service import IJWTService
from app.__core__.domain.exception.exception import AuthenticationError
from app.__core__.domain.repository.repository import IUserRepository


@dataclass(slots=True, frozen=True, kw_only=True)
class SignInInput:
    username: str
    password: str


@dataclass(slots=True, frozen=True, kw_only=True)
class SignInOutput:
    access_token: str


class ISignInUseCase:
    @abstractmethod
    async def execute(self, input_dto: SignInInput) -> SignInOutput:
        pass


class SignInUseCase(ISignInUseCase):
    def __init__(self, user_repository: IUserRepository, jwt_service: IJWTService):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    async def execute(self, input_dto: SignInInput) -> SignInOutput:
        user = await self.user_repository.fetch_one_by_slug(input_dto.username)
        if user is None or not user.password.verify(input_dto.password):
            # Mensagem genérica para mascarar o erro real do sign in
            raise AuthenticationError("invalid_credentials")

        access_token = self.jwt_service.create_token(user.str_id)
        output_dto = SignInOutput(access_token=access_token)
        return output_dto
