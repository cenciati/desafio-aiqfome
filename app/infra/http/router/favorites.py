from fastapi import APIRouter, Depends, HTTPException, Query

from app.__core__.application.logger import logger
from app.__core__.application.settings import get_settings
from app.__core__.application.use_case.favorite_product_use_case import (
    FavoriteProductInput,
    IFavoriteProductUseCase,
)
from app.__core__.application.use_case.list_customer_favorite_products_use_case import (
    IListCustomerFavoriteProductsUseCase,
    ListCustomerFavoriteProductsInput,
    ListCustomerFavoriteProductsOutput,
)
from app.__core__.application.use_case.unfavorite_product_use_case import (
    IUnfavoriteProductUseCase,
    UnfavoriteProductInput,
)
from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.exception.exception import ValidationError
from app.infra.dependency import (
    get_favorite_product_use_case,
    get_list_customer_favorite_products_use_case,
    get_unfavorite_product_use_case,
)
from app.infra.security import get_current_customer_by_token


router = APIRouter()
settings = get_settings()


@router.post("/{product_id}", status_code=201)
async def favorite_product(
    customer_id: str,
    product_id: int,
    customer: Customer = Depends(get_current_customer_by_token),
    favorite_product_use_case: IFavoriteProductUseCase = Depends(
        get_favorite_product_use_case
    ),
):
    if customer_id != customer.str_id:
        raise HTTPException(status_code=403, detail="forbidden")

    try:
        input_dto = FavoriteProductInput(product_id=product_id, customer_id=customer_id)
        await favorite_product_use_case.execute(input_dto)

    except ValidationError as exc:
        match str(exc):
            case "product_not_found":
                raise HTTPException(status_code=404, detail=str(exc))
            case "product_already_in_favorites":
                raise HTTPException(status_code=409, detail=str(exc))
            case _:
                raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("favorite_product_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.get("", response_model=ListCustomerFavoriteProductsOutput, status_code=200)
async def list_customer_favorite_products(
    customer_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=settings.PAGINATION_PER_PAGE_LIMIT),
    customer: Customer = Depends(get_current_customer_by_token),
    list_customer_favorite_products_use_case: IListCustomerFavoriteProductsUseCase = Depends(
        get_list_customer_favorite_products_use_case
    ),
):
    if customer_id != customer.str_id:
        raise HTTPException(status_code=403, detail="forbidden")

    try:
        input_dto = ListCustomerFavoriteProductsInput(
            customer_id=customer_id, page=page, per_page=per_page
        )
        return await list_customer_favorite_products_use_case.execute(input_dto)

    except Exception as exc:
        logger.error("list_customer_favorite_products_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)


@router.delete("/{product_id}", status_code=204)
async def unfavorite_product(
    customer_id: str,
    product_id: int,
    customer: Customer = Depends(get_current_customer_by_token),
    unfavorite_product_use_case: IUnfavoriteProductUseCase = Depends(
        get_unfavorite_product_use_case
    ),
):
    if customer_id != customer.str_id:
        raise HTTPException(status_code=403, detail="forbidden")

    try:
        input_dto = UnfavoriteProductInput(
            product_id=product_id, customer_id=customer_id
        )
        await unfavorite_product_use_case.execute(input_dto)

    except ValidationError as exc:
        match str(exc):
            case "product_not_in_favorites":
                raise HTTPException(status_code=422, detail=str(exc))
            case _:
                raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.error("unfavorite_product_failed", exc_info=str(exc))
        raise HTTPException(status_code=500)
