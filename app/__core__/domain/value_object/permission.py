from enum import Enum

from app.__core__.domain.exception.exception import ValidationError


class Permission(str, Enum):
    CUSTOMERS_CREATE = "customers:create"
    CUSTOMERS_READ = "customers:read"
    CUSTOMERS_UPDATE = "customers:update"
    CUSTOMERS_DELETE = "customers:delete"
    FAVORITES_CREATE = "favorites:create"
    FAVORITES_READ = "favorites:read"
    FAVORITES_UPDATE = "favorites:update"
    FAVORITES_DELETE = "favorites:delete"

    @classmethod
    def from_string(cls, permission: str) -> "Permission":
        try:
            return cls(permission)
        except ValueError:
            raise ValidationError("invalid_permission_data_type")
