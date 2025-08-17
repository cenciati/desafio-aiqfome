from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator, Optional

from fastapi import Depends, Request
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.__core__.application.settings import get_settings
from app.__core__.application.task_manager import TaskManager
from app.__core__.application.use_case.delete_customer_use_case import \
    DeleteCustomerUseCase
from app.__core__.application.use_case.favorite_product_use_case import \
    FavoriteProductUseCase
from app.__core__.application.use_case.fetch_customer_use_case import \
    FetchCustomerUseCase
from app.__core__.application.use_case.list_customer_favorite_products_use_case import \
    ListCustomerFavoriteProductsUseCase
from app.__core__.application.use_case.list_customers_use_case import \
    ListCustomersUseCase
from app.__core__.application.use_case.sign_in_use_case import SignInUseCase
from app.__core__.application.use_case.sign_up_use_case import SignUpUseCase
from app.__core__.application.use_case.unfavorite_product_use_case import \
    UnfavoriteProductUseCase
from app.__core__.application.use_case.update_customer_use_case import \
    UpdateCustomerUseCase
from app.infra.fakestore.fakestore_product_catalog import \
    FakeStoreProductCatalog
from app.infra.jwt.jwt_service import JWTService
from app.infra.postgres.database import AsyncSessionFactory
from app.infra.postgres.repository.customer_favorite_product_repository import \
    PostgresCustomerFavoriteProductRepository
from app.infra.postgres.repository.customer_repository import \
    PostgresCustomerRepository
from app.infra.postgres.repository.product_cache_repository import \
    PostgresProductCacheRepository

if TYPE_CHECKING:
    from app.__core__.application.gateways.jwt_service import IJWTService
    from app.__core__.application.gateways.product_catalog import \
        IProductCatalog
    from app.__core__.application.use_case.delete_customer_use_case import \
        IDeleteCustomerUseCase
    from app.__core__.application.use_case.favorite_product_use_case import \
        IFavoriteProductUseCase
    from app.__core__.application.use_case.fetch_customer_use_case import \
        IFetchCustomerUseCase
    from app.__core__.application.use_case.list_customer_favorite_products_use_case import \
        IListCustomerFavoriteProductsUseCase
    from app.__core__.application.use_case.list_customers_use_case import \
        IListCustomersUseCase
    from app.__core__.application.use_case.sign_in_use_case import \
        ISignInUseCase
    from app.__core__.application.use_case.sign_up_use_case import \
        ISignUpUseCase
    from app.__core__.application.use_case.unfavorite_product_use_case import \
        IUnfavoriteProductUseCase
    from app.__core__.application.use_case.update_customer_use_case import \
        IUpdateCustomerUseCase
    from app.__core__.domain.repository.repository import (
        ICustomerFavoriteProductRepository, ICustomerRepository,
        IProductCacheRepository)


settings = get_settings()
client: Optional[AsyncClient] = None


def get_httpx_client() -> AsyncClient:
    global client
    if client is None:
        client = AsyncClient(
            base_url=settings.PRODUCT_CATALOG_API_BASE_URL,
            timeout=settings.PRODUCT_CATALOG_API_TIMEOUT_LIMIT,
        )
    return client


async def close_httpx_client():
    global client
    if client:
        await client.aclose()
        client = None


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session


# Customers
def get_task_manager(request: Request) -> TaskManager:
    return request.app.state.task_manager


def get_jwt_service() -> IJWTService:
    return JWTService()


def get_customer_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ICustomerRepository:
    return PostgresCustomerRepository(session)


def get_sign_in_use_case(
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
    jwt_service: IJWTService = Depends(get_jwt_service),
) -> ISignInUseCase:
    return SignInUseCase(customer_repository, jwt_service)


def get_sign_up_use_case(
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
) -> ISignUpUseCase:
    return SignUpUseCase(customer_repository)


def get_fake_store_product_catalog(
    client: AsyncClient = Depends(get_httpx_client),
) -> IProductCatalog:
    return FakeStoreProductCatalog(client)


def get_list_customers_use_case(
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
) -> IListCustomersUseCase:
    return ListCustomersUseCase(customer_repository)


def get_fetch_customer_use_case(
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
) -> IFetchCustomerUseCase:
    return FetchCustomerUseCase(customer_repository)


def get_update_customer_use_case(
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
) -> IUpdateCustomerUseCase:
    return UpdateCustomerUseCase(customer_repository)


def get_delete_customer_use_case(
    customer_repository: ICustomerRepository = Depends(get_customer_repository),
) -> IDeleteCustomerUseCase:
    return DeleteCustomerUseCase(customer_repository)


# Favorites
def get_customer_favorite_product_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ICustomerFavoriteProductRepository:
    return PostgresCustomerFavoriteProductRepository(session)


def get_product_cache_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IProductCacheRepository:
    return PostgresProductCacheRepository(session)


def get_favorite_product_use_case(
    customer_favorite_product_repository: ICustomerFavoriteProductRepository = Depends(
        get_customer_favorite_product_repository
    ),
    product_cache_repository: IProductCacheRepository = Depends(
        get_product_cache_repository
    ),
    product_catalog: IProductCatalog = Depends(get_fake_store_product_catalog),
) -> IFavoriteProductUseCase:
    return FavoriteProductUseCase(
        customer_favorite_product_repository,
        product_cache_repository,
        product_catalog,
    )


def get_list_customer_favorite_products_use_case(
    customer_favorite_product_repository: ICustomerFavoriteProductRepository = Depends(
        get_customer_favorite_product_repository
    ),
    product_cache_repository: IProductCacheRepository = Depends(
        get_product_cache_repository
    ),
    product_catalog: IProductCatalog = Depends(get_fake_store_product_catalog),
    task_manager: TaskManager = Depends(get_task_manager),
) -> IListCustomerFavoriteProductsUseCase:
    return ListCustomerFavoriteProductsUseCase(
        customer_favorite_product_repository,
        product_cache_repository,
        product_catalog,
        task_manager,
    )


def get_unfavorite_product_use_case(
    customer_favorite_product_repository: ICustomerFavoriteProductRepository = Depends(
        get_customer_favorite_product_repository
    ),
) -> IUnfavoriteProductUseCase:
    return UnfavoriteProductUseCase(customer_favorite_product_repository)
