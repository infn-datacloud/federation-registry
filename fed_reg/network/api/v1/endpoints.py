"""Network endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from fastapi.security import HTTPBasicCredentials
from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.network.schemas import NetworkQuery, NetworkRead, NetworkUpdate
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.network.api.dependencies import (
    get_network_item,
    network_must_exist,
    validate_new_network_values,
)
from fed_reg.network.api.utils import NetworkReadMulti, NetworkReadSingle, choose_schema
from fed_reg.network.crud import network_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

router = APIRouter(prefix="/networks", tags=["networks"])


@router.get(
    "/",
    response_model=NetworkReadMulti,
    summary="Read all networks",
    description="Retrieve all networks stored in the database. \
        It is possible to filter on networks attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_networks(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[NetworkQuery, Depends()],
):
    """GET operation to retrieve all networks.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = network_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_schema(
        items,
        auth=user_infos is not None,
        short=shape.short,
        with_conn=shape.with_conn,
    )


@router.get(
    "/{network_uid}",
    response_model=NetworkReadSingle,
    summary="Read a specific network",
    description="Retrieve a specific network using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[PrivateNetwork | SharedNetwork, Depends(network_must_exist)],
):
    """GET operation to retrieve the network matching a specific uid.

    The endpoint expects a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - shape: parameters to define the number of information contained in each result.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    return choose_schema(
        item, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@router.patch(
    "/{network_uid}",
    status_code=status.HTTP_200_OK,
    response_model=NetworkRead | None,
    summary="Patch only specific attribute of the target network",
    description="Update only the received attribute values of a specific network. The \
        target network is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new network values checking there are no other items with the \
        given *uuid*, belonging to the same service. In that case, the endpoint raises \
        the `conflict` error. If there are no differences between new values and \
        current ones, the database entity is left unchanged and the endpoint returns \
        the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_network(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    response: Response,
    validated_data: Annotated[
        tuple[PrivateNetwork | SharedNetwork, NetworkUpdate],
        Depends(validate_new_network_values),
    ],
):
    """PATCH operation to update the network matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = network_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{network_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific network",
    description="Delete a specific network using its *uid*. Returns `no content`.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_networks(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    item: Annotated[PrivateNetwork | SharedNetwork, Depends(get_network_item)],
):
    """DELETE operation to remove the network matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    network_mgr.remove(db_obj=item)
