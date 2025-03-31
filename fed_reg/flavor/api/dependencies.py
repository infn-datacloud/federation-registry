"""Flavor REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.flavor.schemas import FlavorUpdate

from fed_reg.dependencies import valid_id
from fed_reg.flavor.crud import flavor_mgr
from fed_reg.service.api.dependencies import compute_service_must_exist


def flavor_must_exist(flavor_uid: str) -> PrivateFlavor | SharedFlavor:
    """The target flavor must exists otherwise raises `not found` error."""
    return valid_id(mgr=flavor_mgr, item_id=flavor_uid)


def get_flavor_item(flavor_uid: str) -> PrivateFlavor | SharedFlavor:
    """Retrieve the target flavor. If not found, return None."""
    return valid_id(mgr=flavor_mgr, item_id=flavor_uid, error=False)


def validate_new_flavor_values(
    item: Annotated[PrivateFlavor | SharedFlavor, Depends(flavor_must_exist)],
    new_data: FlavorUpdate,
) -> tuple[PrivateFlavor | SharedFlavor, FlavorUpdate]:
    """Check given data are valid ones.

    Check there are no other flavors, belonging to the same service, with the same uuid
    and name. Avoid to change flavor visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid and belonging to the
    same service already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.uuid != item.uuid:
        for service in item.services:
            service = compute_service_must_exist(service.uid)
            db_item = service.flavors.get_or_none(uuid=new_data.uuid)
            if db_item is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Flavor with uuid '{item.uuid}' already registered",
                )
    return item, new_data
