"""Region REST API dependencies."""

from fastapi import Depends, HTTPException, status
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.region.schemas import RegionCreate, RegionUpdate

from fed_reg.provider.api.dependencies import valid_provider_id
from fed_reg.region.crud import region_mng


def valid_region_id(region_uid: str) -> Region:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        region_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Region: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = region_mng.get(uid=region_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region '{region_uid}' not found",
        )
    return item


def is_unique_region(
    item: RegionCreate | RegionUpdate,
    provider: Provider = Depends(valid_provider_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other regions, belonging to the same provider, with the same
    name.

    Args:
    ----
        item (RegionCreate | RegionUpdate): new data.
        provider (Provider): hosting provider.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given name already exists.
    """
    db_item = provider.regions.get_or_none(name=item.name)
    if db_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Region with name '{item.name}' already registered",
        )


def validate_new_region_values(
    update_data: RegionUpdate, item: Region = Depends(valid_region_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other user groups, belonging to the same identity provider, with
    the same name.

    Args:
    ----
        update_data (RegionUpdate): new data.
        item (Region): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given name already exists.
    """
    if update_data.name != item.name:
        is_unique_region(item=update_data, provider=item.provider.single())


def not_last_region(item: Region = Depends(valid_region_id)) -> Region:
    """Check parent provider has other regions."""
    db_provider: Provider = item.provider.single()
    if len(db_provider.regions) == 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"This region is the provider's {db_provider.uid} last one.",
        )
    return item
