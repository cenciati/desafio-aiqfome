from fastapi import APIRouter, Depends, HTTPException

from app.__core__.application.logger import logger
from app.__core__.application.settings import get_settings
from app.__core__.application.use_case.delete_customer_use_case import (
    DeleteCustomerInput,
    IDeleteCustomerUseCase,
)
from app.__core__.application.use_case.fetch_customer_use_case import (
    FetchCustomerInput,
    FetchCustomerOutput,
    IFetchCustomerUseCase,
)
from app.__core__.application.use_case.list_customers_use_case import (
    IListCustomersUseCase,
    ListCustomersInput,
    ListCustomersOutput,
)
from app.__core__.application.use_case.update_customer_use_case import (
    IUpdateCustomerUseCase,
    UpdateCustomerInput,
    UpdateCustomerRequestInput,
)
from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.exception.exception import ValidationError
from app.infra.dependency import (
    get_delete_customer_use_case,
    get_fetch_customer_use_case,
    get_list_customers_use_case,
    get_update_customer_use_case,
)
from app.infra.security import get_current_customer_by_token, require_api_key

router = APIRouter()
settings = get_settings()


@router.get("", response_model=ListCustomersOutput, status_code=200)
async def list_customers(
    page: int = 1,
    per_page: int = 20,
    _=Depends(require_api_key),
    list_customers_use_case: IListCustomersUseCase = Depends(
        get_list_customers_use_case
    ),
):
    if per_page > settings.PAGINATION_PER_PAGE_LIMIT:
        raise HTTPException(status_code=422, detail="per_page_limit_exceeded")

    try:
        input_dto = ListCustomersInput(page=page, per_page=per_page)
        return await list_customers_use_case.execute(input_dto)

    except Exception as exc:
        logger.error("list_customers_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.get("/{customer_id}", response_model=FetchCustomerOutput, status_code=200)
async def fetch_customer(
    customer_id: str,
    customer: Customer = Depends(get_current_customer_by_token),
    fetch_customer_use_case: IFetchCustomerUseCase = Depends(
        get_fetch_customer_use_case
    ),
):
    if customer_id != customer.str_id:
        raise HTTPException(status_code=403, detail="forbidden")

    try:
        input_dto = FetchCustomerInput(customer_id=customer_id)
        return await fetch_customer_use_case.execute(input_dto)

    except ValidationError as exc:
        match str(exc):
            case "customer_not_found":
                raise HTTPException(status_code=404, detail=str(exc))
            case _:
                raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("fetch_customer_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.patch("/{customer_id}", status_code=204)
async def update_customer(
    customer_id: str,
    request: UpdateCustomerRequestInput,
    customer: Customer = Depends(get_current_customer_by_token),
    update_customer_use_case: IUpdateCustomerUseCase = Depends(
        get_update_customer_use_case
    ),
):
    if customer_id != customer.str_id:
        raise HTTPException(status_code=403, detail="forbidden")

    try:
        input_dto = UpdateCustomerInput(
            customer_id=customer_id,
            name=request.name,
            email=request.email,
        )
        await update_customer_use_case.execute(input_dto)

    except ValidationError as exc:
        match str(exc):
            case "customer_not_found":
                raise HTTPException(status_code=404, detail=str(exc))
            case _:
                raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("update_customer_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: str,
    customer: Customer = Depends(get_current_customer_by_token),
    delete_customer_use_case: IDeleteCustomerUseCase = Depends(
        get_delete_customer_use_case
    ),
):
    if customer_id != customer.str_id:
        raise HTTPException(status_code=403, detail="forbidden")

    try:
        input_dto = DeleteCustomerInput(customer_id=customer_id)
        await delete_customer_use_case.execute(input_dto)
        logger.info("customer_deleted", extra={"customer_id": customer_id})

    except ValidationError as exc:
        match str(exc):
            case _:
                raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("delete_customer_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)
