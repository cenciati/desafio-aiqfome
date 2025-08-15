from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Callable, Optional

from fastapi import Cookie, Depends, HTTPException
from fastapi.param_functions import Security
from fastapi.security import APIKeyHeader

from app.__core__.application.settings import get_settings
from app.__core__.domain.entity.user import User
from app.__core__.domain.repository.repository import IUserRepository
from app.infra.dependency import get_jwt_service, get_user_repository

if TYPE_CHECKING:
    from app.__core__.application.gateways.jwt_service import IJWTService
    from app.__core__.domain.value_object.permission import Permission


settings = get_settings()

api_key_header = APIKeyHeader(name="x-aiqfome-api-key", auto_error=False)


def validate_api_key(api_key: Optional[str] = Security(api_key_header)) -> None:
    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="missing_api_key",
        )

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="invalid_api_key",
        )


async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None,
    jwt_service: IJWTService = Depends(get_jwt_service),
    user_repository: IUserRepository = Depends(get_user_repository),
) -> User:
    if access_token is None:
        raise HTTPException(status_code=401, detail="missing_token")

    token = jwt_service.verify_token(access_token)
    user_id = token["sub"]

    user = await user_repository.fetch_one(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid_token")

    return user


def require_permission(required_permission: Permission) -> Callable[[User], User]:
    def wrapper(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(required_permission):
            raise HTTPException(status_code=403, detail="permission_denied")
        return current_user

    return wrapper
