"""Flavor endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

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
from fedreg.flavor.models import Flavor
from fedreg.flavor.schemas import (
    FlavorQuery,
    FlavorRead,
    FlavorUpdate,
)
from fedreg.flavor.schemas_extended import (
    FlavorReadMulti,
    FlavorReadSingle,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.flavor.api.dependencies import (
    valid_flavor_id,
    validate_new_flavor_values,
)
from fed_reg.flavor.crud import flavor_mng
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize

router = APIRouter(prefix="/flavors", tags=["flavors"])


@router.get(
    "/",
    response_model=FlavorReadMulti,
    summary="Read all flavors",
    description="Retrieve all flavors stored in the database. \
        It is possible to filter on flavors attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_flavors(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: FlavorQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all flavors.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = flavor_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = flavor_mng.paginate(items=items, page=page.page, size=page.size)
    return flavor_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{flavor_uid}",
    response_model=FlavorReadSingle,
    summary="Read a specific flavor",
    description="Retrieve a specific flavor using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_flavor(
    size: SchemaSize = Depends(),
    item: Flavor = Depends(valid_flavor_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the flavor matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return flavor_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{flavor_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[FlavorRead],
    dependencies=[
        Depends(validate_new_flavor_values),
    ],
    summary="Edit a specific flavor",
    description="Update attribute values of a specific flavor_mng. \
        The target flavor is identified using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new flavor values checking there are \
        no other items with the given *uuid* and *name*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_flavor(
    request: Request,
    update_data: FlavorUpdate,
    response: Response,
    item: Flavor = Depends(valid_flavor_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the flavor matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = flavor_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{flavor_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific flavor",
    description="Delete a specific flavor using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_flavors(
    request: Request,
    item: Flavor = Depends(valid_flavor_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the flavor matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not flavor_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
