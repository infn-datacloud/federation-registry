"""Service REST API dependencies."""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fedreg.service.schemas import (
    BlockStorageServiceUpdate,
    ComputeServiceUpdate,
    IdentityServiceUpdate,
    NetworkServiceUpdate,
    ObjectStoreServiceUpdate,
)

from fed_reg.dependencies import valid_id
from fed_reg.service.crud import (
    block_storage_service_mng,
    compute_service_mng,
    identity_service_mng,
    network_service_mng,
    object_store_service_mng,
)


def block_storage_service_must_exist(service_uid: str) -> BlockStorageService:
    """The target service must exists otherwise raises `not found` error."""
    return valid_id(mgr=block_storage_service_mng, item_id=service_uid)


def get_block_storage_service_item(service_uid: str) -> BlockStorageService:
    """Retrieve the target service. If not found, return None."""
    return valid_id(mgr=block_storage_service_mng, item_id=service_uid, error=False)


def validate_new_block_storage_service_values(
    item: Annotated[BlockStorageService, Depends(block_storage_service_must_exist)],
    new_data: BlockStorageServiceUpdate,
) -> tuple[BlockStorageService, BlockStorageServiceUpdate]:
    """Check given data are valid ones."""
    return validate_new_service_values(
        mgr=block_storage_service_mng, item=item, new_data=new_data
    )


def compute_service_must_exist(service_uid: str) -> ComputeService:
    """The target service must exists otherwise raises `not found` error."""
    return valid_id(mgr=compute_service_mng, item_id=service_uid)


def get_compute_service_item(service_uid: str) -> ComputeService:
    """Retrieve the target service. If not found, return None."""
    return valid_id(mgr=compute_service_mng, item_id=service_uid, error=False)


def validate_new_compute_service_values(
    item: Annotated[ComputeService, Depends(compute_service_must_exist)],
    new_data: ComputeServiceUpdate,
) -> tuple[ComputeService, ComputeServiceUpdate]:
    """Check given data are valid ones."""
    return validate_new_service_values(
        mgr=compute_service_mng, item=item, new_data=new_data
    )


def identity_service_must_exist(service_uid: str) -> IdentityService:
    """The target service must exists otherwise raises `not found` error."""
    return valid_id(mgr=identity_service_mng, item_id=service_uid)


def get_identity_service_item(service_uid: str) -> IdentityService:
    """Retrieve the target service. If not found, return None."""
    return valid_id(mgr=identity_service_mng, item_id=service_uid, error=False)


def validate_new_identity_service_values(
    item: Annotated[IdentityService, Depends(identity_service_must_exist)],
    new_data: IdentityServiceUpdate,
) -> tuple[IdentityService, IdentityServiceUpdate]:
    """Check given data are valid ones."""
    return validate_new_service_values(
        mgr=identity_service_mng, item=item, new_data=new_data
    )


def network_service_must_exist(service_uid: str) -> NetworkService:
    """The target service must exists otherwise raises `not found` error."""
    return valid_id(mgr=network_service_mng, item_id=service_uid)


def get_network_service_item(service_uid: str) -> NetworkService:
    """Retrieve the target service. If not found, return None."""
    return valid_id(mgr=network_service_mng, item_id=service_uid, error=False)


def validate_new_network_service_values(
    item: Annotated[NetworkService, Depends(network_service_must_exist)],
    new_data: NetworkServiceUpdate,
) -> tuple[NetworkService, NetworkServiceUpdate]:
    """Check given data are valid ones."""
    return validate_new_service_values(
        mgr=network_service_mng, item=item, new_data=new_data
    )


def object_store_service_must_exist(service_uid: str) -> ObjectStoreService:
    """The target service must exists otherwise raises `not found` error."""
    return valid_id(mgr=object_store_service_mng, item_id=service_uid)


def get_object_store_service_item(service_uid: str) -> ObjectStoreService:
    """Retrieve the target service. If not found, return None."""
    return valid_id(mgr=object_store_service_mng, item_id=service_uid, error=False)


def validate_new_object_store_service_values(
    item: Annotated[ObjectStoreService, Depends(object_store_service_must_exist)],
    new_data: ObjectStoreServiceUpdate,
) -> tuple[ObjectStoreService, ObjectStoreServiceUpdate]:
    """Check given data are valid ones."""
    return validate_new_service_values(
        mgr=object_store_service_mng, item=item, new_data=new_data
    )


def validate_new_service_values(
    mgr: Any,
    item: BlockStorageService
    | ComputeService
    | IdentityService
    | NetworkService
    | ObjectStoreService,
    new_data: BlockStorageServiceUpdate
    | ComputeServiceUpdate
    | IdentityService
    | NetworkServiceUpdate
    | ObjectStoreServiceUpdate,
) -> (
    tuple[BlockStorageService, BlockStorageServiceUpdate]
    | tuple[ComputeService, ComputeServiceUpdate]
    | tuple[IdentityService, IdentityServiceUpdate]
    | tuple[NetworkService, NetworkServiceUpdate]
    | tuple[ObjectStoreService, ObjectStoreServiceUpdate]
):
    """Check given data are valid ones.

    Check there are no other services with the same site name. Avoid to change
    service visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid, belonging to the same
    provider, already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.endpoint is not None and str(new_data.endpoint) != item.endpoint:
        db_item = mgr.get(endpoint=item.endpoint)
        if db_item is not None:
            msg = f"{mgr.model} with endpoint '{item.endpoint}' already registered."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    return item, new_data
