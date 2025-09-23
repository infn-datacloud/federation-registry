"""Quota REST API utils."""

from typing import Annotated

from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    StorageClassQuota,
)
from fedreg.quota.schemas import (
    BlockStorageQuotaRead,
    BlockStorageQuotaReadPublic,
    ComputeQuotaRead,
    ComputeQuotaReadPublic,
    NetworkQuotaRead,
    NetworkQuotaReadPublic,
    ObjectStoreQuotaRead,
    ObjectStoreQuotaReadPublic,
    StorageClassQuotaRead,
    StorageClassQuotaReadPublic,
)
from fedreg.quota.schemas_extended import (
    BlockStorageQuotaReadExtended,
    BlockStorageQuotaReadExtendedPublic,
    ComputeQuotaReadExtended,
    ComputeQuotaReadExtendedPublic,
    NetworkQuotaReadExtended,
    NetworkQuotaReadExtendedPublic,
    ObjectStoreQuotaReadExtended,
    ObjectStoreQuotaReadExtendedPublic,
    StorageClassQuotaReadExtended,
    StorageClassQuotaReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class BlockStorageQuotaReadSingle(BaseModel):
    __root__: (
        BlockStorageQuotaReadExtended
        | BlockStorageQuotaRead
        | BlockStorageQuotaReadExtendedPublic
        | BlockStorageQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class BlockStorageQuotaReadMulti(BaseModel):
    __root__: (
        list[BlockStorageQuotaReadExtended]
        | list[BlockStorageQuotaRead]
        | list[BlockStorageQuotaReadExtendedPublic]
        | list[BlockStorageQuotaReadPublic]
    ) = Field(..., discriminator="schema_type")


class ComputeQuotaReadSingle(BaseModel):
    __root__: (
        ComputeQuotaReadExtended
        | ComputeQuotaRead
        | ComputeQuotaReadExtendedPublic
        | ComputeQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class ComputeQuotaReadMulti(BaseModel):
    __root__: (
        list[ComputeQuotaReadExtended]
        | list[ComputeQuotaRead]
        | list[ComputeQuotaReadExtendedPublic]
        | list[ComputeQuotaReadPublic]
    ) = Field(..., discriminator="schema_type")


class NetworkQuotaReadSingle(BaseModel):
    __root__: (
        NetworkQuotaReadExtended
        | NetworkQuotaRead
        | NetworkQuotaReadExtendedPublic
        | NetworkQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class NetworkQuotaReadMulti(BaseModel):
    __root__: (
        list[NetworkQuotaReadExtended]
        | list[NetworkQuotaRead]
        | list[NetworkQuotaReadExtendedPublic]
        | list[NetworkQuotaReadPublic]
    ) = Field(..., discriminator="schema_type")


class ObjectStoreQuotaReadSingle(BaseModel):
    __root__: (
        ObjectStoreQuotaReadExtended
        | ObjectStoreQuotaRead
        | ObjectStoreQuotaReadExtendedPublic
        | ObjectStoreQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class ObjectStoreQuotaReadMulti(BaseModel):
    __root__: (
        list[ObjectStoreQuotaReadExtended]
        | list[ObjectStoreQuotaRead]
        | list[ObjectStoreQuotaReadExtendedPublic]
        | list[ObjectStoreQuotaReadPublic]
    ) = Field(..., discriminator="schema_type")


StorageClassQuotaReadSingle = Annotated[
    ObjectStoreQuotaReadExtended
    | ObjectStoreQuotaRead
    | ObjectStoreQuotaReadExtendedPublic
    | ObjectStoreQuotaReadPublic,
    Field(discriminator="schema_type"),
]


StorageClassQuotaReadMulti = Annotated[
    list[ObjectStoreQuotaReadExtended]
    | list[ObjectStoreQuotaRead]
    | list[ObjectStoreQuotaReadExtendedPublic]
    | list[ObjectStoreQuotaReadPublic],
    Field(discriminator="schema_type"),
]


def choose_block_storage_schema(
    items: list[BlockStorageQuota], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[BlockStorageQuotaRead]
    | list[BlockStorageQuotaReadPublic]
    | list[BlockStorageQuotaReadExtended]
    | list[BlockStorageQuotaReadExtendedPublic]
    | BlockStorageQuotaRead
    | BlockStorageQuotaReadPublic
    | BlockStorageQuotaReadExtended
    | BlockStorageQuotaReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=BlockStorageQuotaRead,
        read_public_schema=BlockStorageQuotaReadPublic,
        read_private_extended_schema=BlockStorageQuotaReadExtended,
        read_public_extended_schema=BlockStorageQuotaReadExtendedPublic,
    )


def choose_compute_schema(
    items: list[ComputeQuota], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[ComputeQuotaRead]
    | list[ComputeQuotaReadPublic]
    | list[ComputeQuotaReadExtended]
    | list[ComputeQuotaReadExtendedPublic]
    | ComputeQuotaRead
    | ComputeQuotaReadPublic
    | ComputeQuotaReadExtended
    | ComputeQuotaReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ComputeQuotaRead,
        read_public_schema=ComputeQuotaReadPublic,
        read_private_extended_schema=ComputeQuotaReadExtended,
        read_public_extended_schema=ComputeQuotaReadExtendedPublic,
    )


def choose_network_schema(
    items: list[NetworkQuota], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[NetworkQuotaRead]
    | list[NetworkQuotaReadPublic]
    | list[NetworkQuotaReadExtended]
    | list[NetworkQuotaReadExtendedPublic]
    | NetworkQuotaRead
    | NetworkQuotaReadPublic
    | NetworkQuotaReadExtended
    | NetworkQuotaReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=NetworkQuotaRead,
        read_public_schema=NetworkQuotaReadPublic,
        read_private_extended_schema=NetworkQuotaReadExtended,
        read_public_extended_schema=NetworkQuotaReadExtendedPublic,
    )


def choose_object_store_schema(
    items: list[ObjectStoreQuota], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[ObjectStoreQuotaRead]
    | list[ObjectStoreQuotaReadPublic]
    | list[ObjectStoreQuotaReadExtended]
    | list[ObjectStoreQuotaReadExtendedPublic]
    | ObjectStoreQuotaRead
    | ObjectStoreQuotaReadPublic
    | ObjectStoreQuotaReadExtended
    | ObjectStoreQuotaReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ObjectStoreQuotaRead,
        read_public_schema=ObjectStoreQuotaReadPublic,
        read_private_extended_schema=ObjectStoreQuotaReadExtended,
        read_public_extended_schema=ObjectStoreQuotaReadExtendedPublic,
    )


def choose_storage_class_schema(
    items: list[StorageClassQuota], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[StorageClassQuotaRead]
    | list[StorageClassQuotaReadPublic]
    | list[StorageClassQuotaReadExtended]
    | list[StorageClassQuotaReadExtendedPublic]
    | StorageClassQuotaRead
    | StorageClassQuotaReadPublic
    | StorageClassQuotaReadExtended
    | StorageClassQuotaReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=StorageClassQuotaRead,
        read_public_schema=StorageClassQuotaReadPublic,
        read_private_extended_schema=StorageClassQuotaReadExtended,
        read_public_extended_schema=StorageClassQuotaReadExtendedPublic,
    )
