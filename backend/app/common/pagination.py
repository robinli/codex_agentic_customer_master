from math import ceil
from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    page: int
    page_size: int
    total: int
    total_pages: int


def build_page(*, items: Sequence[T], page: int, page_size: int, total: int) -> Page[T]:
    return Page(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=max(1, ceil(total / page_size)) if page_size else 1,
    )

