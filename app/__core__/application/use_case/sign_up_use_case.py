from abc import abstractmethod
from dataclasses import dataclass
from typing import List

from app.__core__.domain.entity.user import User
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import IUserRepository
from app.__core__.domain.value_object.password import Password
from app.__core__.domain.value_object.permission import Permission


@dataclass(slots=True, frozen=True, kw_only=True)
class SignUpInput:
    username: str
    password: str
    permissions: List[Permission]


@dataclass(slots=True, frozen=True, kw_only=True)
class SignUpOutput:
    id: str
    username: str


class ISignUpUseCase:
    @abstractmethod
    async def execute(self, input_dto: SignUpInput) -> SignUpOutput:
        pass


class SignUpUseCase(ISignUpUseCase):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, input_dto: SignUpInput) -> SignUpOutput:
        if await self.user_repository.fetch_one_by_slug(input_dto.username.lower()):
            raise ValidationError("username_already_exists")

        password = Password.create(input_dto.password)
        user = User(
            slug=input_dto.username,
            password=password,
            permissions=input_dto.permissions,
        )
        await self.user_repository.insert_one(user)

        return SignUpOutput(id=user.str_id, username=user.slug)
