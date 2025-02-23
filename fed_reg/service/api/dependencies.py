"""Service REST API dependencies."""

from fastapi import Depends, HTTPException, status
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fedreg.service.schemas import (
    BlockStorageServiceCreate,
    BlockStorageServiceUpdate,
    ComputeServiceCreate,
    ComputeServiceUpdate,
    IdentityServiceCreate,
    IdentityServiceUpdate,
    NetworkServiceCreate,
    NetworkServiceUpdate,
    ObjectStoreServiceCreate,
    ObjectStoreServiceUpdate,
)

from fed_reg.service.crud import (
    block_storage_service_mng,
    compute_service_mng,
    identity_service_mng,
    network_service_mng,
    object_store_service_mng,
)


def valid_block_storage_service_id(
    service_uid: str,
) -> BlockStorageService:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        service_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = block_storage_service_mng.get(uid=service_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block Storage Service '{service_uid}' not found",
        )
    return item


def valid_block_storage_service_endpoint(
    item: BlockStorageServiceCreate | BlockStorageServiceUpdate,
) -> None:
    """Check there are no other services with the same endpoint.

    Args:
    ----
        item (ServiceCreate | ServiceUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given endpoint already exists.
    """
    db_item = block_storage_service_mng.get(endpoint=item.endpoint)
    if db_item is not None:
        msg = (
            f"Block Storage Service with endpoint '{item.endpoint}' already registered."
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def validate_new_block_storage_service_values(
    update_data: BlockStorageServiceUpdate,
    item: BlockStorageService = Depends(valid_block_storage_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other services with the same endpoint.

    Args:
    ----
        update_data (FlavorUpdate): new data.
        item (Flavor): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given endpoint already exists.
    """
    if str(update_data.endpoint) != item.endpoint:
        valid_block_storage_service_endpoint(update_data)


def valid_compute_service_id(
    service_uid: str,
) -> ComputeService:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        service_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = compute_service_mng.get(uid=service_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Compute Service '{service_uid}' not found",
        )
    return item


def valid_compute_service_endpoint(
    item: ComputeServiceCreate | ComputeServiceUpdate,
) -> None:
    """Check there are no other services with the same endpoint.

    Args:
    ----
        item (ServiceCreate | ServiceUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given endpoint already exists.
    """
    db_item = compute_service_mng.get(endpoint=item.endpoint)
    if db_item is not None:
        msg = f"Compute Service with endpoint '{item.endpoint}' already registered."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def validate_new_compute_service_values(
    update_data: ComputeServiceUpdate,
    item: ComputeService = Depends(valid_compute_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other services with the same endpoint.

    Args:
    ----
        update_data (FlavorUpdate): new data.
        item (Flavor): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given endpoint already exists.
    """
    if str(update_data.endpoint) != item.endpoint:
        valid_compute_service_endpoint(update_data)


def valid_identity_service_id(
    service_uid: str,
) -> IdentityService:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        service_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = identity_service_mng.get(uid=service_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Identity Service '{service_uid}' not found",
        )
    return item


def valid_identity_service_endpoint(
    item: IdentityServiceCreate | IdentityServiceUpdate,
) -> None:
    """Check there are no other services with the same endpoint.

    Args:
    ----
        item (ServiceCreate | ServiceUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given endpoint already exists.
    """
    db_item = identity_service_mng.get(endpoint=item.endpoint)
    if db_item is not None:
        msg = f"Identity Service with endpoint '{item.endpoint}' already registered."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def validate_new_identity_service_values(
    update_data: IdentityServiceUpdate,
    item: IdentityService = Depends(valid_identity_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other services with the same endpoint.

    Args:
    ----
        update_data (FlavorUpdate): new data.
        item (Flavor): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given endpoint already exists.
    """
    if str(update_data.endpoint) != item.endpoint:
        valid_identity_service_endpoint(update_data)


def valid_network_service_id(
    service_uid: str,
) -> NetworkService:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        service_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = network_service_mng.get(uid=service_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network Service '{service_uid}' not found",
        )
    return item


def valid_network_service_endpoint(
    item: NetworkServiceCreate | NetworkServiceUpdate,
) -> None:
    """Check there are no other services with the same endpoint.

    Args:
    ----
        item (ServiceCreate | ServiceUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given endpoint already exists.
    """
    db_item = network_service_mng.get(endpoint=item.endpoint)
    if db_item is not None:
        msg = f"Network Service with endpoint '{item.endpoint}' already registered."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def validate_new_network_service_values(
    update_data: NetworkServiceUpdate,
    item: NetworkService = Depends(valid_network_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other services with the same endpoint.

    Args:
    ----
        update_data (FlavorUpdate): new data.
        item (Flavor): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given endpoint already exists.
    """
    if str(update_data.endpoint) != item.endpoint:
        valid_network_service_endpoint(update_data)


def valid_object_store_service_id(
    service_uid: str,
) -> ObjectStoreService:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        service_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Service: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = object_store_service_mng.get(uid=service_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object Storage Service '{service_uid}' not found",
        )
    return item


def valid_object_store_service_endpoint(
    item: ObjectStoreServiceCreate | ObjectStoreServiceUpdate,
) -> None:
    """Check there are no other services with the same endpoint.

    Args:
    ----
        item (ServiceCreate | ServiceUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given endpoint already exists.
    """
    db_item = object_store_service_mng.get(endpoint=item.endpoint)
    if db_item is not None:
        msg = (
            "Object Storage Service with endpoint "
            + f"'{item.endpoint}' already registered."
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def validate_new_object_store_service_values(
    update_data: ObjectStoreServiceUpdate,
    item: ObjectStoreService = Depends(valid_object_store_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other services with the same endpoint.

    Args:
    ----
        update_data (FlavorUpdate): new data.
        item (Flavor): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given endpoint already exists.
    """
    if str(update_data.endpoint) != item.endpoint:
        valid_object_store_service_endpoint(update_data)
