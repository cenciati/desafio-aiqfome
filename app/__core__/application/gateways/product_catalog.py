from abc import ABC, abstractmethod
from typing import List

from app.__core__.domain.entity.product import Product


class IProductCatalog(ABC):
    @abstractmethod
    async def fetch_many(self, ids: List[int]) -> List[Product]: ...
