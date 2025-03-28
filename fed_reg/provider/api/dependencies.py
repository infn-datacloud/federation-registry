"""Provider REST API dependencies."""

from fastapi import Depends, HTTPException, status
from fedreg.identity_provider.models import IdentityProvider
from fedreg.provider.models import Provider
from fedreg.provider.schemas import ProviderUpdate
from fedreg.provider.schemas_extended import (
    IdentityProviderCreateExtended,
    ProviderCreateExtended,
    RegionCreateExtended,
)
from fedreg.user_group.models import UserGroup
from pydantic import UUID4

from fed_reg.identity_provider.crud import identity_provider_mgr
from fed_reg.location.crud import location_mgr
from fed_reg.provider.crud import provider_mgr
from fed_reg.service.api.dependencies import (
    valid_block_storage_service_endpoint,
    valid_compute_service_endpoint,
    valid_identity_service_endpoint,
    valid_network_service_endpoint,
)
from fed_reg.sla.crud import sla_mgr


def valid_provider_id(provider_uid: UUID4) -> Provider:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        provider_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Provider: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = provider_mgr.get(uid=str(provider_uid).replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_uid}' not found",
        )
    return item


def is_unique_provider(item: ProviderCreateExtended | ProviderUpdate) -> None:
    """Check there are no other providers with the same name and type.

    Args:
    ----
        item (ProviderCreateExtended | ProviderUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given name already exists.
    """
    db_item = provider_mgr.get(name=item.name)
    if db_item is not None and db_item.type == item.type:
        msg = f"Provider with name '{item.name}' and type '{db_item.type}' "
        msg += "already registered"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )


def validate_new_provider_values(
    update_data: ProviderUpdate, item: Provider = Depends(valid_provider_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other providers with the same name and type.

    Args:
    ----
        update_data (ProviderUpdate): new data.
        item (Provider): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given name already exists.
    """
    if update_data.name != item.name:
        is_unique_provider(update_data)


def valid_provider(item: ProviderCreateExtended) -> None:
    """Check given data are valid ones.

    Check provider does not already exists and validate identity providers and regions.
    """
    is_unique_provider(item)
    for idp in item.identity_providers:
        valid_identity_provider(idp)
    for region in item.regions:
        valid_region(region)


def valid_identity_provider(item: IdentityProviderCreateExtended) -> None:
    """Check given data are valid ones.

    Check there are no identity providers with the same endpoint, in the identity
    provider list of the received provider. Check that all items have a corresponding
    relationship Check that if there is another identity provider in the DB with the
    same endpoint, it matches the given attributes.

    Args:
    ----
        item (ProviderCreateExtended): provider data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: multiple items with identical name or uuid,
            or DB entity with given endpoint already exists but has
            different attributes.
    """
    db_item = identity_provider_mgr.get(endpoint=item.endpoint)
    if db_item is not None:
        data = item.dict(exclude={"relationship", "user_groups"}, exclude_unset=True)
        for k, v in data.items():
            if db_item.__getattribute__(k) != v:
                msg = f"Identity Provider '{item.endpoint}' already exists with "
                msg += f"different attributes. Received: {data}. Stored: {db_item}"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    for group in item.user_groups:
        db_item = sla_mgr.get(doc_uuid=group.sla.doc_uuid)
        if db_item is not None:
            db_group: UserGroup = db_item.user_group.single()
            db_idp: IdentityProvider = db_group.identity_provider.single()
            if db_group.name != group.name or db_idp.endpoint != item.endpoint:
                msg = f"SLA {group.sla.doc_uuid} already used by another group"
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


def valid_region(item: RegionCreateExtended) -> None:
    """Check given data are valid one."""
    if item.location is not None:
        db_item = location_mgr.get(site=item.location.site)
        if db_item is not None:
            for k, v in item.location.dict(exclude_unset=True).items():
                if db_item.__getattribute__(k) != v:
                    msg = f"Location '{item.location.site}' already exists with "
                    msg += f"different attributes. Received: {item.location.dict()}. "
                    msg += f"Stored: {db_item}"
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=msg
                    )

    for service in item.block_storage_services:
        valid_block_storage_service_endpoint(service)
    for service in item.compute_services:
        valid_compute_service_endpoint(service)
    for service in item.identity_services:
        valid_identity_service_endpoint(service)
    for service in item.network_services:
        valid_network_service_endpoint(service)
