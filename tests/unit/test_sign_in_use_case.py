from unittest.mock import AsyncMock, MagicMock

import pytest

from app.__core__.application.use_case.sign_in_use_case import (SignInInput,
                                                                SignInOutput,
                                                                SignInUseCase)
from app.__core__.domain.exception.exception import AuthenticationError


@pytest.mark.unit
@pytest.mark.asyncio
class TestSignInUseCase:
    async def test_should_raise_authentication_error_when_user_not_found(self):
        customer_repo = AsyncMock()
        customer_repo.fetch_one_by_email.return_value = None
        jwt_service = MagicMock()

        use_case = SignInUseCase(customer_repo, jwt_service)

        with pytest.raises(AuthenticationError) as exc:
            await use_case.execute(SignInInput(email="foo@bar.com", password="bar"))

        assert str(exc.value) == "invalid_credentials"
        customer_repo.fetch_one_by_email.assert_awaited_once_with("foo@bar.com")
        jwt_service.create_token.assert_not_called()

    async def test_should_raise_authentication_error_when_password_is_invalid(self):
        fake_user = MagicMock()
        fake_user.password.verify.return_value = False
        customer_repo = AsyncMock()
        customer_repo.fetch_one_by_email.return_value = fake_user
        jwt_service = MagicMock()

        use_case = SignInUseCase(customer_repo, jwt_service)

        with pytest.raises(AuthenticationError) as exc:
            await use_case.execute(SignInInput(email="foo@bar.com", password="wrong"))

        assert str(exc.value) == "invalid_credentials"
        customer_repo.fetch_one_by_email.assert_awaited_once_with("foo@bar.com")
        fake_user.password.verify.assert_called_once_with("wrong")
        jwt_service.create_token.assert_not_called()

    async def test_should_return_access_token_when_password_is_valid(self):
        fake_user = MagicMock()
        fake_user.password.verify.return_value = True
        fake_user.str_id = "user-123"
        customer_repo = AsyncMock()
        customer_repo.fetch_one_by_email.return_value = fake_user
        jwt_service = MagicMock()
        jwt_service.create_token.return_value = "token123"

        use_case = SignInUseCase(customer_repo, jwt_service)

        output = await use_case.execute(
            SignInInput(email="foo@bar.com", password="bar")
        )

        assert isinstance(output, SignInOutput)
        assert output.access_token == "token123"
        customer_repo.fetch_one_by_email.assert_awaited_once_with("foo@bar.com")
        fake_user.password.verify.assert_called_once_with("bar")
        jwt_service.create_token.assert_called_once_with("user-123")
