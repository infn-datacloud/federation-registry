"""StorageClass endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.storageclass.models import StorageClass
from fedreg.storageclass.schemas import (
    StorageClassQuery,
    StorageClassRead,
    StorageClassUpdate,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate
from fed_reg.storageclass.api.dependencies import (
    get_storageclass_item,
    storageclass_must_exist,
    validate_new_storageclass_values,
)
from fed_reg.storageclass.api.utils import (
    StorageClassReadMulti,
    StorageClassReadSingle,
    choose_schema,
)
from fed_reg.storageclass.crud import storageclass_mgr

router = APIRouter(prefix="/storageclasss", tags=["storageclasss"])


@router.get(
    "/",
    response_model=StorageClassReadMulti,
    summary="Read all storageclasss",
    description="Retrieve all storageclasss stored in the database. \
        It is possible to filter on storageclasss attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_storageclasss(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[StorageClassQuery, Depends()],
):
    """GET operation to retrieve all storageclasss.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = storageclass_mgr.get_multi(
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
    "/{storageclass_uid}",
    response_model=StorageClassReadSingle,
    summary="Read a specific storageclass",
    description="Retrieve a specific storageclass using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_storageclass(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[StorageClass, Depends(storageclass_must_exist)],
):
    """GET operation to retrieve the storageclass matching a specific uid.

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
    "/{storageclass_uid}",
    status_code=status.HTTP_200_OK,
    response_model=StorageClassRead | None,
    summary="Patch only specific attribute of the target storageclass",
    description="Update only the received attribute values of a specific storageclass. \
        The target storageclass is identified using its *uid*. If no entity matches \
        the given *uid*, the endpoint raises a `not found` error.  At first, the \
        endpoint validates the new storageclass values checking there are no other \
        items with the given *uuid*, belonging to the same service. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_storageclass(
    response: Response,
    validated_data: Annotated[
        tuple[StorageClass, StorageClassUpdate],
        Depends(validate_new_storageclass_values),
    ],
):
    """PATCH operation to update the storageclass matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = storageclass_mgr.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{storageclass_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific storageclass",
    description="Delete a specific storageclass using its *uid*. Returns `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_storageclasss(
    item: Annotated[StorageClass, Depends(get_storageclass_item)],
):
    """DELETE operation to remove the storageclass matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        storageclass_mgr.remove(db_obj=item)
