"""Quota REST API dependencies."""
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

from fed_reg.quota.crud import (
    block_storage_quota_mng,
    compute_quota_mng,
    network_quota_mng,
    object_store_quota_mng,
)


def valid_block_storage_quota_id(quota_uid: str) -> BlockStorageQuota:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        quota_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = block_storage_quota_mng.get(uid=quota_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block Storage Quota '{quota_uid}' not found",
        )
    return item


def validate_new_block_storage_quota_values(
    update_data: BlockStorageQuotaUpdate,
    item: BlockStorageQuota = Depends(valid_block_storage_quota_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other quotas, belonging to the same project, with the same type
    and per_user flag, pointing to the same service.

    Args:
    ----
        update_data (BlockStorageQuotaUpdate): new data.
        item (BlockStorageQuota): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    if update_data.per_user != item.per_user:
        db_project = item.project.single()
        db_service = item.service.single()
        proj_quotas = db_project.quotas.filter(type=update_data.type)
        serv_quotas_matching_proj = db_service.quotas.filter(
            uid__in=[i.uid for i in proj_quotas], per_user=update_data.per_user
        )
        if len(serv_quotas_matching_proj.all()) > 0:
            s = "" if update_data.per_user else "not"
            msg = f"Duplicated Block Storage Quota, to {s} apply to each user, on "
            msg += f"Project '{db_project.uid}' and Service {db_service.uid}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def valid_compute_quota_id(quota_uid: str) -> ComputeQuota:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        quota_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = compute_quota_mng.get(uid=quota_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compute Quota '{quota_uid}' not found",
        )
    return item


def validate_new_compute_quota_values(
    update_data: ComputeQuotaUpdate,
    item: ComputeQuota = Depends(valid_compute_quota_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other quotas, belonging to the same project, with the same type
    and per_user flag, pointing to the same service.

    Args:
    ----
        update_data (ComputeQuotaUpdate): new data.
        item (ComputeQuota): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    if update_data.per_user != item.per_user:
        db_project = item.project.single()
        db_service = item.service.single()
        proj_quotas = db_project.quotas.filter(type=update_data.type)
        serv_quotas_matching_proj = db_service.quotas.filter(
            uid__in=[i.uid for i in proj_quotas], per_user=update_data.per_user
        )
        if len(serv_quotas_matching_proj.all()) > 0:
            s = "" if update_data.per_user else "not"
            msg = f"Duplicated Compute Quota, to {s} apply to each user, on "
            msg += f"Project '{db_project.uid}' and Service {db_service.uid}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def valid_network_quota_id(quota_uid: str) -> NetworkQuota:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        quota_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = network_quota_mng.get(uid=quota_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network Quota '{quota_uid}' not found",
        )
    return item


def validate_new_network_quota_values(
    update_data: NetworkQuotaUpdate,
    item: NetworkQuota = Depends(valid_network_quota_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other quotas, belonging to the same project, with the same type
    and per_user flag, pointing to the same service.

    Args:
    ----
        update_data (NetworkQuotaUpdate): new data.
        item (NetworkQuota): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    if update_data.per_user != item.per_user:
        db_project = item.project.single()
        db_service = item.service.single()
        proj_quotas = db_project.quotas.filter(type=update_data.type)
        serv_quotas_matching_proj = db_service.quotas.filter(
            uid__in=[i.uid for i in proj_quotas], per_user=update_data.per_user
        )
        if len(serv_quotas_matching_proj.all()) > 0:
            s = "" if update_data.per_user else "not"
            msg = f"Duplicated Network Quota, to {s} apply to each user, on "
            msg += f"Project '{db_project.uid}' and Service {db_service.uid}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def valid_object_store_quota_id(quota_uid: str) -> ObjectStoreQuota:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        quota_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = object_store_quota_mng.get(uid=quota_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object Storage Quota '{quota_uid}' not found",
        )
    return item


def validate_new_object_store_quota_values(
    update_data: ObjectStoreQuotaUpdate,
    item: ObjectStoreQuota = Depends(valid_object_store_quota_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other quotas, belonging to the same project, with the same type
    and per_user flag, pointing to the same service.

    Args:
    ----
        update_data (ObjectStoreQuotaUpdate): new data.
        item (ObjectStoreQuota): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    if update_data.per_user != item.per_user:
        db_project = item.project.single()
        db_service = item.service.single()
        proj_quotas = db_project.quotas.filter(type=update_data.type)
        serv_quotas_matching_proj = db_service.quotas.filter(
            uid__in=[i.uid for i in proj_quotas], per_user=update_data.per_user
        )
        if len(serv_quotas_matching_proj.all()) > 0:
            s = "" if update_data.per_user else "not"
            msg = f"Duplicated Object Storage Quota, to {s} apply to each user, on "
            msg += f"Project '{db_project.uid}' and Service {db_service.uid}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
