import pytest
from datetime import datetime
from uuid import uuid4

from app.__core__.domain.entity.customer import Customer
from app.__core__.domain.entity.customer import CreateCustomerProps
from app.__core__.domain.exception.exception import ValidationError


@pytest.mark.unit
class TestCustomer:
    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid_email",
            "invalid_email@example",
            "invalid_email@example.",
        ],
    )
    def test_should_raise_validation_error_when_email_is_invalid(self, invalid_email):
        with pytest.raises(ValidationError) as exc:
            Customer(name="Foo Bar", email=invalid_email)
        assert str(exc.value) == "invalid_email"

    def test_should_create_customer_with_lowercase_email(self):
        props = CreateCustomerProps(name="Foo Bar", email="Foo@Example.COM")
        customer = Customer.create(props)
        assert customer.name == "Foo Bar"
        assert customer.email == "foo@example.com"
        assert isinstance(customer.created_at, datetime)
        assert isinstance(customer.updated_at, datetime)

    def test_should_convert_customer_to_domain(self):
        raw = {
            "id": str(uuid4()),
            "name": "Foo Bar",
            "email": "foo@example.com",
            "created_at": datetime(2023, 1, 1, 10, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0),
        }

        customer = Customer.to_domain(raw)

        assert str(customer.id) == raw["id"]
        assert customer.name == raw["name"]
        assert customer.email == raw["email"]
        assert customer.created_at == raw["created_at"]
        assert customer.updated_at == raw["updated_at"]
