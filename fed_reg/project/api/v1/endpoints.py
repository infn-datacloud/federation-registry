"""Project endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
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
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security

# from app.flavor.api.dependencies import is_private_flavor, valid_flavor_id
# from app.flavor.crud import flavor
# from app.flavor.models import Flavor
# from app.flavor.schemas import FlavorRead, FlavorReadPublic, FlavorReadShort
# from app.flavor.schemas_extended import FlavorReadExtended, FlavorReadExtendedPublic
# from app.image.api.dependencies import is_private_image, valid_image_id
# from app.image.crud import image
# from app.image.models import Image
# from app.image.schemas import ImageRead, ImageReadPublic, ImageReadShort
# from app.image.schemas_extended import ImageReadExtended, ImageReadExtendedPublic
from fed_reg.project.api.dependencies import (
    valid_project_id,
    validate_new_project_values,
)
from fed_reg.project.api.utils import filter_on_region_attr
from fed_reg.project.crud import project_mng
from fed_reg.project.models import Project
from fed_reg.project.schemas import (
    ProjectQuery,
    ProjectRead,
    ProjectReadPublic,
    ProjectUpdate,
)
from fed_reg.project.schemas_extended import (
    ProjectReadExtended,
    ProjectReadExtendedPublic,
    ProjectReadMulti,
    ProjectReadSingle,
)
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize
from fed_reg.region.schemas import RegionQuery
from fed_reg.utils import choose_out_schema, paginate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "/",
    response_model=ProjectReadMulti,
    summary="Read all projects",
    description="Retrieve all projects stored in the database. \
        It is possible to filter on projects attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_projects(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ProjectQuery = Depends(),
    provider_uid: Optional[str] = None,
    region_name: Optional[str] = None,
    user_group_uid: Optional[str] = None,
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all projects.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = project_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    if provider_uid:
        items = filter(lambda x: x.provider.single().uid == provider_uid, items)
    if user_group_uid:
        items = filter(
            lambda x: x.sla.single().user_group.single().uid == user_group_uid, items
        )

    items = paginate(items=items, page=page.page, size=page.size)
    region_query = RegionQuery(name=region_name)
    items = filter_on_region_attr(items=items, region_query=region_query)
    items = choose_out_schema(
        schema_read_public=ProjectReadPublic,
        schema_read_private=ProjectRead,
        schema_read_public_extended=ProjectReadExtendedPublic,
        schema_read_private_extended=ProjectReadExtended,
        items=items,
        auth=user_infos,
        short=size.short,
        with_conn=size.with_conn,
    )
    if provider_uid and size.with_conn:
        for item in items:
            item.sla.user_group.identity_provider.providers = filter(
                lambda x: x.uid == item.provider.uid,
                item.sla.user_group.identity_provider.providers,
            )
    return items


@router.get(
    "/{project_uid}",
    response_model=ProjectReadSingle,
    summary="Read a specific project",
    description="Retrieve a specific project using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_project(
    size: SchemaSize = Depends(),
    item: Project = Depends(valid_project_id),
    region_name: Optional[str] = None,
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the project matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    region_query = RegionQuery(name=region_name)
    items = filter_on_region_attr(items=[item], region_query=region_query)
    items = choose_out_schema(
        schema_read_public=ProjectReadPublic,
        schema_read_private=ProjectRead,
        schema_read_public_extended=ProjectReadExtendedPublic,
        schema_read_private_extended=ProjectReadExtended,
        items=items,
        auth=user_infos,
        short=size.short,
        with_conn=size.with_conn,
    )
    return items[0]


@router.patch(
    "/{project_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ProjectRead],
    dependencies=[
        Depends(validate_new_project_values),
    ],
    summary="Edit a specific project",
    description="Update attribute values of a specific project. \
        The target project is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new project values checking there are \
        no other items with the given *uuid* and *name*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_project(
    request: Request,
    update_data: ProjectUpdate,
    response: Response,
    item: Project = Depends(valid_project_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the project matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = project_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{project_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific project",
    description="Delete a specific project using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related SLA and quotas. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_project(
    request: Request,
    item: Project = Depends(valid_project_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the project matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not project_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


# @db.read_transaction
# @router.get(
#     "/{project_uid}/flavors",
#     response_model=
#         list[FlavorReadExtended]|
#         list[FlavorRead]|
#         list[FlavorReadShort]|
#         list[FlavorReadExtendedPublic]|
#         list[FlavorReadPublic],
#     summary="Read user group accessible flavors",
#     description="Retrieve all the flavors the user group \
#         has access to thanks to its SLA. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error.",
# )
# def get_project_flavors(
#     auth: bool = Depends(check_read_access),
#     size: SchemaSize = Depends(),
#     item: Project = Depends(valid_project_id),
# ):
#     items = item.private_flavors.all() + item.public_flavors()
#     return flavor.choose_out_schema(
#         items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
#     )


# @db.write_transaction
# @router.put(
#     "/{project_uid}/flavors/{flavor_uid}",
#     response_model=Optional[list[FlavorRead]],
#
#     summary="Connect project to flavor",
#     description="Connect a project to a specific flavor \
#         knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def connect_project_to_flavor(
#     response: Response,
#     item: Project = Depends(valid_project_id),
#     flavor: Flavor = Depends(is_private_flavor),
# ):
#     if item.private_flavors.is_connected(flavor):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.private_flavors.connect(flavor)
#     return item.private_flavors.all()


# @db.write_transaction
# @router.delete(
#     "/{project_uid}/flavors/{flavor_uid}",
#     response_model=Optional[list[FlavorRead]],
#
#     summary="Disconnect project from flavor",
#     description="Disconnect a project from a specific flavor \
#         knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def disconnect_project_from_flavor(
#     response: Response,
#     item: Project = Depends(valid_project_id),
#     flavor: Flavor = Depends(valid_flavor_id),
# ):
#     if not item.private_flavors.is_connected(flavor):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.private_flavors.disconnect(flavor)
#     return item.private_flavors.all()


# @db.read_transaction
# @router.get(
#     "/{project_uid}/images",
#     response_model=list[ImageReadExtended]|
#         list[ImageRead]|
#         list[ImageReadShort]|
#         list[ImageReadExtendedPublic]|
#         list[ImageReadPublic],
#     summary="Read user group accessible images",
#     description="Retrieve all the images the user group \
#         has access to thanks to its SLA. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error.",
# )
# def get_project_images(
#     auth: bool = Depends(check_read_access),
#     size: SchemaSize = Depends(),
#     item: Project = Depends(valid_project_id),
# ):
#     items = item.private_images.all() + item.public_images()
#     return image.choose_out_schema(
#         items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
#     )


# @db.write_transaction
# @router.put(
#     "/{project_uid}/images/{image_uid}",
#     response_model=Optional[list[ImageRead]],
#
#     summary="Connect project to image",
#     description="Connect a project to a specific image \
#         knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def connect_project_to_image(
#     response: Response,
#     item: Project = Depends(valid_project_id),
#     image: Image = Depends(is_private_image),
# ):
#     if item.private_images.is_connected(image):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.private_images.connect(image)
#     return item.private_images.all()


# @db.write_transaction
# @router.delete(
#     "/{project_uid}/images/{image_uid}",
#     response_model=Optional[list[ImageRead]],
#
#     summary="Disconnect project from image",
#     description="Disconnect a project from a specific image \
#         knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def disconnect_project_from_image(
#     response: Response,
#     item: Project = Depends(valid_project_id),
#     image: Image = Depends(valid_image_id),
# ):
#     if not item.private_images.is_connected(image):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.private_images.disconnect(image)
#     return item.private_images.all()
