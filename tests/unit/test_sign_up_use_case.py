from unittest.mock import AsyncMock, MagicMock

import pytest

from app.__core__.application.use_case.sign_up_use_case import (
    SignUpInput,
    SignUpOutput,
    SignUpUseCase,
)
from app.__core__.domain.exception.exception import ValidationError
from app.__core__.domain.value_object.permission import Permission


@pytest.mark.unit
@pytest.mark.asyncio
class TestSignUpUseCase:
    valid_username = "foooooooooooooooooo"
    invalid_username = "fo"
    valid_password = "barbarbarbarbarbarbarbar"
    invalid_password = "bar"
    valid_permissions = [Permission.CUSTOMERS_CREATE]

    async def test_should_raise_authentication_error_when_username_already_exists(self):
        user_repo = AsyncMock()
        user_repo.fetch_one_by_slug.return_value = MagicMock()

        use_case = SignUpUseCase(user_repo)

        with pytest.raises(ValidationError) as exc:
            await use_case.execute(
                SignUpInput(
                    username=self.valid_username,
                    password=self.valid_password,
                    permissions=self.valid_permissions,
                )
            )

        assert str(exc.value) == "username_already_exists"
        user_repo.fetch_one_by_slug.assert_awaited_once_with(self.valid_username)

    async def test_should_raise_validation_error_when_password_is_invalid(self):
        user_repo = AsyncMock()
        user_repo.fetch_one_by_slug.return_value = None

        use_case = SignUpUseCase(user_repo)

        with pytest.raises(ValidationError) as exc:
            await use_case.execute(
                SignUpInput(
                    username=self.valid_username,
                    password=self.invalid_password,
                    permissions=self.valid_permissions,
                )
            )

        assert str(exc.value) == "password_must_be_a_string_between_8_and_32_characters"
        user_repo.fetch_one_by_slug.assert_awaited_once_with(self.valid_username)

    async def test_should_create_user_when_password_is_valid(self):
        user_repo = AsyncMock()
        user_repo.fetch_one_by_slug.return_value = None
        user_repo.insert_one.return_value = MagicMock()

        use_case = SignUpUseCase(user_repo)

        output = await use_case.execute(
            SignUpInput(
                username=self.valid_username,
                password=self.valid_password,
                permissions=self.valid_permissions,
            )
        )

        assert isinstance(output, SignUpOutput)
        assert isinstance(output.id, str)
        assert len(output.id) == 36  # Tamanho de um UUID v4
        assert output.username == self.valid_username
        user_repo.fetch_one_by_slug.assert_awaited_once_with(self.valid_username)
