"""Quota REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fedreg.quota.schemas import (
    BlockStorageQuotaUpdate,
    ComputeQuotaUpdate,
    NetworkQuotaUpdate,
    ObjectStoreQuotaUpdate,
)

from fed_reg.dependencies import valid_id
from fed_reg.quota.crud import (
    block_storage_quota_mng,
    compute_quota_mng,
    network_quota_mng,
    object_store_quota_mng,
)


def block_storage_quota_must_exist(quota_uid: str) -> BlockStorageQuota:
    """The target quota must exists otherwise raises `not found` error."""
    return valid_id(mgr=block_storage_quota_mng, item_id=quota_uid)


def get_block_storage_quota_item(quota_uid: str) -> BlockStorageQuota:
    """Retrieve the target quota. If not found, return None."""
    return valid_id(mgr=block_storage_quota_mng, item_id=quota_uid, error=False)


def validate_new_block_storage_quota_values(
    item: Annotated[BlockStorageQuota, Depends(block_storage_quota_must_exist)],
    new_data: BlockStorageQuotaUpdate,
) -> tuple[BlockStorageQuota, BlockStorageQuotaUpdate]:
    """Check given data are valid ones."""
    return validate_new_quota_values(item=item, new_data=new_data)


def compute_quota_must_exist(quota_uid: str) -> ComputeQuota:
    """The target quota must exists otherwise raises `not found` error."""
    return valid_id(mgr=compute_quota_mng, item_id=quota_uid)


def get_compute_quota_item(quota_uid: str) -> ComputeQuota:
    """Retrieve the target quota. If not found, return None."""
    return valid_id(mgr=compute_quota_mng, item_id=quota_uid, error=False)


def validate_new_compute_quota_values(
    item: Annotated[ComputeQuota, Depends(compute_quota_must_exist)],
    new_data: ComputeQuotaUpdate,
) -> tuple[ComputeQuota, ComputeQuotaUpdate]:
    """Check given data are valid ones."""
    return validate_new_quota_values(item=item, new_data=new_data)


def network_quota_must_exist(quota_uid: str) -> NetworkQuota:
    """The target quota must exists otherwise raises `not found` error."""
    return valid_id(mgr=network_quota_mng, item_id=quota_uid)


def get_network_quota_item(quota_uid: str) -> NetworkQuota:
    """Retrieve the target quota. If not found, return None."""
    return valid_id(mgr=network_quota_mng, item_id=quota_uid, error=False)


def validate_new_network_quota_values(
    item: Annotated[NetworkQuota, Depends(network_quota_must_exist)],
    new_data: NetworkQuotaUpdate,
) -> tuple[NetworkQuota, NetworkQuotaUpdate]:
    """Check given data are valid ones."""
    return validate_new_quota_values(item=item, new_data=new_data)


def object_store_quota_must_exist(quota_uid: str) -> ObjectStoreQuota:
    """The target quota must exists otherwise raises `not found` error."""
    return valid_id(mgr=object_store_quota_mng, item_id=quota_uid)


def get_object_store_quota_item(quota_uid: str) -> ObjectStoreQuota:
    """Retrieve the target quota. If not found, return None."""
    return valid_id(mgr=object_store_quota_mng, item_id=quota_uid, error=False)


def validate_new_object_store_quota_values(
    item: Annotated[ObjectStoreQuota, Depends(object_store_quota_must_exist)],
    new_data: ObjectStoreQuotaUpdate,
) -> tuple[ObjectStoreQuota, ObjectStoreQuotaUpdate]:
    """Check given data are valid ones."""
    return validate_new_quota_values(item=item, new_data=new_data)


def validate_new_quota_values(
    item: BlockStorageQuota | ComputeQuota | NetworkQuota | ObjectStoreQuota,
    new_data: BlockStorageQuotaUpdate
    | ComputeQuotaUpdate
    | NetworkQuotaUpdate
    | ObjectStoreQuotaUpdate,
) -> (
    tuple[BlockStorageQuota, BlockStorageQuotaUpdate]
    | tuple[ComputeQuota, ComputeQuotaUpdate]
    | tuple[NetworkQuota, NetworkQuotaUpdate]
    | tuple[ObjectStoreQuota, ObjectStoreQuotaUpdate]
):
    """Check given data are valid ones.

    Check there are no other quotas with the same site name. Avoid to change
    quota visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid, belonging to the same
    provider, already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.per_user != item.per_user:
        db_project = item.project.single()
        db_service = item.service.single()
        proj_quotas = db_project.quotas.filter(
            type=new_data.type, per_user=new_data.per_user
        )
        serv_quotas = db_service.quotas.filter(per_user=new_data.per_user)
        serv_quotas_matching_proj = set([i.uid for i in proj_quotas]).intersection(
            set([i.uid for i in serv_quotas])
        )
        if len(serv_quotas_matching_proj) > 0:
            s = "" if new_data.per_user else "not"
            msg = f"Duplicated {type(item)}, to {s} apply to each user, on "
            msg += f"Project '{db_project.uid}' and Service {db_service.uid}"
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    return item, new_data
