import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import text


@pytest.mark.asyncio
@pytest.mark.integration
class TestIntegrationSetup:
    async def test_database_connection(self, async_session: AsyncSession):
        result = await async_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    async def test_health_check(self, http_client: AsyncClient):
        response = await http_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
