"""Network REST API utils."""

from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.network.schemas import NetworkRead, NetworkReadPublic
from fedreg.network.schemas_extended import (
    NetworkReadExtended,
    NetworkReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class NetworkReadSingle(BaseModel):
    __root__: (
        NetworkReadExtended
        | NetworkRead
        | NetworkReadExtendedPublic
        | NetworkReadPublic
    ) = Field(..., discriminator="schema_type")


class NetworkReadMulti(BaseModel):
    __root__: (
        list[NetworkReadExtended]
        | list[NetworkRead]
        | list[NetworkReadExtendedPublic]
        | list[NetworkReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[PrivateNetwork | SharedNetwork],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[NetworkRead]
    | list[NetworkReadPublic]
    | list[NetworkReadExtended]
    | list[NetworkReadExtendedPublic]
    | NetworkRead
    | NetworkReadPublic
    | NetworkReadExtended
    | NetworkReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=NetworkRead,
        read_public_schema=NetworkReadPublic,
        read_private_extended_schema=NetworkReadExtended,
        read_public_extended_schema=NetworkReadExtendedPublic,
    )
