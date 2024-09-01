"""SLA endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""
from typing import Optional

# from app.user_group.api.dependencies import valid_user_group_id
# from app.user_group.models import UserGroup
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

# from app.project.api.dependencies import project_has_no_sla
# from app.project.models import Project
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize
from fed_reg.sla.api.dependencies import (  # is_unique_sla,
    valid_sla_id,
    validate_new_sla_values,
)
from fed_reg.sla.crud import sla_mng
from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import (
    SLAQuery,
    SLARead,
    SLAReadPublic,
    SLAUpdate,
)
from fed_reg.sla.schemas_extended import (
    SLAReadExtended,
    SLAReadExtendedPublic,
    SLAReadMulti,
    SLAReadSingle,
)
from fed_reg.utils import choose_out_schema, paginate

router = APIRouter(prefix="/slas", tags=["slas"])


@router.get(
    "/",
    response_model=SLAReadMulti,
    summary="Read all SLAs",
    description="Retrieve all SLAs stored in the database. \
        It is possible to filter on SLAs attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_slas(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: SLAQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all SLAs.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = sla_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_out_schema(
        schema_read_public=SLAReadPublic,
        schema_read_private=SLARead,
        schema_read_public_extended=SLAReadExtendedPublic,
        schema_read_private_extended=SLAReadExtended,
        items=items,
        auth=user_infos,
        short=size.short,
        with_conn=size.with_conn,
    )


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


@router.get(
    "/{sla_uid}",
    response_model=SLAReadSingle,
    summary="Read a specific SLA",
    description="Retrieve a specific SLA using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_sla(
    size: SchemaSize = Depends(),
    item: SLA = Depends(valid_sla_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the SLA matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return choose_out_schema(
        schema_read_public=SLAReadPublic,
        schema_read_private=SLARead,
        schema_read_public_extended=SLAReadExtendedPublic,
        schema_read_private_extended=SLAReadExtended,
        items=[item],
        auth=user_infos,
        short=size.short,
        with_conn=size.with_conn,
    )[0]


@router.patch(
    "/{sla_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[SLARead],
    dependencies=[
        Depends(validate_new_sla_values),
    ],
    summary="Edit a specific SLA",
    description="Update attribute values of a specific SLA. \
        The target SLA is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new SLA values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_sla(
    request: Request,
    update_data: SLAUpdate,
    response: Response,
    item: SLA = Depends(valid_sla_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the SLA matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = sla_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{sla_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific SLA",
    description="Delete a specific SLA using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_slas(
    request: Request,
    item: SLA = Depends(valid_sla_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the SLA matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not sla_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
