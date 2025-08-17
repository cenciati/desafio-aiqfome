from abc import ABC, abstractmethod
from typing import Any, List


class BasePresenter(ABC):
    @staticmethod
    @abstractmethod
    def present(data: Any) -> List[dict] | dict:
        pass
