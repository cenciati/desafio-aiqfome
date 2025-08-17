from typing import Optional

from httpx import AsyncClient, TimeoutException

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.application.retry_with_backoff import retry_with_backoff
from app.__core__.application.settings import get_settings
from app.__core__.domain.entity.product import Product

settings = get_settings()


class FakeStoreProductCatalog(IProductCatalog):
    MAX_RETRIES = settings.PRODUCT_CATALOG_API_MAX_RETRIES

    def __init__(self, client: AsyncClient):
        self.client = client

    @retry_with_backoff(TimeoutException)
    async def fetch_one(self, id: int) -> Optional[Product]:
        response = await self.client.get(f"/products/{id}")
        return Product.from_api_to_domain(response.json())
