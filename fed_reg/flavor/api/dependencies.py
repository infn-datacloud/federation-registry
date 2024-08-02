"""Flavor REST API dependencies."""
from fastapi import Depends, HTTPException, status

from fed_reg.flavor.crud import flavor_mng
from fed_reg.flavor.models import Flavor
from fed_reg.flavor.schemas import FlavorUpdate, PrivateFlavorCreate, SharedFlavorCreate
from fed_reg.service.api.dependencies import valid_compute_service_id
from fed_reg.service.models import ComputeService


def valid_flavor_id(flavor_uid: str) -> Flavor:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        flavor_uid (str): uid of the target DB entity.

    Returns:
    -------
        Flavor: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = flavor_mng.get(uid=flavor_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flavor '{flavor_uid}' not found",
        )
    return item


def valid_flavor_name(
    item: PrivateFlavorCreate | SharedFlavorCreate | FlavorUpdate,
    services: list[ComputeService],
) -> None:
    """Check no duplicate name.

    Check there are no other flavors, belonging to the same service, with the same
    name.

    Args:
    ----
        item (PrivateFlavorCreate | SharedFlavorCreate | FlavorUpdate): new data.
        services (list of ComputeService): list of services to inspect.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical name,
            belonging to the same service, already exists.
    """
    for service in services:
        service = valid_compute_service_id(service.uid)
        db_item = service.flavors.get_or_none(name=item.name)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Flavor with name '{item.name}' already registered",
            )


def valid_flavor_uuid(
    item: PrivateFlavorCreate | SharedFlavorCreate | FlavorUpdate,
    services: list[ComputeService] = Depends(valid_compute_service_id),
) -> None:
    """Check no duplicate UUID.

    Check there are no other flavors, belonging to the same service, with the same
    uuid.

    Args:
    ----
        item (PrivateFlavorCreate | SharedFlavorCreate | FlavorUpdate): new data.
        services (list of ComputeService): list of services to inspect.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical uuid,
            belonging to the same service, already exists.
    """
    for service in services:
        service = valid_compute_service_id(service.uid)
        db_item = service.flavors.get_or_none(uuid=item.uuid)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Flavor with uuid '{item.uuid}' already registered",
            )


def validate_new_flavor_values(
    update_data: FlavorUpdate, item: Flavor = Depends(valid_flavor_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other flavors, belonging to the same service, with the same uuid
    and name. Avoid to change flavor visibility.

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
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    if update_data.name != item.name:
        valid_flavor_name(item=update_data, services=item.services.all())
    if update_data.uuid != item.uuid:
        valid_flavor_uuid(item=update_data, services=item.services.all())
    if update_data.is_public != item.is_public:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Flavor visibility can't be changed",
        )


def is_private_flavor(item: Flavor = Depends(valid_flavor_id)) -> Flavor:
    """Check given flavor has private or shared visibility.

    Args:
    ----
        item (Flavor): entity to validate.

    Returns:
    -------
        Flavor: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity has not valid visibility
    """
    if item.is_public:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Flavor {item.uid} is a public flavor",
        )
    return item
