"""Image endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from fastapi.security import HTTPBasicCredentials
from fedreg.image.models import PrivateImage, SharedImage
from fedreg.image.schemas import ImageQuery, ImageRead, ImageUpdate
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.image.api.dependencies import (
    get_image_item,
    image_must_exist,
    validate_new_image_values,
)
from fed_reg.image.api.utils import ImageReadMulti, ImageReadSingle, choose_schema
from fed_reg.image.crud import image_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

router = APIRouter(prefix="/images", tags=["images"])


@router.get(
    "/",
    response_model=ImageReadMulti,
    summary="Read all images",
    description="Retrieve all images stored in the database. \
        It is possible to filter on images attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_images(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ImageQuery, Depends()],
):
    """GET operation to retrieve all images.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = image_mgr.get_multi(
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
    "/{image_uid}",
    response_model=ImageReadSingle,
    summary="Read a specific image",
    description="Retrieve a specific image using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_image(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[PrivateImage | SharedImage, Depends(image_must_exist)],
):
    """GET operation to retrieve the image matching a specific uid.

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
    "/{image_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ImageRead | None,
    summary="Patch only specific attribute of the target image",
    description="Update only the received attribute values of a specific image. The \
        target image is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new image values checking there are no other items with the \
        given *uuid*, belonging to the same service. In that case, the endpoint raises \
        the `conflict` error. If there are no differences between new values and \
        current ones, the database entity is left unchanged and the endpoint returns \
        the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_image(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    response: Response,
    validated_data: Annotated[
        tuple[PrivateImage | SharedImage, ImageUpdate],
        Depends(validate_new_image_values),
    ],
):
    """PATCH operation to update the image matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = image_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{image_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific image",
    description="Delete a specific image using its *uid*. Returns `no content`.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_images(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    item: Annotated[PrivateImage | SharedImage, Depends(get_image_item)],
):
    """DELETE operation to remove the image matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    image_mgr.remove(db_obj=item)
