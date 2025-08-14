from datetime import datetime
from uuid import uuid4
import pytest

from app.__core__.domain.entity.user import User
from app.__core__.domain.value_object.password import Password
from app.__core__.domain.value_object.permission import Permission
from app.__core__.domain.exception.exception import ValidationError
from app.infra.postgres.orm.user_orm import UserORM


@pytest.mark.unit
class TestUser:
    def build_valid_user(self, **kwargs) -> User:
        return User(
            id=kwargs.get("id", uuid4()),
            slug=kwargs.get("slug", "foobar"),
            password=kwargs.get("password", Password(hash="hashed123")),
            permissions=kwargs.get("permissions", [Permission.CUSTOMERS_READ]),
            created_at=kwargs.get("created_at", datetime.now()),
            updated_at=kwargs.get("updated_at", datetime.now()),
        )

    @pytest.mark.parametrize(
        "field,value,error_msg",
        [
            ("slug", 123, "invalid_slug_data_type"),
            ("password", "not_a_password", "invalid_password_data_type"),
            ("permissions", "not_a_list", "invalid_permissions_data_type"),
        ],
    )
    def test_post_init_validation(self, field, value, error_msg):
        kwargs = {
            "slug": "validslug",
            "password": Password(hash="hashed123"),
            "permissions": [Permission.CUSTOMERS_READ],
        }
        kwargs[field] = value
        with pytest.raises(ValidationError) as exc:
            self.build_valid_user(**kwargs)
        assert str(exc.value) == error_msg
