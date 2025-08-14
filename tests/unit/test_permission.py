import pytest

from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.value_object.permission import Permission


@pytest.mark.unit
class TestPermission:
    def test_should_create_permission_with_valid_data(self):
        permission = Permission.from_string("customers:create")

        assert permission is Permission.CUSTOMERS_CREATE
        assert isinstance(permission, Permission)
        assert permission.value == "customers:create"

    def test_should_raise_validation_error_when_permission_is_invalid(self):
        with pytest.raises(
            ValidationError,
            match="invalid_permission_data_type",
        ):
            Permission.from_string("invalid:perm")
