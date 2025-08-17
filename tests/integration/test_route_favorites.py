from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.postgres.orm.customer_favorite_product_orm import \
    CustomerFavoriteProductORM
from app.infra.postgres.orm.customer_orm import CustomerORM
from app.infra.postgres.orm.product_cache_orm import ProductCacheORM

BASE_ENDPOINT = "/customers/{}/favorites"


@pytest.mark.asyncio
@pytest.mark.integration
class TestFavoritesRoute:
    @pytest.fixture
    def test_customer_data(self, customer_id: str) -> dict:
        return {
            "id": customer_id,
            "name": "foobar",
            "email": "foo@bar.com",
            "password_hash": "foobarfoobar",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    async def create_test_customer(
        self, async_session: AsyncSession, customer_data: dict
    ) -> CustomerORM:
        customer = CustomerORM(**customer_data)
        async_session.add(customer)
        await async_session.commit()
        return customer

    async def add_product_to_cache(
        self, async_session: AsyncSession, product_id: int, fetched_at: datetime
    ) -> ProductCacheORM:
        product_cache = ProductCacheORM(
            id=product_id,
            title="test product",
            image_url="https://test.com/image.jpg",
            price=100,
            review_rate=4.5,
            review_count=100,
            fetched_at=fetched_at,
        )
        async_session.add(product_cache)
        await async_session.commit()
        return product_cache

    async def add_favorite_to_test_customer(
        self, async_session: AsyncSession, customer_data: dict, product_id: int
    ) -> CustomerFavoriteProductORM:
        customer_favorite_product = CustomerFavoriteProductORM(
            customer_id=customer_data["id"],
            product_id=product_id,
            favorited_at=datetime.now(),
        )
        async_session.add(customer_favorite_product)
        await async_session.commit()
        return customer_favorite_product

    @pytest.mark.parametrize("method", ["get", "post", "delete"])
    async def test_should_return_403_when_customer_tries_to_perform_an_action_on_behalf_of_another_customer(
        self,
        method: str,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        await self.create_test_customer(async_session, test_customer_data)
        another_customer_id = str(uuid4())
        any_product_id = 1

        endpoint = (
            BASE_ENDPOINT.format(another_customer_id)
            if method == "get"
            else f"{BASE_ENDPOINT.format(another_customer_id)}/{any_product_id}"
        )
        response = await http_client.request(method, endpoint)

        assert response.status_code == 403
        assert response.json()["detail"] == "forbidden"

    async def test_should_return_422_when_trying_to_favorite_a_product_that_is_already_in_favorites(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        product_id = 1
        await self.create_test_customer(async_session, test_customer_data)
        await self.add_favorite_to_test_customer(
            async_session, test_customer_data, product_id=product_id
        )
        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/{product_id}"

        response = await http_client.post(endpoint)

        assert response.status_code == 409
        assert response.json()["detail"] == "product_already_in_favorites"

    async def test_should_return_422_when_trying_to_favorite_a_product_that_does_not_exist(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        await self.create_test_customer(async_session, test_customer_data)
        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/999"

        response = await http_client.post(endpoint)

        assert response.status_code == 404
        assert response.json()["detail"] == "product_not_found"

    async def test_should_return_201_when_favoriting_a_product_that_is_not_in_favorites(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        product_id = 1
        await self.create_test_customer(async_session, test_customer_data)
        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/{product_id}"

        response = await http_client.post(endpoint)
        customer_favorite_product = await async_session.get(
            CustomerFavoriteProductORM, (test_customer_data["id"], product_id)
        )

        assert response.status_code == 201
        assert customer_favorite_product is not None
        assert str(customer_favorite_product.customer_id) == test_customer_data["id"]
        assert customer_favorite_product.product_id == product_id
        assert customer_favorite_product.favorited_at is not None

    async def test_should_insert_product_to_cache_table_when_it_is_still_not_in_it(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        product_id = 1
        await self.create_test_customer(async_session, test_customer_data)
        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/{product_id}"

        response = await http_client.post(endpoint)
        product_cache = await async_session.get(ProductCacheORM, product_id)

        assert response.status_code == 201
        assert product_cache is not None
        assert product_cache.id == product_id

    async def test_should_return_cached_product_when_it_is_still_fresh(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        product_id, fetched_at = 1, datetime.now() - timedelta(minutes=3)
        await self.create_test_customer(async_session, test_customer_data)
        await self.add_product_to_cache(async_session, product_id, fetched_at)

        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/{product_id}"

        response = await http_client.post(endpoint)
        product_cache = await async_session.get(ProductCacheORM, product_id)

        assert response.status_code == 201
        assert product_cache is not None
        assert product_cache.id == product_id
        assert product_cache.fetched_at is not None
        assert (
            product_cache.fetched_at == fetched_at
        )  # validando que não houve refresh no cache, pois ainda está fresco (abaixo do soft_ttl)

    async def test_should_refresh_product_cache_when_it_is_not_fresh(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        product_id, fetched_at = 1, datetime.now() - timedelta(hours=24)
        await self.create_test_customer(async_session, test_customer_data)
        await self.add_product_to_cache(async_session, product_id, fetched_at)

        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/{product_id}"
        response = await http_client.post(endpoint)
        product_cache = await async_session.get(ProductCacheORM, product_id)

        assert response.status_code == 201
        assert product_cache is not None
        assert product_cache.id == product_id
        assert product_cache.fetched_at is not None
        assert product_cache.fetched_at > fetched_at  # validando que houve o refresh

    async def test_should_return_422_when_trying_to_unfavorite_a_product_that_is_not_in_favorites(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        await self.create_test_customer(async_session, test_customer_data)
        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/999"

        response = await http_client.delete(endpoint)

        assert response.status_code == 422
        assert response.json()["detail"] == "product_not_in_favorites"

    async def test_should_return_200_when_unfavoriting_a_product_that_is_in_favorites(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        product_id = 1
        await self.create_test_customer(async_session, test_customer_data)
        await self.add_favorite_to_test_customer(
            async_session, test_customer_data, product_id=product_id
        )
        endpoint = f"{BASE_ENDPOINT.format(test_customer_data['id'])}/{product_id}"

        response = await http_client.delete(endpoint)
        customer_favorite_product = await async_session.get(
            CustomerFavoriteProductORM, (test_customer_data["id"], product_id)
        )

        assert response.status_code == 204
        assert customer_favorite_product is None
