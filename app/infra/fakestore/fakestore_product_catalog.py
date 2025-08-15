import asyncio
from typing import List

from httpx import AsyncClient

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.application.settings import get_settings
from app.__core__.domain.entity.product import Product

settings = get_settings()


class FakeStoreProductCatalog(IProductCatalog):
    MAX_RETRIES = settings.PRODUCT_CATALOG_API_MAX_RETRIES

    def __init__(self, client: AsyncClient):
        self.client = client

    async def fetch_many(self, ids: List[int]) -> List[Product]:
        tasks = [self.client.get(f"/products/{id}") for id in ids]
        responses = await asyncio.gather(*tasks)
        return [
            Product.to_domain(response.json()) if response.status_code == 200 else None
            for response in responses
        ]
