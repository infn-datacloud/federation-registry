"""Location REST API utils."""

from fedreg.location.models import Location
from fedreg.location.schemas import LocationRead, LocationReadPublic
from fedreg.location.schemas_extended import (
    LocationReadExtended,
    LocationReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class LocationReadSingle(BaseModel):
    __root__: (
        LocationReadExtended
        | LocationRead
        | LocationReadExtendedPublic
        | LocationReadPublic
    ) = Field(..., discriminator="schema_type")


class LocationReadMulti(BaseModel):
    __root__: (
        list[LocationReadExtended]
        | list[LocationRead]
        | list[LocationReadExtendedPublic]
        | list[LocationReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[Location],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[LocationRead]
    | list[LocationReadPublic]
    | list[LocationReadExtended]
    | list[LocationReadExtendedPublic]
    | LocationRead
    | LocationReadPublic
    | LocationReadExtended
    | LocationReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=LocationRead,
        read_public_schema=LocationReadPublic,
        read_private_extended_schema=LocationReadExtended,
        read_public_extended_schema=LocationReadExtendedPublic,
    )
