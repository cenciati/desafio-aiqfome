import pytest

from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.value_object.password import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    Password,
)


@pytest.mark.unit
class TestPassword:
    def test_should_create_password_with_valid_data(self):
        password = Password.create("validpassword123")
        assert password.hash.startswith("$argon2id$v=19$m=65536,t=3,p=4$")

    @pytest.mark.parametrize(
        "invalid_password",
        [
            "",
            "A" * (PASSWORD_MIN_LENGTH - 1),
            "A" * (PASSWORD_MAX_LENGTH + 1),
            123,
            None,
            [],
            {},
        ],
    )
    def test_should_raise_validation_error_when_password_is_invalid(
        self, invalid_password
    ):
        with pytest.raises(
            ValidationError,
            match="password_must_be_a_string_between_8_and_32_characters",
        ):
            Password.create(invalid_password)

    def test_should_verify_password_with_valid_password(self):
        raw_password = "validpassword123"
        password = Password.create(raw_password)
        assert password.verify(raw_password)

    def test_should_verify_password_with_invalid_password(self):
        raw_password = "validpassword123"
        password = Password.create(raw_password)
        assert not password.verify("invalidpassword")
