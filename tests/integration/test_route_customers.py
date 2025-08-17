from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.postgres.orm.customer_orm import CustomerORM

BASE_ENDPOINT = "/customers"


@pytest.mark.asyncio
@pytest.mark.integration
class TestCustomerRoute:
    @pytest.fixture
    def test_customer_data(self, customer_id: str):
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

    @pytest.mark.parametrize("method", ["get", "patch", "delete"])
    async def test_should_return_403_when_customer_tries_to_perform_an_action_on_behalf_of_another_customer(
        self,
        method: str,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        await self.create_test_customer(async_session, test_customer_data)
        another_customer_id = str(uuid4())

        response = await http_client.request(
            method,
            f"{BASE_ENDPOINT}/{another_customer_id}",
            **{
                "json": (
                    {}
                    if method == "get"
                    else {"name": "foobar", "email": "foo@bar.com"}
                )
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "forbidden"

    async def test_should_fetch_customer_by_id_when_id_is_valid(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        customer = await self.create_test_customer(async_session, test_customer_data)

        response = await http_client.get(f"{BASE_ENDPOINT}/{customer.id}")
        response_data = response.json()

        assert response.status_code == 200
        assert response_data["id"] == customer.id
        assert response_data["name"] == customer.name
        assert response_data["email"] == customer.email
        assert response_data["created_at"] is not None
        assert response_data["updated_at"] is not None

    async def test_should_update_customer_name(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        old_customer = await self.create_test_customer(
            async_session, test_customer_data
        )

        response = await http_client.patch(
            f"{BASE_ENDPOINT}/{old_customer.id}",
            json={"name": "new foobar name"},
        )
        await async_session.refresh(old_customer)
        new_customer = await async_session.get(CustomerORM, old_customer.id)

        assert response.status_code == 204
        assert new_customer.name == "new foobar name"
        assert new_customer.email == old_customer.email

    async def test_should_update_customer_email(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        old_customer = await self.create_test_customer(
            async_session, test_customer_data
        )

        response = await http_client.patch(
            f"{BASE_ENDPOINT}/{old_customer.id}",
            json={"email": "new_foobar@email.com"},
        )
        await async_session.refresh(old_customer)
        new_customer = await async_session.get(CustomerORM, old_customer.id)

        assert response.status_code == 204
        assert new_customer.email == "new_foobar@email.com"
        assert new_customer.name == old_customer.name

    async def test_should_return_400_when_email_is_invalid(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        old_customer = await self.create_test_customer(
            async_session, test_customer_data
        )

        response = await http_client.patch(
            f"{BASE_ENDPOINT}/{old_customer.id}",
            json={"email": "invalid_email"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "invalid_email"

    async def test_should_return_204_when_customer_deletes_itself(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
    ):
        customer = await self.create_test_customer(async_session, test_customer_data)

        response = await http_client.delete(f"{BASE_ENDPOINT}/{customer.id}")

        assert response.status_code == 204
        assert await async_session.get(CustomerORM, customer.id) is None

    async def test_should_list_all_customers_when_api_key_sent_is_valid(
        self,
        http_client: AsyncClient,
        async_session: AsyncSession,
        test_customer_data: dict,
        auth_headers: dict,
    ):
        test_customer_data_2 = test_customer_data.copy()
        test_customer_data_2["id"] = str(uuid4())
        test_customer_data_2["email"] = "foo2@bar.com"
        customer_1 = await self.create_test_customer(async_session, test_customer_data)
        customer_2 = await self.create_test_customer(
            async_session, test_customer_data_2
        )

        response = await http_client.get(f"{BASE_ENDPOINT}", headers=auth_headers)
        response_data = response.json()

        assert response.status_code == 200
        assert len(response_data["data"]) == 2
        assert response_data["data"][0]["id"] == customer_1.id
        assert response_data["data"][1]["id"] == customer_2.id
        assert response_data["pagination"]["page"] == 1
        assert response_data["pagination"]["per_page"] == 20
        assert response_data["pagination"]["total_pages"] == 1
        assert response_data["pagination"]["total_items"] == 2

    async def test_should_return_400_when_page_is_less_than_1(
        self,
        http_client: AsyncClient,
        auth_headers: dict,
    ):
        response = await http_client.get(
            f"{BASE_ENDPOINT}?page=0", headers=auth_headers
        )
        assert response.status_code == 422

    async def test_should_return_400_when_per_page_is_less_than_1(
        self,
        http_client: AsyncClient,
        auth_headers: dict,
    ):
        response = await http_client.get(
            f"{BASE_ENDPOINT}?per_page=0", headers=auth_headers
        )
        assert response.status_code == 422
