"""Network REST API dependencies."""

from fastapi import Depends, HTTPException, status

from fed_reg.network.crud import network_mgr
from fed_reg.network.models import Network
from fed_reg.network.schemas import (
    NetworkUpdate,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from fed_reg.service.api.dependencies import valid_network_service_id
from fed_reg.service.models import NetworkService


def valid_network_id(network_uid: str) -> Network:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        network_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Network: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = network_mgr.get(uid=network_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network '{network_uid}' not found",
        )
    return item


def valid_network_uuid(
    item: PrivateNetworkCreate | SharedNetworkCreate | NetworkUpdate,
    service: NetworkService = Depends(valid_network_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other networks, belonging to the same service, with the same
    uuid.

    Args:
    ----
        item (PrivateNetworkCreate | SharedNetworkCreate | NetworkUpdate): new data.
        service (NetworkService): Service to inspect.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical uuid,
            belonging to the same service, already exists.
    """
    service = valid_network_service_id(service.uid)
    db_item = service.networks.get_or_none(uuid=item.uuid)
    if db_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Network with uuid '{item.uuid}' already registered",
        )


def validate_new_network_values(
    update_data: NetworkUpdate, item: Network = Depends(valid_network_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other networks, belonging to the same service, with the same uuid
    and name.

    Args:
    ----
        update_data (NetworkUpdate): new data.
        item (Network): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    if update_data.uuid != item.uuid:
        valid_network_uuid(item=update_data, service=item.service.single())
    if update_data.is_shared != item.is_shared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Network visibility can't be changed",
        )


def is_private_network(item: Network = Depends(valid_network_id)) -> Network:
    """Check given network has private or shared visibility.

    Args:
    ----
        item (Network): entity to validate.

    Returns:
    -------
        Network: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity has not valid visibility
    """
    if item.is_shared:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Network {item.uid} is a public network",
        )
    return item
