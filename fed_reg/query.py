"""Module defining the classes with query common attributes."""

from typing import Any, TypeVar

from fedreg.core import (
    BaseReadPrivate,
    BaseReadPrivateExtended,
    BaseReadPublic,
    BaseReadPublicExtended,
)
from pydantic import BaseModel, Field, validator

from fed_reg.crud import ModelType

ReadPrivateSchemaType = TypeVar("ReadPrivateSchemaType", bound=BaseReadPrivate)
ReadPublicSchemaType = TypeVar("ReadPublicSchemaType", bound=BaseReadPublic)
ReadPrivateExtendedSchemaType = TypeVar(
    "ReadPrivateExtendedSchemaType", bound=BaseReadPrivateExtended
)
ReadPublicExtendedSchemaType = TypeVar(
    "ReadPublicExtendedSchemaType", bound=BaseReadPublicExtended
)


class SchemaShape(BaseModel):
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
        size (int): Chunk size.
    """

    size: int = Field(default=0, ge=1, description="Chunk size.")
    page: int = Field(default=0, ge=0, description="Divide the list in chunks")

    @validator("page", pre=True)
    @classmethod
    def set_page_to_0(cls, v: int, values: dict[str, Any]) -> int:
        """If chunk size is 0 set page index to 0."""
        if values.get("size", 0) == 0:
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
    limit: int | None = Field(
        default=None, ge=0, description="Maximum number or returned items."
    )
    sort: str | None = Field(default=None, description="Sorting rule.")

    @validator("sort")
    @classmethod
    def parse_sort_rule(cls, v: str | None) -> str | None:
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


def paginate(*, items: list[Any], page: int, size: int = 0) -> list[Any]:
    """Divide the list in chunks.

    Args:
    ----
        items (list[Any]): list of items to split.
        page (int): Target chunk (start from 0).
        size (int): Chunk size.

    Returns:
    -------
        list[Any]. Chunk with index equal to page and length equal to, at
        most, size.
    """
    if size is None:
        return items
    start = page * size
    end = start + size
    return items[start:end]


def choose_out_schema(
    *,
    items: list[ModelType] | ModelType,
    auth: bool,
    with_conn: bool,
    short: bool,
    read_private_schema: ReadPrivateSchemaType,
    read_private_extended_schema: ReadPrivateExtendedSchemaType,
    read_public_schema: ReadPublicSchemaType,
    read_public_extended_schema: ReadPublicExtendedSchemaType,
) -> (
    list[ReadPrivateSchemaType]
    | list[ReadPrivateExtendedSchemaType]
    | list[ReadPublicSchemaType]
    | list[ReadPublicExtendedSchemaType]
    | ReadPrivateSchemaType
    | ReadPrivateExtendedSchemaType
    | ReadPublicSchemaType
    | ReadPublicExtendedSchemaType
):
    """Choose which read model use to return data to users.

    Based on authorization, and on the user request to retrieve linked items, choose
    one of the read schemas.

    Args:
    ----
        items (list[ModelType]): list of items to cast.
        auth (bool): Flag for authorization.
        with_conn (bool): Flag to retrieve linked items.
        short (bool): Only for authenticated users: show shrunk version (public).

    Returns:
    -------
        list[ReadPublicSchemaType] | list[ReadSchemaType] |
        list[ReadExtendedPublicSchemaType] | list[ReadExtendedSchemaType].
    """
    single_item = False
    if not isinstance(items, list):
        single_item = True
        items = [items]

    if auth:
        if short:
            if with_conn:
                items = [read_public_extended_schema.from_orm(i) for i in items]
            else:
                items = [read_public_schema.from_orm(i) for i in items]
        else:
            if with_conn:
                items = [read_private_extended_schema.from_orm(i) for i in items]
            else:
                items = [read_private_schema.from_orm(i) for i in items]
    else:
        if with_conn:
            items = [read_public_extended_schema.from_orm(i) for i in items]
        else:
            items = [read_public_schema.from_orm(i) for i in items]

    return items[0] if single_item else items
