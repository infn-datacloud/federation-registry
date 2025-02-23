"""Image endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
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
from fedreg.image.models import Image
from fedreg.image.schemas import (
    ImageQuery,
    ImageRead,
    ImageUpdate,
)
from fedreg.image.schemas_extended import (
    ImageReadMulti,
    ImageReadSingle,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.image.api.dependencies import (
    valid_image_id,
    validate_new_image_values,
)
from fed_reg.image.crud import image_mng
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize

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
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ImageQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all images.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = image_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = image_mng.paginate(items=items, page=page.page, size=page.size)
    return image_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{image_uid}",
    response_model=ImageReadSingle,
    summary="Read a specific image",
    description="Retrieve a specific image using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_image(
    size: SchemaSize = Depends(),
    item: Image = Depends(valid_image_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the image matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return image_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{image_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ImageRead],
    dependencies=[
        Depends(validate_new_image_values),
    ],
    summary="Edit a specific image",
    description="Update attribute values of a specific image. \
        The target image is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new image values checking there are \
        no other items with the given *uuid* and *name*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_image(
    request: Request,
    update_data: ImageUpdate,
    response: Response,
    item: Image = Depends(valid_image_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the image matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = image_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{image_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific image",
    description="Delete a specific image using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_images(
    request: Request,
    item: Image = Depends(valid_image_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the image matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not image_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
