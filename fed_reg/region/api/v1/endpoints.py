"""Region endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.region.models import Region
from fedreg.region.schemas import RegionQuery, RegionRead, RegionUpdate
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate
from fed_reg.region.api.dependencies import (
    get_region_item,
    region_must_exist,
    validate_new_region_values,
)
from fed_reg.region.api.utils import RegionReadMulti, RegionReadSingle, choose_schema
from fed_reg.region.crud import region_mgr

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get(
    "/",
    response_model=RegionReadMulti,
    summary="Read all regions",
    description="Retrieve all regions stored in the database. \
        It is possible to filter on regions attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_regions(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[RegionQuery, Depends()],
):
    """GET operation to retrieve all regions.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = region_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_schema(
        items, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@router.get(
    "/{region_uid}",
    response_model=RegionReadSingle,
    summary="Read a specific region",
    description="Retrieve a specific region using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_region(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[Region, Depends(region_must_exist)],
):
    """GET operation to retrieve the region matching a specific uid.

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
    "/{region_uid}",
    status_code=status.HTTP_200_OK,
    response_model=RegionRead | None,
    summary="Patch only specific attribute of the target region",
    description="Update only the received attribute values of a specific region. The \
        target region is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new region values checking there are no other items with the \
        given *uuid* and *name*. In that case, the endpoint raises the `conflict` \
        error. If there are no differences between new values and current ones, the \
        database entity is left unchanged and the endpoint returns the `not modified` \
        message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_region(
    response: Response,
    validated_data: Annotated[
        tuple[Region, RegionUpdate], Depends(validate_new_region_values)
    ],
):
    """PATCH operation to update the region matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = region_mgr.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{region_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific region",
    description="Delete a specific region using its *uid*. Returns `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_regions(item: Annotated[Region, Depends(get_region_item)]):
    """DELETE operation to remove the region matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        region_mgr.remove(db_obj=item)
