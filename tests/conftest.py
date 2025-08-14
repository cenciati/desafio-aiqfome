import pytest

from app.__core__.application.settings import get_settings, Settings


@pytest.fixture
def mock_settings(monkeypatch):
    get_settings.cache_clear()

    fake_settings = Settings(
        ENV="dev",
        API_PORT=8000,
        API_DEBUG=True,
        PAGINATION_PER_PAGE_LIMIT=50,
        PRODUCT_CATALOG_API_BASE_URL="http://fake-api.local",
        PRODUCT_CATALOG_API_TIMEOUT_LIMIT=5.0,
        PRODUCT_CATALOG_API_MAX_RETRIES=3,
        API_KEY="fake-api-key",
        JWT_SECRET_KEY="fake-secret",
        JWT_EXPIRE_DAYS=7,
        DATABASE_DIALECT="postgresql",
        DATABASE_HOST="localhost",
        DATABASE_PORT=5432,
        DATABASE_USER="user",
        DATABASE_PASSWORD="pass",
        DATABASE_NAME="test_db",
        DATABASE_POOL_SIZE=5,
    )

    monkeypatch.setattr(
        "app.__core__.application.settings.get_settings", lambda: fake_settings
    )

    return fake_settings
