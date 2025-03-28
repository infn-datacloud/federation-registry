"""Region endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""

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
from fedreg.region.models import Region
from fedreg.region.schemas import (
    RegionQuery,
    RegionRead,
    RegionUpdate,
)
from fedreg.region.schemas_extended import (
    RegionReadMulti,
    RegionReadSingle,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize
from fed_reg.region.api.dependencies import (
    not_last_region,
    valid_region_id,
    validate_new_region_values,
)
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
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: RegionQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all regions.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = region_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = region_mgr.paginate(items=items, page=page.page, size=page.size)
    return region_mgr.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{region_uid}",
    response_model=RegionReadSingle,
    summary="Read a specific region",
    description="Retrieve a specific region using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_region(
    size: SchemaSize = Depends(),
    item: Region = Depends(valid_region_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the region matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return region_mgr.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{region_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[RegionRead],
    dependencies=[
        Depends(validate_new_region_values),
    ],
    summary="Edit a specific region",
    description="Update attribute values of a specific region. \
        The target region is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new region values checking there are \
        no other items, belonging to the same provider with \
        the given *name*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_region(
    request: Request,
    update_data: RegionUpdate,
    response: Response,
    item: Region = Depends(valid_region_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the region matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = region_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{region_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific region",
    description="Delete a specific region using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_regions(
    request: Request,
    item: Region = Depends(not_last_region),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the region matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not region_mgr.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
