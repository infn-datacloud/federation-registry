"""Project endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.project.models import Project
from fedreg.project.schemas import (
    ProjectQuery,
    ProjectRead,
    ProjectUpdate,
)
from fedreg.project.schemas_extended import (
    ProjectReadMulti,
    ProjectReadSingle,
)
from fedreg.region.schemas import RegionQuery
from fedreg.service.schemas import IdentityServiceQuery
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.project.api.dependencies import (
    get_project_item,
    project_must_exist,
    validate_new_project_values,
)
from fed_reg.project.api.utils import (
    choose_schema,
    filter_on_region_attr,
    filter_on_service_attr,
)
from fed_reg.project.crud import project_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

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
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ProjectQuery, Depends()],
    identity_service_endpoint: str | None = None,
    provider_uid: str | None = None,
    region_name: str | None = None,
    user_group_uid: str | None = None,
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
    items = project_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    if provider_uid:
        items = filter(lambda x: x.provider.single().uid == provider_uid, items)
    if user_group_uid:
        items = filter(
            lambda x: x.sla.single().user_group.single().uid == user_group_uid, items
        )
    region_query = RegionQuery(name=region_name)
    items = filter_on_region_attr(items=items, region_query=region_query)
    service_query = IdentityServiceQuery(endpoint=identity_service_endpoint)
    items = filter_on_service_attr(items=items, service_query=service_query)

    items = paginate(items=items, page=page.page, size=page.size)
    items = choose_schema(
        items, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )
    if provider_uid and shape.with_conn:
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
    description="Retrieve a specific project using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_project(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[Project, Depends(project_must_exist)],
):
    """GET operation to retrieve the project matching a specific uid.

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
    "/{project_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ProjectRead | None,
    summary="Patch only specific attribute of the target project",
    description="Update only the received attribute values of a specific project. The \
        target project is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new project values checking there are no other items with the \
        given *uuid* and *name*. In that case, the endpoint raises the `conflict` \
        error. If there are no differences between new values and current ones, the \
        database entity is left unchanged and the endpoint returns the `not modified` \
        message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_project(
    response: Response,
    validated_data: Annotated[
        tuple[Project, ProjectUpdate],
        Depends(validate_new_project_values),
    ],
):
    """PATCH operation to update the project matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = project_mgr.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{project_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific project",
    description="Delete a specific project using its *uid*. Returns `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_projects(item: Annotated[Project, Depends(get_project_item)]):
    """DELETE operation to remove the project matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        project_mgr.remove(db_obj=item)


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
#     size: SchemaShape = Depends(),
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
#     size: SchemaShape = Depends(),
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
