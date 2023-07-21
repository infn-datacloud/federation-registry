from fastapi import APIRouter, Depends, HTTPException, status
from neomodel import db
from typing import List
from app.identity_provider.api.dependencies import valid_identity_provider_id
from app.identity_provider.models import IdentityProvider
from app.location.api.dependencies import valid_location_id
from app.location.models import Location

from app.pagination import Pagination, paginate
from app.provider.api.dependencies import valid_provider_id, valid_location
from app.provider.crud import provider
from app.provider.models import Provider
from app.provider.schemas import ProviderQuery
from app.provider.schemas_extended import (
    ProviderCreateExtended,
    ProviderReadExtended,
    ProviderUpdate,
)
from app.query import CommonGetQuery

router = APIRouter(prefix="/providers", tags=["providers"])


@db.read_transaction
@router.get("/", response_model=List[ProviderReadExtended])
def get_providers(
    comm: CommonGetQuery = Depends(),
    page: Pagination = Depends(),
    item: ProviderQuery = Depends(),
):
    items = provider.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    return paginate(items=items, page=page.page, size=page.size)


@db.write_transaction
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProviderReadExtended,
)
def post_provider(item: ProviderCreateExtended = Depends(valid_location)):
    return provider.create(obj_in=item, force=True)


@db.read_transaction
@router.get("/{provider_uid}", response_model=ProviderReadExtended)
def get_provider(item: Provider = Depends(valid_provider_id)):
    return item


@db.write_transaction
@router.put("/{provider_uid}", response_model=ProviderReadExtended)
def put_provider(
    update_data: ProviderUpdate,
    item: Provider = Depends(valid_provider_id),
):
    return provider.update(db_obj=item, obj_in=update_data)


@db.write_transaction
@router.delete("/{provider_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_providers(item: Provider = Depends(valid_provider_id)):
    if not provider.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


@db.write_transaction
@router.put(
    "/{project_uid}/identity_providers", response_model=ProviderReadExtended
)
def connect_user_group_identity_providers_link(
    item: Provider = Depends(valid_provider_id),
    identity_provider: IdentityProvider = Depends(valid_identity_provider_id),
):
    item.identity_providers.connect(identity_provider)
    return item


@db.write_transaction
@router.delete(
    "/{project_uid}/identity_providers", response_model=ProviderReadExtended
)
def disconnect_user_group_identity_providers_link(
    item: Provider = Depends(valid_provider_id),
    identity_provider: IdentityProvider = Depends(valid_identity_provider_id),
):
    item.identity_providers.disconnect(identity_provider)
    return item


@db.write_transaction
@router.put("/{user_group_uid}/locations", response_model=ProviderReadExtended)
def connect_user_group_location(
    item: Provider = Depends(valid_provider_id),
    location: Location = Depends(valid_location_id),
):
    if item.location is None:
        item.location.connect(location)
    else:
        item.location.replace(location)
    return item


@db.write_transaction
@router.delete(
    "/{user_group_uid}/locations", response_model=ProviderReadExtended
)
def disconnect_user_group_location(
    item: Provider = Depends(valid_provider_id),
    location: Location = Depends(valid_location_id),
):
    item.location.disconnect(location)
    return item
