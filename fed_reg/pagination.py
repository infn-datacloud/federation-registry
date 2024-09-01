from typing import Any

from pydantic import BaseModel, Field, validator


class Pagination(BaseModel):
    """Model to filter lists in GET operations with multiple items.

    Attributes:
    ----------
        page (int): Divide the list in chunks.
        size (int | None): Chunk size.
    """

    size: int | None = Field(default=None, ge=1, description="Chunk size.")
    page: int = Field(default=0, ge=0, description="Divide the list in chunks")

    @validator("page", pre=True)
    @classmethod
    def set_page_to_0(cls, v: int, values: dict[str, Any]) -> int:
        """If chunk size is 0 set page index to 0."""
        if values.get("size") is None:
            return 0
        return v


def paginate(*, items: list[Any], page: int, size: int | None) -> list[Any]:
    """Divide the list in chunks.

    Args:
    ----
        items (list[Any]): list to split.
        page (int): Target chunk (start from 0).
        size (int | None): Chunk size.

    Returns:
    -------
        list[Any]. Chunk with index equal to page and length equal to, at most, size.
    """
    if size is None or size == 0:
        return items
    start = page * size
    end = start + size
    return items[start:end]
