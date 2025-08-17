from datetime import datetime, timedelta, timezone
from typing import List

from app.__core__.application.presenters.base_presenter import BasePresenter
from app.__core__.application.use_case.fetch_customer_use_case import \
    FetchCustomerOutput


class CustomerPresenter(BasePresenter):
    @staticmethod
    def present(
        data: FetchCustomerOutput | List[FetchCustomerOutput],
    ) -> FetchCustomerOutput | List[FetchCustomerOutput]:
        def _present_single(c: FetchCustomerOutput) -> FetchCustomerOutput:
            return FetchCustomerOutput(
                id=c.id,
                name=c.name,
                email=c.email,
                created_at=CustomerPresenter.present_date(c.created_at),
                updated_at=CustomerPresenter.present_date(c.updated_at),
            )

        if isinstance(data, list):
            return [_present_single(value) for value in data]

        return _present_single(data)

    @staticmethod
    def present_date(date: datetime) -> str:
        utc_minus_3 = timezone(timedelta(hours=-3))
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc).astimezone(utc_minus_3)
        else:
            date = date.astimezone(utc_minus_3)
        return date.isoformat()
