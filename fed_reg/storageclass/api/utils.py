"""StorageClass REST API utils."""

from fedreg.storageclass.models import StorageClass
from fedreg.storageclass.schemas import StorageClassRead, StorageClassReadPublic
from fedreg.storageclass.schemas_extended import (
    StorageClassReadExtended,
    StorageClassReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class StorageClassReadSingle(BaseModel):
    __root__: (
        StorageClassReadExtended
        | StorageClassRead
        | StorageClassReadExtendedPublic
        | StorageClassReadPublic
    ) = Field(..., discriminator="schema_type")


class StorageClassReadMulti(BaseModel):
    __root__: (
        list[StorageClassReadExtended]
        | list[StorageClassRead]
        | list[StorageClassReadExtendedPublic]
        | list[StorageClassReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[StorageClass],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[StorageClassRead]
    | list[StorageClassReadPublic]
    | list[StorageClassReadExtended]
    | list[StorageClassReadExtendedPublic]
    | StorageClassRead
    | StorageClassReadPublic
    | StorageClassReadExtended
    | StorageClassReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=StorageClassRead,
        read_public_schema=StorageClassReadPublic,
        read_private_extended_schema=StorageClassReadExtended,
        read_public_extended_schema=StorageClassReadExtendedPublic,
    )
