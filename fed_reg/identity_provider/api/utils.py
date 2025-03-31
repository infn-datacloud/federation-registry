"""IdentityProvider REST API utils."""

from fedreg.identity_provider.models import IdentityProvider
from fedreg.identity_provider.schemas import (
    IdentityProviderRead,
    IdentityProviderReadPublic,
)
from fedreg.identity_provider.schemas_extended import (
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class IdentityProviderReadSingle(BaseModel):
    __root__: (
        IdentityProviderReadExtended
        | IdentityProviderRead
        | IdentityProviderReadExtendedPublic
        | IdentityProviderReadPublic
    ) = Field(..., discriminator="schema_type")


class IdentityProviderReadMulti(BaseModel):
    __root__: (
        list[IdentityProviderReadExtended]
        | list[IdentityProviderRead]
        | list[IdentityProviderReadExtendedPublic]
        | list[IdentityProviderReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[IdentityProvider],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[IdentityProviderRead]
    | list[IdentityProviderReadPublic]
    | list[IdentityProviderReadExtended]
    | list[IdentityProviderReadExtendedPublic]
    | IdentityProviderRead
    | IdentityProviderReadPublic
    | IdentityProviderReadExtended
    | IdentityProviderReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=IdentityProviderRead,
        read_public_schema=IdentityProviderReadPublic,
        read_private_extended_schema=IdentityProviderReadExtended,
        read_public_extended_schema=IdentityProviderReadExtendedPublic,
    )
