"""Flavor REST API utils."""

from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.flavor.schemas import FlavorRead, FlavorReadPublic
from fedreg.flavor.schemas_extended import FlavorReadExtended, FlavorReadExtendedPublic
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class FlavorReadSingle(BaseModel):
    __root__: (
        FlavorReadExtended | FlavorRead | FlavorReadExtendedPublic | FlavorReadPublic
    ) = Field(..., discriminator="schema_type")


class FlavorReadMulti(BaseModel):
    __root__: (
        list[FlavorReadExtended]
        | list[FlavorRead]
        | list[FlavorReadExtendedPublic]
        | list[FlavorReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[PrivateFlavor | SharedFlavor],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[FlavorRead]
    | list[FlavorReadPublic]
    | list[FlavorReadExtended]
    | list[FlavorReadExtendedPublic]
    | FlavorRead
    | FlavorReadPublic
    | FlavorReadExtended
    | FlavorReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=FlavorRead,
        read_public_schema=FlavorReadPublic,
        read_private_extended_schema=FlavorReadExtended,
        read_public_extended_schema=FlavorReadExtendedPublic,
    )
