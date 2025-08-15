from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class PaginationInput:
    page: int
    per_page: int


@dataclass(slots=True, frozen=True, kw_only=True)
class PaginationOutput:
    page: int
    per_page: int
    total_pages: int
    total_items: int
