from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Optional

from fastapi import Cookie, Depends, HTTPException
from fastapi.param_functions import Security
from fastapi.security import APIKeyHeader

from app.__core__.application.settings import get_settings
from app.__core__.domain.entity.customer import Customer
from app.infra.dependency import get_customer_repository, get_jwt_service

if TYPE_CHECKING:
    from app.__core__.application.gateways.jwt_service import IJWTService
    from app.__core__.domain.repository.repository import ICustomerRepository


settings = get_settings()

api_key_header = APIKeyHeader(name="x-aiqfome-api-key", auto_error=False)


def require_api_key(api_key: Optional[str] = Security(api_key_header)) -> None:
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


async def get_current_customer_by_token(
    access_token: Annotated[Optional[str], Cookie()] = None,
    jwt_service: IJWTService = Depends(get_jwt_service),
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
) -> Customer:
    if access_token is None:
        raise HTTPException(status_code=401, detail="missing_token")

    token = jwt_service.verify_token(access_token)
    customer_id = token["sub"]

    customer = await customer_repository.fetch_one(customer_id)
    if customer is None:
        raise HTTPException(status_code=401, detail="invalid_token")

    return customer
