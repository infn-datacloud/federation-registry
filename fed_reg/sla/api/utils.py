"""SLA REST API utils."""

from fedreg.sla.models import SLA
from fedreg.sla.schemas import SLARead, SLAReadPublic
from fedreg.sla.schemas_extended import SLAReadExtended, SLAReadExtendedPublic
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class SLAReadSingle(BaseModel):
    __root__: SLAReadExtended | SLARead | SLAReadExtendedPublic | SLAReadPublic = Field(
        ..., discriminator="schema_type"
    )


class SLAReadMulti(BaseModel):
    __root__: (
        list[SLAReadExtended]
        | list[SLARead]
        | list[SLAReadExtendedPublic]
        | list[SLAReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[SLA],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[SLARead]
    | list[SLAReadPublic]
    | list[SLAReadExtended]
    | list[SLAReadExtendedPublic]
    | SLARead
    | SLAReadPublic
    | SLAReadExtended
    | SLAReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=SLARead,
        read_public_schema=SLAReadPublic,
        read_private_extended_schema=SLAReadExtended,
        read_public_extended_schema=SLAReadExtendedPublic,
    )
