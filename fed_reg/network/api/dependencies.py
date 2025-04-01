"""Network REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.network.schemas import NetworkUpdate
from neomodel.exceptions import CardinalityViolation

from fed_reg.dependencies import valid_id
from fed_reg.network.crud import network_mgr


def network_must_exist(network_uid: str) -> PrivateNetwork | SharedNetwork:
    """The target network must exists otherwise raises `not found` error."""
    return valid_id(mgr=network_mgr, item_id=network_uid)


def get_network_item(network_uid: str) -> PrivateNetwork | SharedNetwork:
    """Retrieve the target network. If not found, return None."""
    return valid_id(mgr=network_mgr, item_id=network_uid, error=False)


def validate_new_network_values(
    item: Annotated[PrivateNetwork | SharedNetwork, Depends(network_must_exist)],
    new_data: NetworkUpdate,
) -> tuple[PrivateNetwork | SharedNetwork, NetworkUpdate]:
    """Check given data are valid ones.

    Check there are no other networks, belonging to the same service, with the same
    uuid. Avoid to change network visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid and belonging to the
    same service already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.uuid is not None and new_data.uuid != item.uuid:
        try:
            service = item.service.single()
        except CardinalityViolation as e:
            msg = f"Corrupted DB: Network with uuid '{item.uuid}' has no linked service"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            ) from e
        db_item = service.networks.get_or_none(uuid=new_data.uuid)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Network with uuid '{item.uuid}' already registered",
            )
    return item, new_data
