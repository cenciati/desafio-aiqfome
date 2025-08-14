from abc import ABC, abstractmethod


class IJWTService(ABC):
    @abstractmethod
    def create_token(self, account_id: str) -> str: ...

    @abstractmethod
    def verify_token(self, token: str) -> dict: ...
