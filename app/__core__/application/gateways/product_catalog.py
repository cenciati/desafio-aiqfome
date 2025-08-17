from abc import ABC, abstractmethod
from typing import Optional

from app.__core__.domain.entity.product import Product


class IProductCatalog(ABC):
    @abstractmethod
    async def fetch_one(self, id: int) -> Optional[Product]: ...
