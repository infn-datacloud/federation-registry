from typing import List, Optional, Union

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
from neomodel import db

from app.auth import custom, flaat, lazy_security, security

# from app.project.api.dependencies import project_has_no_sla
# from app.project.models import Project
from app.query import DbQueryCommonParams, Pagination, SchemaSize
from app.sla.api.dependencies import (  # is_unique_sla,
    valid_sla_id,
    validate_new_sla_values,
)
from app.sla.crud import sla_mng
from app.sla.models import SLA
from app.sla.schemas import (
    SLAQuery,
    SLARead,
    SLAReadPublic,
    SLAUpdate,
)
from app.sla.schemas_extended import SLAReadExtended, SLAReadExtendedPublic

router = APIRouter(prefix="/slas", tags=["slas"])


@db.read_transaction
@router.get(
    "/",
    response_model=Union[
        List[SLAReadExtended],
        List[SLARead],
        List[SLAReadExtendedPublic],
        List[SLAReadPublic],
    ],
    summary="Read all SLAs",
    description="Retrieve all SLAs stored in the database. \
        It is possible to filter on SLAs attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
def get_slas(
    request: Request,
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: SLAQuery = Depends(),
    client_credentials: HTTPBasicCredentials = Security(lazy_security),
):
    if client_credentials:
        user_infos = flaat.get_user_infos_from_request(request)
    else:
        user_infos = None
    items = sla_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = sla_mng.paginate(items=items, page=page.page, size=page.size)
    return sla_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
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


@db.read_transaction
@router.get(
    "/{sla_uid}",
    response_model=Union[
        SLAReadExtended,
        SLARead,
        SLAReadExtendedPublic,
        SLAReadPublic,
    ],
    summary="Read a specific SLA",
    description="Retrieve a specific SLA using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
def get_sla(
    request: Request,
    size: SchemaSize = Depends(),
    item: SLA = Depends(valid_sla_id),
    client_credentials: HTTPBasicCredentials = Security(lazy_security),
):
    if client_credentials:
        user_infos = flaat.get_user_infos_from_request(request)
    else:
        user_infos = None
    return sla_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@db.write_transaction
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
def put_sla(
    request: Request,
    update_data: SLAUpdate,
    response: Response,
    item: SLA = Depends(valid_sla_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    db_item = sla_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@db.write_transaction
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
def delete_slas(
    request: Request,
    item: SLA = Depends(valid_sla_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    if not sla_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
