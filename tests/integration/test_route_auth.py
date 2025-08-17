import pytest
from httpx import AsyncClient

BASE_ENDPOINT = "/auth"
API_KEY_REQUIRED_ENDPOINT = "/customers"


@pytest.mark.asyncio
@pytest.mark.integration
class TestAPIKey:
    async def test_api_key_required(self, http_client: AsyncClient):
        response = await http_client.get(API_KEY_REQUIRED_ENDPOINT)

        assert response.status_code == 401
        assert response.json()["detail"] == "missing_api_key"

    async def test_api_key_valid(self, http_client: AsyncClient, auth_headers: dict):
        http_client.headers.update(auth_headers)
        response = await http_client.get(API_KEY_REQUIRED_ENDPOINT)

        assert response.status_code != 401
        assert response.json()["data"] == []


@pytest.mark.asyncio
@pytest.mark.integration
class TestAuthRoute:
    async def test_should_return_401_when_sign_in_with_invalid_password(
        self, http_client: AsyncClient
    ):
        email, password = "foo@bar.com", "foobarbarbar1"
        await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={"email": email, "name": "foo bar", "password": password},
        )

        response = await http_client.post(
            f"{BASE_ENDPOINT}/sign-in",
            json={"email": email, "password": password.upper()},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "invalid_credentials"

    async def test_should_return_401_when_sign_in_with_unknown_email(
        self, http_client: AsyncClient
    ):
        response = await http_client.post(
            f"{BASE_ENDPOINT}/sign-in",
            json={"email": "foo@bar.com", "password": "foobarbarbar"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "invalid_credentials"

    async def test_should_return_200_and_set_access_token_cookie_when_sign_in_with_valid_credentials(
        self, http_client: AsyncClient
    ):
        email, password = "foo@bar.com", "foobarbarbar"
        await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={"email": email, "name": "foo bar", "password": password},
        )

        response = await http_client.post(
            f"{BASE_ENDPOINT}/sign-in",
            json={"email": email, "password": password},
        )

        assert response.status_code == 200
        assert response.cookies.get("access_token") is not None
        assert response.cookies.get("access_token").startswith("ey")

    async def test_should_return_201_when_sign_up_with_valid_credentials(
        self, http_client: AsyncClient
    ):
        response = await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={
                "email": "foo@bar.com",
                "name": "foo bar",
                "password": "foobarbarbar",
            },
        )
        response_data = response.json()

        assert response.status_code == 201
        assert isinstance(response_data["id"], str)
        assert len(response_data["id"]) == 36

    async def test_should_return_400_when_sign_up_with_invalid_email(
        self, http_client: AsyncClient
    ):
        response = await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={
                "email": "invalid_email",
                "name": "foo bar",
                "password": "foobarbarbar",
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "invalid_email"

    async def test_should_return_400_when_sign_up_with_already_existing_email(
        self, http_client: AsyncClient
    ):
        email = "foo@bar.com"
        await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={"email": email, "name": "foo bar", "password": "foobarbarbar"},
        )
        response = await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={"email": email, "name": "foo bar", "password": "foobarbarbar"},
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "email_already_exists"

    async def test_should_return_204_when_sign_out(self, http_client: AsyncClient):
        email, password = "foo@bar.com", "foobarbarbar"
        await http_client.post(
            f"{BASE_ENDPOINT}/sign-up",
            json={"email": email, "name": "foo bar", "password": password},
        )
        await http_client.post(
            f"{BASE_ENDPOINT}/sign-in",
            json={"email": email, "password": password},
        )

        response = await http_client.post(f"{BASE_ENDPOINT}/sign-out")

        assert response.status_code == 204
        assert response.cookies.get("access_token") is None
