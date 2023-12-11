from typing import Any, List, Optional, Union

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

from app.auth import flaat, security
from app.query import DbQueryCommonParams, Pagination, SchemaSize
from app.region.api.dependencies import (
    not_last_region,
    valid_region_id,
    validate_new_region_values,
)
from app.region.crud import region_mng
from app.region.models import Region
from app.region.schemas import (
    RegionQuery,
    RegionRead,
    RegionReadPublic,
    RegionUpdate,
)
from app.region.schemas_extended import (
    RegionReadExtended,
    RegionReadExtendedPublic,
)

router = APIRouter(prefix="/regions", tags=["regions"])


@db.read_transaction
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
@flaat.inject_user_infos(strict=False)
def get_regions(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: RegionQuery = Depends(),
    user_infos: Optional[Any] = None,
):
    items = region_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = region_mng.paginate(items=items, page=page.page, size=page.size)
    return region_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@db.read_transaction
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
@flaat.inject_user_infos(strict=False)
def get_region(
    size: SchemaSize = Depends(),
    item: Region = Depends(valid_region_id),
    user_infos: Optional[Any] = None,
):
    return region_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@db.write_transaction
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
def put_region(
    request: Request,
    update_data: RegionUpdate,
    response: Response,
    item: Region = Depends(valid_region_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    db_item = region_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@db.write_transaction
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
def delete_regions(
    request: Request,
    item: Region = Depends(valid_region_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    if not region_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
