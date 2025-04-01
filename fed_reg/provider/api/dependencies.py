"""Provider REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.provider.models import Provider
from fedreg.provider.schemas import ProviderUpdate
from fedreg.provider.schemas_extended import ProviderCreateExtended

from fed_reg.dependencies import valid_id
from fed_reg.provider.crud import provider_mgr


def provider_must_exist(provider_uid: str) -> Provider:
    """The target provider must exists otherwise raises `not found` error."""
    return valid_id(mgr=provider_mgr, item_id=provider_uid)


def provider_must_not_exist(item: ProviderCreateExtended) -> ProviderCreateExtended:
    """The target provider must exists otherwise raises `not found` error."""
    db_item = provider_mgr.get(name=item.name, type=item.type)
    if db_item is not None:
        msg = f"Provider with name '{item.name}' and type '{item.type}' already exists."
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


def get_provider_item(provider_uid: str) -> Provider:
    """Retrieve the target provider. If not found, return None."""
    return valid_id(mgr=provider_mgr, item_id=provider_uid, error=False)


def validate_new_provider_values(
    item: Annotated[Provider, Depends(provider_must_exist)],
    new_data: ProviderUpdate | ProviderCreateExtended,
) -> tuple[Provider, ProviderUpdate | ProviderCreateExtended]:
    """Check given data are valid ones.

    Check there are no other providers with the same site name. Avoid to change
    provider visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical site name already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.name is not None and new_data.name != item.name:
        db_item = provider_mgr.get(name=new_data.name, type=new_data.type)
        if db_item is not None:
            msg = (
                f"Provider with name '{item.name}' and type '{item.type}' already "
                "exists."
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    return item, new_data
