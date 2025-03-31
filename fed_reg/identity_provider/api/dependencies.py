"""IdentityProvider REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.identity_provider.models import IdentityProvider
from fedreg.identity_provider.schemas import IdentityProviderUpdate

from fed_reg.dependencies import valid_id
from fed_reg.identity_provider.crud import identity_provider_mgr


def identity_provider_must_exist(identity_provider_uid: str) -> IdentityProvider:
    """The target identity provider must exists otherwise raises `not found` error."""
    return valid_id(mgr=identity_provider_mgr, item_id=identity_provider_uid)


def get_identity_provider_item(identity_provider_uid: str) -> IdentityProvider:
    """Retrieve the target identity provider. If not found, return None."""
    return valid_id(
        mgr=identity_provider_mgr, item_id=identity_provider_uid, error=False
    )


def validate_new_identity_provider_values(
    item: Annotated[IdentityProvider, Depends(identity_provider_must_exist)],
    new_data: IdentityProviderUpdate,
) -> tuple[IdentityProvider, IdentityProviderUpdate]:
    """Check given data are valid ones.

    Check there are no other identity providers with the same endpoint.
    Avoid to change identity provider visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical endpoint already exists.

    Return the current item and the schema with the new data.
    """
    if str(new_data.endpoint) != item.endpoint:
        db_item = identity_provider_mgr.get(endpoint=new_data.endpoint)
        if db_item is not None:
            msg = (
                f"Identity Provider with endpoint '{item.endpoint}' already registered"
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    return item, new_data
