from typing import Dict, Optional
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.domain.entity.product import Product
from app.__main__ import app
from app.infra.dependency import (get_async_session,
                                  get_fake_store_product_catalog)


@pytest.fixture(scope="session")
def postgres_container():
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:17.4") as postgres:
        yield postgres


@pytest_asyncio.fixture
async def async_engine(postgres_container):
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(
        postgres_container.get_connection_url(driver="psycopg"),
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def session_factory(async_engine):
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.ext.asyncio.session import async_sessionmaker

    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def async_session(session_factory):
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="session")
def customer_id() -> str:
    return str(uuid4())


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    from app.__core__.application.settings import get_settings

    settings = get_settings()
    return {"x-aiqfome-api-key": settings.API_KEY}


@pytest.fixture
def stub_product_catalog():
    class StubProductCatalog(IProductCatalog):
        async def fetch_one(self, id: int) -> Optional[Product]:
            product_id_that_does_not_exist = 999
            if id == product_id_that_does_not_exist:
                return None

            return Product(
                id=id,
                title="Product",
                image_url="https://example.com",
                price=30.0,
                review=None,
            )

    return StubProductCatalog()


@pytest_asyncio.fixture
async def http_client(
    async_session: AsyncSession, customer_id: str, stub_product_catalog: IProductCatalog
):
    from httpx import ASGITransport, AsyncClient

    from app.__core__.application.task_manager import TaskManager
    from app.infra.jwt.jwt_service import JWTService

    async def get_test_session():
        yield async_session

    app.dependency_overrides[get_async_session] = get_test_session
    app.state.task_manager = TaskManager()
    app.dependency_overrides[get_fake_store_product_catalog] = (
        lambda: stub_product_catalog
    )

    jwt_service = JWTService()
    access_token = jwt_service.create_token(customer_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set("access_token", access_token)
        yield client
