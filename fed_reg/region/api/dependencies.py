"""Region REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.region.models import Region
from fedreg.region.schemas import RegionUpdate
from neomodel.exceptions import CardinalityViolation

from fed_reg.dependencies import valid_id
from fed_reg.region.crud import region_mgr


def region_must_exist(region_uid: str) -> Region:
    """The target region must exists otherwise raises `not found` error."""
    return valid_id(mgr=region_mgr, item_id=region_uid)


def get_region_item(region_uid: str) -> Region:
    """Retrieve the target region. If not found, return None."""
    return valid_id(mgr=region_mgr, item_id=region_uid, error=False)


def validate_new_region_values(
    item: Annotated[Region, Depends(region_must_exist)], new_data: RegionUpdate
) -> tuple[Region, RegionUpdate]:
    """Check given data are valid ones.

    Check there are no other regions with the same site name. Avoid to change
    region visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical site name already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.name is not None and new_data.name != item.name:
        try:
            provider = item.provider.single()
        except CardinalityViolation as e:
            msg = (
                f"Corrupted DB: Project with uuid '{item.uuid}' has no linked provider"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            ) from e
        db_item = provider.regions.get_or_none(name=new_data.name)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Region with name '{item.name}' already registered",
            )
    return item, new_data
