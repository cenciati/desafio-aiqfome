from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.__core__.application.gateways.jwt_service import IJWTService
from app.__core__.application.use_case.sign_in_use_case import SignInUseCase
from app.__core__.application.use_case.sign_up_use_case import SignUpUseCase
from app.__core__.domain.repository.repository import IUserRepository
from app.infra.jwt.jwt_service import JWTService
from app.infra.postgres.database import AsyncSessionFactory
from app.infra.postgres.repository.user_repository import PostgresUserRepository

if TYPE_CHECKING:
    from app.__core__.application.use_case.sign_in_use_case import ISignInUseCase
    from app.__core__.application.use_case.sign_up_use_case import ISignUpUseCase


def get_jwt_service() -> IJWTService:
    return JWTService()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session


def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return PostgresUserRepository(session)


def get_sign_in_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    jwt_service: IJWTService = Depends(get_jwt_service),
) -> ISignInUseCase:
    return SignInUseCase(user_repository, jwt_service)


def get_sign_up_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> ISignUpUseCase:
    return SignUpUseCase(user_repository)
