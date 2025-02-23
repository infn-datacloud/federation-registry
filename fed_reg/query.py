"""Module defining the classes with query common attributes."""

from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class SchemaSize(BaseModel):
    """Model to add query attribute related to data response size.

    Attributes:
    ----------
        with_conn (bool): Show related items.
        short (bool): Return shrunk version of data. Only for authenticated users.
    """

    short: bool = Field(default=False, description="Show a shrunk version of the item.")
    with_conn: bool = Field(default=False, description="Show related items.")


class Pagination(BaseModel):
    """Model to filter lists in GET operations with multiple items.

    Attributes:
    ----------
        page (int): Divide the list in chunks.
        size (int | None): Chunk size.
    """

    size: Optional[int] = Field(default=None, ge=1, description="Chunk size.")
    page: int = Field(default=0, ge=0, description="Divide the list in chunks")

    @validator("page", pre=True)
    @classmethod
    def set_page_to_0(cls, v: int, values: dict[str, Any]) -> int:
        """If chunk size is 0 set page index to 0."""
        if values.get("size") is None:
            return 0
        return v


class DbQueryCommonParams(BaseModel):
    """Model to read common query attributes passed to GET operations.

    Attributes:
    ----------
        skip (int): Number of items to skip from the first one in the list.
        limit (int | None): Maximum number or returned items.
        sort (str | None): Sorting rule.
    """

    skip: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip from the first one in the list.",
    )
    limit: Optional[int] = Field(
        default=None, ge=0, description="Maximum number or returned items."
    )
    sort: Optional[str] = Field(default=None, description="Sorting rule.")

    @validator("sort")
    @classmethod
    def parse_sort_rule(cls, v: Optional[str]) -> Optional[str]:
        """Parse and correct sort rule.

        Remove `_asc` or `_desc` suffix. Prepend `-` when `_desc` is received.
        """
        if v is None:
            return v

        if v.endswith("_asc"):
            return v[: -len("_asc")]
        elif v.endswith("_desc"):
            if v.startswith("-"):
                return v[: -len("_desc")]
            return f"-{v[: -len('_desc')]}"
        return v
