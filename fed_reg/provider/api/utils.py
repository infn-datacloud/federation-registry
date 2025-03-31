"""Provider REST API utils."""

from fedreg.provider.models import Provider
from fedreg.provider.schemas import ProviderRead, ProviderReadPublic
from fedreg.provider.schemas_extended import (
    ProviderReadExtended,
    ProviderReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class ProviderReadSingle(BaseModel):
    __root__: (
        ProviderReadExtended
        | ProviderRead
        | ProviderReadExtendedPublic
        | ProviderReadPublic
    ) = Field(..., discriminator="schema_type")


class ProviderReadMulti(BaseModel):
    __root__: (
        list[ProviderReadExtended]
        | list[ProviderRead]
        | list[ProviderReadExtendedPublic]
        | list[ProviderReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[Provider],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[ProviderRead]
    | list[ProviderReadPublic]
    | list[ProviderReadExtended]
    | list[ProviderReadExtendedPublic]
    | ProviderRead
    | ProviderReadPublic
    | ProviderReadExtended
    | ProviderReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ProviderRead,
        read_public_schema=ProviderReadPublic,
        read_private_extended_schema=ProviderReadExtended,
        read_public_extended_schema=ProviderReadExtendedPublic,
    )
