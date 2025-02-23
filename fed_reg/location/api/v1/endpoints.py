"""Location endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""

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
from fedreg.location.models import Location
from fedreg.location.schemas import (
    LocationQuery,
    LocationRead,
    LocationUpdate,
)
from fedreg.location.schemas_extended import (
    LocationReadMulti,
    LocationReadSingle,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.location.api.dependencies import (
    valid_location_id,
    validate_new_location_values,
)
from fed_reg.location.crud import location_mng
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize

# from app.region.models import Region
# from app.region.api.dependencies import valid_region_id

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
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: LocationQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all locations.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = location_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = location_mng.paginate(items=items, page=page.page, size=page.size)
    return location_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{location_uid}",
    response_model=LocationReadSingle,
    summary="Read a specific location",
    description="Retrieve a specific location using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_location(
    size: SchemaSize = Depends(),
    item: Location = Depends(valid_location_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the location matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return location_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{location_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[LocationRead],
    dependencies=[
        Depends(validate_new_location_values),
    ],
    summary="Edit a specific Location",
    description="Update attribute values of a specific location. \
        The target location is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new location values checking there are \
        no other items with the given *site*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_location(
    request: Request,
    update_data: LocationUpdate,
    response: Response,
    item: Location = Depends(valid_location_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the location matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = location_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{location_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific location",
    description="Delete a specific location using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_location(
    request: Request,
    item: Location = Depends(valid_location_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the location matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not location_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


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
