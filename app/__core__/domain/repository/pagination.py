from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class Pagination:
    page: int
    per_page: int
    total_pages: int
    total_items: int
