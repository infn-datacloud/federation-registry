"""Flavor REST API utils."""

from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fedreg.service.schemas import (
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    IdentityServiceRead,
    IdentityServiceReadPublic,
    NetworkServiceRead,
    NetworkServiceReadPublic,
    ObjectStoreServiceRead,
    ObjectStoreServiceReadPublic,
)
from fedreg.service.schemas_extended import (
    BlockStorageServiceReadExtended,
    BlockStorageServiceReadExtendedPublic,
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    IdentityServiceReadExtended,
    IdentityServiceReadExtendedPublic,
    NetworkServiceReadExtended,
    NetworkServiceReadExtendedPublic,
    ObjectStoreServiceReadExtended,
    ObjectStoreServiceReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class BlockStorageServiceReadSingle(BaseModel):
    __root__: (
        BlockStorageServiceReadExtended
        | BlockStorageServiceRead
        | BlockStorageServiceReadExtendedPublic
        | BlockStorageServiceReadPublic
    ) = Field(..., discriminator="schema_type")


class BlockStorageServiceReadMulti(BaseModel):
    __root__: (
        list[BlockStorageServiceReadExtended]
        | list[BlockStorageServiceRead]
        | list[BlockStorageServiceReadExtendedPublic]
        | list[BlockStorageServiceReadPublic]
    ) = Field(..., discriminator="schema_type")


class ComputeServiceReadSingle(BaseModel):
    __root__: (
        ComputeServiceReadExtended
        | ComputeServiceRead
        | ComputeServiceReadExtendedPublic
        | ComputeServiceReadPublic
    ) = Field(..., discriminator="schema_type")


class ComputeServiceReadMulti(BaseModel):
    __root__: (
        list[ComputeServiceReadExtended]
        | list[ComputeServiceRead]
        | list[ComputeServiceReadExtendedPublic]
        | list[ComputeServiceReadPublic]
    ) = Field(..., discriminator="schema_type")


class IdentityServiceReadSingle(BaseModel):
    __root__: (
        IdentityServiceReadExtended
        | IdentityServiceRead
        | IdentityServiceReadExtendedPublic
        | IdentityServiceReadPublic
    ) = Field(..., discriminator="schema_type")


class IdentityServiceReadMulti(BaseModel):
    __root__: (
        list[IdentityServiceReadExtended]
        | list[IdentityServiceRead]
        | list[IdentityServiceReadExtendedPublic]
        | list[IdentityServiceReadPublic]
    ) = Field(..., discriminator="schema_type")


class NetworkServiceReadSingle(BaseModel):
    __root__: (
        NetworkServiceReadExtended
        | NetworkServiceRead
        | NetworkServiceReadExtendedPublic
        | NetworkServiceReadPublic
    ) = Field(..., discriminator="schema_type")


class NetworkServiceReadMulti(BaseModel):
    __root__: (
        list[NetworkServiceReadExtended]
        | list[NetworkServiceRead]
        | list[NetworkServiceReadExtendedPublic]
        | list[NetworkServiceReadPublic]
    ) = Field(..., discriminator="schema_type")


class ObjectStoreServiceReadSingle(BaseModel):
    __root__: (
        ObjectStoreServiceReadExtended
        | ObjectStoreServiceRead
        | ObjectStoreServiceReadExtendedPublic
        | ObjectStoreServiceReadPublic
    ) = Field(..., discriminator="schema_type")


class ObjectStoreServiceReadMulti(BaseModel):
    __root__: (
        list[ObjectStoreServiceReadExtended]
        | list[ObjectStoreServiceRead]
        | list[ObjectStoreServiceReadExtendedPublic]
        | list[ObjectStoreServiceReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_block_storage_schema(
    items: list[BlockStorageService], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[BlockStorageServiceRead]
    | list[BlockStorageServiceReadPublic]
    | list[BlockStorageServiceReadExtended]
    | list[BlockStorageServiceReadExtendedPublic]
    | BlockStorageServiceRead
    | BlockStorageServiceReadPublic
    | BlockStorageServiceReadExtended
    | BlockStorageServiceReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=BlockStorageServiceRead,
        read_public_schema=BlockStorageServiceReadPublic,
        read_private_extended_schema=BlockStorageServiceReadExtended,
        read_public_extended_schema=BlockStorageServiceReadExtendedPublic,
    )


def choose_compute_schema(
    items: list[ComputeService], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[ComputeServiceRead]
    | list[ComputeServiceReadPublic]
    | list[ComputeServiceReadExtended]
    | list[ComputeServiceReadExtendedPublic]
    | ComputeServiceRead
    | ComputeServiceReadPublic
    | ComputeServiceReadExtended
    | ComputeServiceReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ComputeServiceRead,
        read_public_schema=ComputeServiceReadPublic,
        read_private_extended_schema=ComputeServiceReadExtended,
        read_public_extended_schema=ComputeServiceReadExtendedPublic,
    )


def choose_identity_schema(
    items: list[IdentityService], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[IdentityServiceRead]
    | list[IdentityServiceReadPublic]
    | list[IdentityServiceReadExtended]
    | list[IdentityServiceReadExtendedPublic]
    | IdentityServiceRead
    | IdentityServiceReadPublic
    | IdentityServiceReadExtended
    | IdentityServiceReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=IdentityServiceRead,
        read_public_schema=IdentityServiceReadPublic,
        read_private_extended_schema=IdentityServiceReadExtended,
        read_public_extended_schema=IdentityServiceReadExtendedPublic,
    )


def choose_network_schema(
    items: list[NetworkService], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[NetworkServiceRead]
    | list[NetworkServiceReadPublic]
    | list[NetworkServiceReadExtended]
    | list[NetworkServiceReadExtendedPublic]
    | NetworkServiceRead
    | NetworkServiceReadPublic
    | NetworkServiceReadExtended
    | NetworkServiceReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=NetworkServiceRead,
        read_public_schema=NetworkServiceReadPublic,
        read_private_extended_schema=NetworkServiceReadExtended,
        read_public_extended_schema=NetworkServiceReadExtendedPublic,
    )


def choose_object_store_schema(
    items: list[ObjectStoreService], *, auth: bool, with_conn: bool, short: bool
) -> (
    list[ObjectStoreServiceRead]
    | list[ObjectStoreServiceReadPublic]
    | list[ObjectStoreServiceReadExtended]
    | list[ObjectStoreServiceReadExtendedPublic]
    | ObjectStoreServiceRead
    | ObjectStoreServiceReadPublic
    | ObjectStoreServiceReadExtended
    | ObjectStoreServiceReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ObjectStoreServiceRead,
        read_public_schema=ObjectStoreServiceReadPublic,
        read_private_extended_schema=ObjectStoreServiceReadExtended,
        read_public_extended_schema=ObjectStoreServiceReadExtendedPublic,
    )
