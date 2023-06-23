from fastapi import Depends, HTTPException, status
from pydantic import UUID4

from .schemas import ProviderCreate
from .models import Provider
from .crud import read_provider


def valid_provider_id(provider_uid: UUID4) -> Provider:
    item = read_provider(uid=str(provider_uid).replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_uid} not found",
        )
    return item


def is_unique_provider(item: ProviderCreate) -> ProviderCreate:
    db_item = read_provider(name=item.name)
    if db_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider with name '{item.name}' already registered",
        )
    return item


def check_rel_consistency(
    item: ProviderCreate = Depends(is_unique_provider),
) -> ProviderCreate:
    for l in [item.clusters, item.flavors, item.images, item.projects]:
        names = [i.relationship.name for i in l]
        if len(names) != len(set(names)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"There are multiple items with the same relationship name",
            )
        uuids = [i.relationship.uuid for i in l]
        if len(uuids) != len(set(uuids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"There are multiple items with the same relationship uuid",
            )
    return item


def check_rel_uniqueness(item: ProviderCreate) -> ProviderCreate:
    for l in [item.clusters, item.flavors, item.images, item.projects]:
        for i in l:
            end_node_rel_match_name = l.match(name=i.relationship.name).all()
            if len(end_node_rel_match_name) > 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"There are multiple items with relationship matching name '{i.relationship.name}'",
                )
            elif len(end_node_rel_match_name) == 1:
                end_node_rel_match_name = end_node_rel_match_name[0]
            else:
                end_node_rel_match_name = None

            end_node_rel_match_uuid = l.match(uuid=i.relationship.uuid).all()
            if len(end_node_rel_match_uuid) > 1:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"There are multiple items with relationship matching uuid '{i.relationship.uuid}'",
                )
            elif len(end_node_rel_match_uuid) == 1:
                end_node_rel_match_uuid = end_node_rel_match_uuid[0]
            else:
                end_node_rel_match_uuid = None
    return item