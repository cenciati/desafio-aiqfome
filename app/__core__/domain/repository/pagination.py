from app.__core__.domain.strict_record import strict_record


@strict_record
class PaginationInput:
    page: int
    per_page: int


@strict_record
class PaginationOutput:
    page: int
    per_page: int
    total_pages: int
    total_items: int
