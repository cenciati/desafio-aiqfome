from unittest.mock import AsyncMock, MagicMock

import pytest

from app.__core__.application.use_case.sign_up_use_case import (SignUpInput,
                                                                SignUpOutput,
                                                                SignUpUseCase)
from app.__core__.domain.exception.exception import ValidationError


@pytest.mark.unit
@pytest.mark.asyncio
class TestSignUpUseCase:
    valid_email = "foo@bar.com"
    invalid_email = "invalid_email"
    valid_password = "barbarbarbarbarbarbarbar"
    invalid_password = "bar"

    async def test_should_raise_validation_error_when_email_already_exists(self):
        user_repo = AsyncMock()
        user_repo.fetch_one_by_email.return_value = MagicMock()

        use_case = SignUpUseCase(user_repo)

        with pytest.raises(ValidationError) as exc:
            await use_case.execute(
                SignUpInput(
                    name="foo",
                    email=self.valid_email,
                    password=self.valid_password,
                )
            )

        assert str(exc.value) == "email_already_exists"
        user_repo.fetch_one_by_email.assert_awaited_once_with(self.valid_email)

    async def test_should_raise_validation_error_when_password_is_invalid(self):
        user_repo = AsyncMock()
        user_repo.fetch_one_by_email.return_value = None

        use_case = SignUpUseCase(user_repo)

        with pytest.raises(ValidationError) as exc:
            await use_case.execute(
                SignUpInput(
                    name="foo",
                    email=self.valid_email,
                    password=self.invalid_password,
                )
            )

        assert str(exc.value) == "password_must_be_a_string_between_8_and_32_characters"
        user_repo.fetch_one_by_email.assert_not_called()

    async def test_should_create_user_when_password_is_valid(self):
        user_repo = AsyncMock()
        user_repo.fetch_one_by_email.return_value = None
        user_repo.insert_one.return_value = MagicMock()

        use_case = SignUpUseCase(user_repo)

        output = await use_case.execute(
            SignUpInput(
                name="foo",
                email=self.valid_email,
                password=self.valid_password,
            )
        )

        assert isinstance(output, SignUpOutput)
        assert isinstance(output.id, str)
        assert len(output.id) == 36  # Tamanho de um UUID v4
        user_repo.fetch_one_by_email.assert_awaited_once_with(self.valid_email)

    async def test_should_raise_validation_error_when_email_is_invalid(self):
        customer_repo = AsyncMock()

        use_case = SignUpUseCase(customer_repo)

        with pytest.raises(ValidationError) as exc:
            await use_case.execute(
                SignUpInput(
                    name="foo", email="invalid_email", password=self.valid_password
                )
            )

        assert str(exc.value) == "invalid_email"
        customer_repo.insert_one.assert_not_called()
