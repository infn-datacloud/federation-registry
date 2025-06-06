"""Location endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.location.models import Location
from fedreg.location.schemas import LocationQuery, LocationRead, LocationUpdate
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.location.api.dependencies import (
    get_location_item,
    location_must_exist,
    validate_new_location_values,
)
from fed_reg.location.api.utils import (
    LocationReadMulti,
    LocationReadSingle,
    choose_schema,
)
from fed_reg.location.crud import location_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get(
    "/",
    response_model=LocationReadMulti,
    summary="Read all locations",
    description="Retrieve all locations stored in the database. \
        It is possible to filter on locations attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_locations(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[LocationQuery, Depends()],
):
    """GET operation to retrieve all locations.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = location_mgr.get_multi(
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
    "/{location_uid}",
    response_model=LocationReadSingle,
    summary="Read a specific location",
    description="Retrieve a specific location using its *uid*. If no entity matches \
        the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_location(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[Location, Depends(location_must_exist)],
):
    """GET operation to retrieve the location matching a specific uid.

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
    "/{location_uid}",
    status_code=status.HTTP_200_OK,
    response_model=LocationRead | None,
    summary="Patch only specific attribute of the target location",
    description="Update only the received attribute values of a specific location. The \
        target location is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new location values checking there are no other items with the \
        given *uuid* and *name*. In that case, the endpoint raises the `conflict` \
        error. If there are no differences between new values and current ones, the \
        database entity is left unchanged and the endpoint returns the `not modified` \
        message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_location(
    response: Response,
    validated_data: Annotated[
        tuple[Location, LocationUpdate],
        Depends(validate_new_location_values),
    ],
):
    """PATCH operation to update the location matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = location_mgr.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{location_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific location",
    description="Delete a specific location using its *uid*. Returns `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_locations(item: Annotated[Location, Depends(get_location_item)]):
    """DELETE operation to remove the location matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        location_mgr.remove(db_obj=item)


# @db.write_transaction
# @router.put(
#     "/{location_uid}/regions/{region_uid}",
#     response_model=Optional[LocationReadExtended],
#
#     summary="Connect location to region",
#     description="Connect a location to a specific region \
#         knowing their *uid*s. \
#         If the location already has a \
#         current region and the new one is different, \
#         the endpoint replaces it with the new one, otherwise \
#         it leaves the entity unchanged and returns a \
#         `not modified` message. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def connect_location_to_region(
#     response: Response,
#     item: Location = Depends(valid_location_id),
#     r_egion: Region = Depends(valid_region_id),
# ):
#     if not item.region.single():
#         item.region.connect(region)
#     elif not item.region.is_connected(region):
#         item.region.replace(region)
#     else:
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     return item


# @db.write_transaction
# @router.delete(
#     "/{location_uid}/regions/{region_uid}",
#     response_model=Optional[LocationReadExtended],
#
#     summary="Disconnect location from region",
#     description="Disconnect a location from a specific region \
#         knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def disconnect_location_from_region(
#     response: Response,
#     item: Location = Depends(valid_location_id),
#     r_egion: Region = Depends(valid_region_id),
# ):
#     if not item.region.is_connected(region):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.region.disconnect(region)
#     return item
