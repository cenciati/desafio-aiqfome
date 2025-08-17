import asyncio
from datetime import datetime, timedelta, timezone

from app.__core__.application.gateways.product_catalog import IProductCatalog
from app.__core__.application.logger import logger
from app.__core__.application.settings import get_settings
from app.__core__.domain.entity.product import Product
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.repository.repository import IProductCacheRepository

settings = get_settings()


class BaseProductCacheUseCase:
    def __init__(
        self,
        product_cache_repository: IProductCacheRepository,
        product_catalog: IProductCatalog,
    ):
        self.product_cache_repository = product_cache_repository
        self.product_catalog = product_catalog

        self.soft_ttl = timedelta(minutes=settings.PRODUCT_CACHE_SOFT_TTL_MINUTES)
        self.hard_ttl = timedelta(minutes=settings.PRODUCT_CACHE_HARD_TTL_MINUTES)

        self._catalog_semaphore = asyncio.Semaphore(
            settings.PRODUCT_CATALOG_API_MAX_CONCURRENCY
        )

    async def _fetch_and_insert(self, product_id: int) -> Product:
        async with self._catalog_semaphore:
            product = await self.product_catalog.fetch_one(product_id)

        if product is None:
            raise ValidationError("product_not_found")

        await self.product_cache_repository.insert_one(product)
        return product

    async def _fetch_and_refresh(self, product_id: int) -> Product:
        async with self._catalog_semaphore:
            product = await self.product_catalog.fetch_one(product_id)

        if product is None:
            raise ValidationError("product_not_found")

        await self.product_cache_repository.refresh(product)
        return product

    async def _refresh_cache(self, product_id: int) -> None:
        try:
            async with self._catalog_semaphore:
                product = await self.product_catalog.fetch_one(product_id)

            if product is None:
                raise ValidationError("product_not_found")

            await self.product_cache_repository.refresh(product)
        except Exception:
            logger.exception("refresh_cache_error")

    def _get_cache_age(self, cached_product: Product) -> timedelta:
        return datetime.now(timezone.utc) - cached_product.fetched_at.replace(
            tzinfo=timezone.utc
        )

    def _is_cache_fresh(self, age: timedelta) -> bool:
        return age <= self.soft_ttl

    def _is_cache_stale(self, age: timedelta) -> bool:
        return age > self.hard_ttl
