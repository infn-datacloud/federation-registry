"""Network endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    Security,
    status,
)
from fastapi.security import HTTPBasicCredentials
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.network.api.dependencies import (
    valid_network_id,
    validate_new_network_values,
)
from fed_reg.network.crud import network_mgr
from fed_reg.network.models import Network
from fed_reg.network.schemas import (
    NetworkQuery,
    NetworkRead,
    NetworkReadPublic,
    NetworkUpdate,
)
from fed_reg.network.schemas_extended import (
    NetworkReadExtended,
    NetworkReadExtendedPublic,
    NetworkReadMulti,
    NetworkReadSingle,
)
from fed_reg.pagination import Pagination, paginate
from fed_reg.query import DbQueryCommonParams, SchemaSize
from fed_reg.utils import choose_out_schema

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
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: NetworkQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all networks.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = network_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_out_schema(
        schema_read_public=NetworkReadPublic,
        schema_read_private=NetworkRead,
        schema_read_public_extended=NetworkReadExtendedPublic,
        schema_read_private_extended=NetworkReadExtended,
        items=items,
        auth=user_infos,
        short=size.short,
        with_conn=size.with_conn,
    )


@router.get(
    "/{network_uid}",
    response_model=NetworkReadSingle,
    summary="Read a specific network",
    description="Retrieve a specific network using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network(
    size: SchemaSize = Depends(),
    item: Network = Depends(valid_network_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the network matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return choose_out_schema(
        schema_read_public=NetworkReadPublic,
        schema_read_private=NetworkRead,
        schema_read_public_extended=NetworkReadExtendedPublic,
        schema_read_private_extended=NetworkReadExtended,
        items=[item],
        auth=user_infos,
        short=size.short,
        with_conn=size.with_conn,
    )[0]


@router.patch(
    "/{network_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[NetworkRead],
    dependencies=[
        Depends(validate_new_network_values),
    ],
    summary="Edit a specific network",
    description="Update attribute values of a specific network. \
        The target network is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new network values checking there are \
        no other items with the given *uuid* and *name*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_network(
    request: Request,
    update_data: NetworkUpdate,
    response: Response,
    item: Network = Depends(valid_network_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the network matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = network_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{network_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific network",
    description="Delete a specific network using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_networks(
    request: Request,
    item: Network = Depends(valid_network_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the network matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not network_mgr.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
