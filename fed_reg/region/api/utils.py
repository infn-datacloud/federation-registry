"""Region REST API utils."""

from fedreg.region.models import Region
from fedreg.region.schemas import RegionRead, RegionReadPublic
from fedreg.region.schemas_extended import RegionReadExtended, RegionReadExtendedPublic
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class RegionReadSingle(BaseModel):
    __root__: (
        RegionReadExtended | RegionRead | RegionReadExtendedPublic | RegionReadPublic
    ) = Field(..., discriminator="schema_type")


class RegionReadMulti(BaseModel):
    __root__: (
        list[RegionReadExtended]
        | list[RegionRead]
        | list[RegionReadExtendedPublic]
        | list[RegionReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[Region],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[RegionRead]
    | list[RegionReadPublic]
    | list[RegionReadExtended]
    | list[RegionReadExtendedPublic]
    | RegionRead
    | RegionReadPublic
    | RegionReadExtended
    | RegionReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=RegionRead,
        read_public_schema=RegionReadPublic,
        read_private_extended_schema=RegionReadExtended,
        read_public_extended_schema=RegionReadExtendedPublic,
    )
