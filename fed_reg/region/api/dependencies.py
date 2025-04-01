"""Region REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.region.models import Region
from fedreg.region.schemas import RegionUpdate

from fed_reg.dependencies import valid_id
from fed_reg.provider.api.dependencies import provider_must_exist
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
    if new_data.name != item.name:
        provider = provider_must_exist(item.provider.uid)
        db_item = provider.regions.get_or_none(name=new_data.name)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Region with name '{item.name}' already registered",
            )
    return item, new_data


def not_last_region(item: Annotated[Region, Depends(get_region_item)]) -> Region:
    """Check parent provider has other regions."""
    if item is not None:
        db_provider: Region = item.provider.single()
        if len(db_provider.regions) == 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"This region is the provider's {db_provider.uid} last one.",
            )
    return item
