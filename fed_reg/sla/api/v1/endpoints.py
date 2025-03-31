"""SLA endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from fastapi.security import HTTPBasicCredentials
from fedreg.sla.models import SLA
from fedreg.sla.schemas import SLAQuery, SLARead, SLAUpdate
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate
from fed_reg.sla.api.dependencies import (
    get_sla_item,
    sla_must_exist,
    validate_new_sla_values,
)
from fed_reg.sla.api.utils import SLAReadMulti, SLAReadSingle, choose_schema
from fed_reg.sla.crud import sla_mgr

router = APIRouter(prefix="/slas", tags=["slas"])


@router.get(
    "/",
    response_model=SLAReadMulti,
    summary="Read all slas",
    description="Retrieve all slas stored in the database. \
        It is possible to filter on slas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_slas(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[SLAQuery, Depends()],
):
    """GET operation to retrieve all slas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = sla_mgr.get_multi(
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
    "/{sla_uid}",
    response_model=SLAReadSingle,
    summary="Read a specific sla",
    description="Retrieve a specific sla using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_sla(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[SLA, Depends(sla_must_exist)],
):
    """GET operation to retrieve the sla matching a specific uid.

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
    "/{sla_uid}",
    status_code=status.HTTP_200_OK,
    response_model=SLARead | None,
    summary="Patch only specific attribute of the target sla",
    description="Update only the received attribute values of a specific sla. The \
        target sla is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new sla values checking there are no other items with the \
        given *doc_uuid*. In that case, the endpoint raises the `conflict` \
        error. If there are no differences between new values and current ones, the \
        database entity is left unchanged and the endpoint returns the `not modified` \
        message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_sla(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    response: Response,
    validated_data: Annotated[tuple[SLA, SLAUpdate], Depends(validate_new_sla_values)],
):
    """PATCH operation to update the sla matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = sla_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{sla_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific sla",
    description="Delete a specific sla using its *uid*. Returns `no content`.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_slas(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    item: Annotated[SLA, Depends(get_sla_item)],
):
    """DELETE operation to remove the sla matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    sla_mgr.remove(db_obj=item)


# @db.write_transaction
# @router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=SLAReadExtended,
#     dependencies=[ Depends(is_unique_sla)],
#     summary="Create an SLA",
#     description="Create an SLA associated to a user group \
#         and a project each identified by the given *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error. \
#         At first validate new SLA values checking there are \
#         no other items pointing the given *document uuid*. \
#         Moreover, check the target project is not already \
#         involved into another SLA.",
# )
# def post_sla(
#     item: SLACreate,
#     project: Project = Depends(project_has_no_sla),
#     user_group: UserGroup = Depends(valid_user_group_id),
# ):
#     # Check Project provider is one of the UserGroup accessible providers
#     provider = project.provider.single()
#     idp = user_group.identity_provider.single()
#     providers = idp.providers.all()
#     if provider not in providers:
#         msg = f"Project's provider '{provider.name}' does not support "
#         msg += "given user group."
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
#     # Check UserGroup does not already have a project on the same provider
#     slas = user_group.slas.all()
#     for s in slas:
#         p = s.project.single()
#         if p.provider.single() == provider:
#             msg = f"Project's provider '{provider.name}' has already assigned "
#             msg += f"a project to user group '{user_group.name}'."
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
#     # Create SLA
#     return sla.create(obj_in=item, project=project, user_group=user_group, force=True)
