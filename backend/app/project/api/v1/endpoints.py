from typing import List, Optional, Union

from app.auth.dependencies import check_read_access, check_write_access
from app.flavor.api.dependencies import valid_flavor_id
from app.flavor.models import Flavor
from app.image.api.dependencies import valid_image_id
from app.image.models import Image
from app.project.api.dependencies import valid_project_id, validate_new_project_values
from app.project.crud import project
from app.project.models import Project
from app.project.schemas import (
    ProjectQuery,
    ProjectRead,
    ProjectReadPublic,
    ProjectReadShort,
    ProjectUpdate,
)
from app.project.schemas_extended import ProjectReadExtended, ProjectReadExtendedPublic
from app.query import DbQueryCommonParams, Pagination, SchemaSize
from fastapi import APIRouter, Depends, HTTPException, Response, status
from neomodel import db

router = APIRouter(prefix="/projects", tags=["projects"])


@db.read_transaction
@router.get(
    "/",
    response_model=Union[
        List[ProjectReadExtended],
        List[ProjectRead],
        List[ProjectReadShort],
        List[ProjectReadExtendedPublic],
        List[ProjectReadPublic],
    ],
    summary="Read all projects",
    description="Retrieve all projects stored in the database. \
        It is possible to filter on projects attributes and other \
        common query parameters.",
)
def get_projects(
    auth: bool = Depends(check_read_access),
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ProjectQuery = Depends(),
):
    items = project.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = project.paginate(items=items, page=page.page, size=page.size)
    return project.choose_out_schema(
        items=items, auth=auth, short=size.short, with_conn=size.with_conn
    )


@db.read_transaction
@router.get(
    "/{project_uid}",
    response_model=Union[
        ProjectReadExtended,
        ProjectRead,
        ProjectReadShort,
        ProjectReadExtendedPublic,
        ProjectReadPublic,
    ],
    summary="Read a specific project",
    description="Retrieve a specific project using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
def get_project(
    auth: bool = Depends(check_read_access),
    size: SchemaSize = Depends(),
    item: Project = Depends(valid_project_id),
):
    return project.choose_out_schema(
        items=[item], auth=auth, short=size.short, with_conn=size.with_conn
    )[0]


@db.write_transaction
@router.patch(
    "/{project_uid}",
    response_model=Optional[ProjectRead],
    dependencies=[Depends(check_write_access), Depends(validate_new_project_values)],
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
def put_project(
    update_data: ProjectUpdate,
    response: Response,
    item: Project = Depends(valid_project_id),
):
    db_item = project.update(db_obj=item, obj_in=update_data)
    if db_item is None:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@db.write_transaction
@router.delete(
    "/{project_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_write_access)],
    summary="Delete a specific project",
    description="Delete a specific project using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related SLA and quotas.",
)
def delete_project(item: Project = Depends(valid_project_id)):
    if not project.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


@db.write_transaction
@router.put(
    "/{project_uid}/flavors/{flavor_uid}",
    response_model=ProjectReadExtended,
    dependencies=[Depends(check_write_access)],
    summary="Connect project to flavor",
    description="Connect a project to a specific flavor \
        knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
def connect_project_to_flavor(
    response: Response,
    item: Project = Depends(valid_project_id),
    flavor: Flavor = Depends(valid_flavor_id),
):
    if item.flavors.is_connected(flavor):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.flavors.connect(flavor)
    return item


@db.write_transaction
@router.delete(
    "/{project_uid}/flavors/{flavor_uid}",
    response_model=ProjectReadExtended,
    dependencies=[Depends(check_write_access)],
    summary="Disconnect project from flavor",
    description="Disconnect a project from a specific flavor \
        knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
def disconnect_project_from_flavor(
    response: Response,
    item: Project = Depends(valid_project_id),
    flavor: Flavor = Depends(valid_flavor_id),
):
    if not item.flavors.is_connected(flavor):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.flavors.disconnect(flavor)
    return item


@db.write_transaction
@router.put(
    "/{project_uid}/images/{image_uid}",
    response_model=ProjectReadExtended,
    dependencies=[Depends(check_write_access)],
    summary="Connect project to image",
    description="Connect a project to a specific image \
        knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
def connect_project_to_image(
    response: Response,
    item: Project = Depends(valid_project_id),
    image: Image = Depends(valid_image_id),
):
    if item.images.is_connected(image):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.images.connect(image)
    return item


@db.write_transaction
@router.delete(
    "/{project_uid}/images/{image_uid}",
    response_model=ProjectReadExtended,
    dependencies=[Depends(check_write_access)],
    summary="Disconnect project from image",
    description="Disconnect a project from a specific image \
        knowing their *uid*s. \
        If no entity matches the given *uid*s, the endpoint \
        raises a `not found` error.",
)
def disconnect_project_from_image(
    response: Response,
    item: Project = Depends(valid_project_id),
    image: Image = Depends(valid_image_id),
):
    if not item.images.is_connected(image):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.images.disconnect(image)
    return item
