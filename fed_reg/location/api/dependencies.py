"""Location REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.location.models import Location
from fedreg.location.schemas import LocationUpdate

from fed_reg.dependencies import valid_id
from fed_reg.location.crud import location_mgr


def location_must_exist(location_uid: str) -> Location:
    """The target location must exists otherwise raises `not found` error."""
    return valid_id(mgr=location_mgr, item_id=location_uid)


def get_location_item(location_uid: str) -> Location:
    """Retrieve the target location. If not found, return None."""
    return valid_id(mgr=location_mgr, item_id=location_uid, error=False)


def validate_new_location_values(
    item: Annotated[Location, Depends(location_must_exist)],
    new_data: LocationUpdate,
) -> tuple[Location, LocationUpdate]:
    """Check given data are valid ones.

    Check there are no other locations with the same site name. Avoid to change
    location visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical site name already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.site != item.site:
        db_item = location_mgr.get(site=new_data.site)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Location with site '{item.site}' already registered",
            )
    return item, new_data
