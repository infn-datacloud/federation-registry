"""Flavor endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from fastapi.security import HTTPBasicCredentials
from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.flavor.schemas import FlavorQuery, FlavorRead, FlavorUpdate
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.flavor.api.dependencies import (
    flavor_must_exist,
    get_flavor_item,
    validate_new_flavor_values,
)
from fed_reg.flavor.api.utils import FlavorReadMulti, FlavorReadSingle, choose_schema
from fed_reg.flavor.crud import flavor_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

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
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[FlavorQuery, Depends()],
):
    """GET operation to retrieve all flavors.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = flavor_mgr.get_multi(
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
    "/{flavor_uid}",
    response_model=FlavorReadSingle,
    summary="Read a specific flavor",
    description="Retrieve a specific flavor using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_flavor(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[PrivateFlavor | SharedFlavor, Depends(flavor_must_exist)],
):
    """GET operation to retrieve the flavor matching a specific uid.

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
    "/{flavor_uid}",
    status_code=status.HTTP_200_OK,
    response_model=FlavorRead | None,
    summary="Patch only specific attribute of the target flavor",
    description="Update only the received attribute values of a specific flavor. The \
        target flavor is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new flavor values checking there are no other items with the \
        given *uuid*, belonging to the same service. In that case, the endpoint raises \
        the `conflict` error. If there are no differences between new values and \
        current ones, the database entity is left unchanged and the endpoint returns \
        the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_flavor(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    response: Response,
    validated_data: Annotated[
        tuple[PrivateFlavor | SharedFlavor, FlavorUpdate],
        Depends(validate_new_flavor_values),
    ],
):
    """PATCH operation to update the flavor matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = flavor_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{flavor_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific flavor",
    description="Delete a specific flavor using its *uid*. Returns `no content`.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_flavors(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    item: Annotated[PrivateFlavor | SharedFlavor, Depends(get_flavor_item)],
):
    """DELETE operation to remove the flavor matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    flavor_mgr.remove(db_obj=item)
