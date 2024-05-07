"""Region endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
from typing import List, Optional, Union

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
from neomodel import db

from fed_reg.auth import custom, flaat, lazy_security, security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize
from fed_reg.region.api.dependencies import (
    not_last_region,
    valid_region_id,
    validate_new_region_values,
)
from fed_reg.region.crud import region_mng
from fed_reg.region.models import Region
from fed_reg.region.schemas import (
    RegionQuery,
    RegionRead,
    RegionReadPublic,
    RegionUpdate,
)
from fed_reg.region.schemas_extended import (
    RegionReadExtended,
    RegionReadExtendedPublic,
)

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get(
    "/",
    response_model=Union[
        List[RegionReadExtended],
        List[RegionRead],
        List[RegionReadExtendedPublic],
        List[RegionReadPublic],
    ],
    summary="Read all regions",
    description="Retrieve all regions stored in the database. \
        It is possible to filter on regions attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_regions(
    request: Request,
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: RegionQuery = Depends(),
    client_credentials: HTTPBasicCredentials = Security(lazy_security),
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
    if client_credentials:
        user_infos = flaat.get_user_infos_from_request(request)
    else:
        user_infos = None
    items = region_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = region_mng.paginate(items=items, page=page.page, size=page.size)
    return region_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{region_uid}",
    response_model=Union[
        RegionReadExtended,
        RegionRead,
        RegionReadExtendedPublic,
        RegionReadPublic,
    ],
    summary="Read a specific region",
    description="Retrieve a specific region using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_region(
    request: Request,
    size: SchemaSize = Depends(),
    item: Region = Depends(valid_region_id),
    client_credentials: HTTPBasicCredentials = Security(lazy_security),
):
    """GET operation to retrieve the region matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    if client_credentials:
        user_infos = flaat.get_user_infos_from_request(request)
    else:
        user_infos = None
    return region_mng.choose_out_schema(
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
    db_item = region_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{region_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(not_last_region)],
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
    item: Region = Depends(valid_region_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the region matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not region_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
