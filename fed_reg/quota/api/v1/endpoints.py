"""Quotas endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
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
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize
from fed_reg.quota.api.dependencies import (
    valid_block_storage_quota_id,
    valid_compute_quota_id,
    valid_network_quota_id,
    valid_object_store_quota_id,
    validate_new_block_storage_quota_values,
    validate_new_compute_quota_values,
    validate_new_network_quota_values,
    validate_new_object_store_quota_values,
)
from fed_reg.quota.crud import (
    block_storage_quota_mng,
    compute_quota_mng,
    network_quota_mng,
    object_store_quota_mng,
)
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fed_reg.quota.schemas import (
    BlockStorageQuotaQuery,
    BlockStorageQuotaRead,
    BlockStorageQuotaUpdate,
    ComputeQuotaQuery,
    ComputeQuotaRead,
    ComputeQuotaUpdate,
    NetworkQuotaQuery,
    NetworkQuotaRead,
    NetworkQuotaUpdate,
    ObjectStoreQuotaQuery,
    ObjectStoreQuotaRead,
    ObjectStoreQuotaUpdate,
)
from fed_reg.quota.schemas_extended import (
    BlockStorageQuotaReadMulti,
    BlockStorageQuotaReadSingle,
    ComputeQuotaReadMulti,
    ComputeQuotaReadSingle,
    NetworkQuotaReadMulti,
    NetworkQuotaReadSingle,
    ObjectStoreQuotaReadMulti,
    ObjectStoreQuotaReadSingle,
)

bs_router = APIRouter(prefix="/block_storage_quotas", tags=["block_storage_quotas"])


@bs_router.get(
    "/",
    response_model=BlockStorageQuotaReadMulti,
    summary="Read all quotas",
    description="Retrieve all quotas stored in the database. \
        It is possible to filter on quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_quotas(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: BlockStorageQuotaQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all block storage quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = block_storage_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = block_storage_quota_mng.paginate(
        items=items, page=page.page, size=page.size
    )
    return block_storage_quota_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


# @db.write_transaction
# @bs_router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=BlockStorageQuotaReadExtended,
#
#     summary="Create quota",
#     description="Create a quota and connect it to its related entities: \
#         project and service. \
#         At first verify that target project and service exist. \
#         Then verify project does not already have an equal quota type and \
#         check service and project belong to the same provider.",
# )
# def post_block_storage_quota(
#     project: Project = Depends(valid_project_id),
#     service: Service = Depends(valid_service_id),
#     item: BlockStorageQuotaCreate = Body(),
# ):
#     # Check project does not have duplicated quota types
#     # for q in project.quotas.all():
#     #     if q.type == item.type and q.service.single() == service:
#     #         msg = f"Project '{project.name}' already has a quota "
#     #         msg += f"with type '{item.type}' on service '{service.endpoint}'."
#     #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
#     # Check Project provider and service provider are equals
#     proj_prov = project.provider.single()
#     serv_prov = service.provider.single()
#     if proj_prov != serv_prov:
#         msg = f"Project provider '{proj_prov.name}' and service provider "
#         msg += f"'{serv_prov.name}' do not match."
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

#     return block_storage_quota.create(
#         obj_in=item, project=project, service=service, force=True
#     )


@bs_router.get(
    "/{quota_uid}",
    response_model=BlockStorageQuotaReadSingle,
    summary="Read a specific quota",
    description="Retrieve a specific quota using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_quota(
    size: SchemaSize = Depends(),
    item: BlockStorageQuota = Depends(valid_block_storage_quota_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the block storage quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return block_storage_quota_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@bs_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[BlockStorageQuotaRead],
    dependencies=[
        Depends(validate_new_block_storage_quota_values),
    ],
    summary="Edit a specific quota",
    description="Update attribute values of a specific quota. \
        The target quota is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_block_storage_quota(
    request: Request,
    update_data: BlockStorageQuotaUpdate,
    response: Response,
    item: BlockStorageQuota = Depends(valid_block_storage_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the block storage quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = block_storage_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@bs_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific quota",
    description="Delete a specific quota using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_block_storage_quotas(
    request: Request,
    item: BlockStorageQuota = Depends(valid_block_storage_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the block storage quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not block_storage_quota_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


c_router = APIRouter(prefix="/compute_quotas", tags=["compute_quotas"])


@c_router.get(
    "/",
    response_model=ComputeQuotaReadMulti,
    summary="Read all compute quotas",
    description="Retrieve all compute quotas stored in the database. \
        It is possible to filter on quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_quotas(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ComputeQuotaQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all compute quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = compute_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = compute_quota_mng.paginate(items=items, page=page.page, size=page.size)
    return compute_quota_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


# @db.write_transaction
# @c_router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=ComputeQuotaReadExtended,
#
#     summary="Create compute quota",
#     description="Create a compute quota and connect it to its related entities: \
#         project and service. \
#         At first verify that target project and service exist. \
#         Then verify project does not already have an equal quota type and \
#         check service and project belong to the same provider.",
# )
# def post_compute_quota(
#     project: Project = Depends(valid_project_id),
#     service: Service = Depends(valid_service_id),
#     item: ComputeQuotaCreate = Body(),
# ):
#     # Check project does not have duplicated quota types
#     # for q in project.quotas.all():
#     #     if q.type == item.type and q.service.single() == service:
#     #         msg = f"Project '{project.name}' already has a quota "
#     #         msg += f"with type '{item.type}' on service '{service.endpoint}'."
#     #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
#     # Check Project provider and service provider are equals
#     proj_prov = project.provider.single()
#     serv_prov = service.provider.single()
#     if proj_prov != serv_prov:
#         msg = f"Project provider '{proj_prov.name}' and service provider "
#         msg += f"'{serv_prov.name}' do not match."
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

#     return compute_quota.create(
#         obj_in=item, project=project, service=service, force=True
#     )


@c_router.get(
    "/{quota_uid}",
    response_model=ComputeQuotaReadSingle,
    summary="Read a specific quota",
    description="Retrieve a specific quota using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_quota(
    size: SchemaSize = Depends(),
    item: ComputeQuota = Depends(valid_compute_quota_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the compute quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return compute_quota_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@c_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ComputeQuotaRead],
    dependencies=[
        Depends(validate_new_compute_quota_values),
    ],
    summary="Edit a specific quota",
    description="Update attribute values of a specific quota. \
        The target quota is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_compute_quota(
    request: Request,
    update_data: ComputeQuotaUpdate,
    response: Response,
    item: ComputeQuota = Depends(valid_compute_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the compute quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = compute_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@c_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific quota",
    description="Delete a specific quota using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_compute_quotas(
    request: Request,
    item: ComputeQuota = Depends(valid_compute_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the compute quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not compute_quota_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


n_router = APIRouter(prefix="/network_quotas", tags=["network_quotas"])


@n_router.get(
    "/",
    response_model=NetworkQuotaReadMulti,
    summary="Read all network quotas",
    description="Retrieve all network quotas stored in the database. \
        It is possible to filter on quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_quotas(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: NetworkQuotaQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all network quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = network_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = network_quota_mng.paginate(items=items, page=page.page, size=page.size)
    return network_quota_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@n_router.get(
    "/{quota_uid}",
    response_model=NetworkQuotaReadSingle,
    summary="Read a specific quota",
    description="Retrieve a specific quota using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_quota(
    size: SchemaSize = Depends(),
    item: NetworkQuota = Depends(valid_network_quota_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the network quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return network_quota_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@n_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[NetworkQuotaRead],
    dependencies=[
        Depends(validate_new_network_quota_values),
    ],
    summary="Edit a specific quota",
    description="Update attribute values of a specific quota. \
        The target quota is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_network_quota(
    request: Request,
    update_data: NetworkQuotaUpdate,
    response: Response,
    item: NetworkQuota = Depends(valid_network_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the network quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = network_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@n_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific quota",
    description="Delete a specific quota using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_network_quotas(
    request: Request,
    item: NetworkQuota = Depends(valid_network_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the network quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not network_quota_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


os_router = APIRouter(prefix="/object_store_quotas", tags=["object_store_quotas"])


@os_router.get(
    "/",
    response_model=ObjectStoreQuotaReadMulti,
    summary="Read all quotas",
    description="Retrieve all quotas stored in the database. \
        It is possible to filter on quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_quotas(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ObjectStoreQuotaQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all object storage quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = object_store_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = object_store_quota_mng.paginate(items=items, page=page.page, size=page.size)
    return object_store_quota_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


# @db.write_transaction
# @os_router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=ObjectStoreQuotaReadExtended,
#
#     summary="Create quota",
#     description="Create a quota and connect it to its related entities: \
#         project and service. \
#         At first verify that target project and service exist. \
#         Then verify project does not already have an equal quota type and \
#         check service and project belong to the same provider.",
# )
# def post_object_store_quota(
#     project: Project = Depends(valid_project_id),
#     service: Service = Depends(valid_service_id),
#     item: ObjectStoreQuotaCreate = Body(),
# ):
#     # Check project does not have duplicated quota types
#     # for q in project.quotas.all():
#     #     if q.type == item.type and q.service.single() == service:
#     #         msg = f"Project '{project.name}' already has a quota "
#     #         msg += f"with type '{item.type}' on service '{service.endpoint}'."
#     #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
#     # Check Project provider and service provider are equals
#     proj_prov = project.provider.single()
#     serv_prov = service.provider.single()
#     if proj_prov != serv_prov:
#         msg = f"Project provider '{proj_prov.name}' and service provider "
#         msg += f"'{serv_prov.name}' do not match."
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

#     return object_store_quota.create(
#         obj_in=item, project=project, service=service, force=True
#     )


@os_router.get(
    "/{quota_uid}",
    response_model=ObjectStoreQuotaReadSingle,
    summary="Read a specific quota",
    description="Retrieve a specific quota using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_quota(
    size: SchemaSize = Depends(),
    item: ObjectStoreQuota = Depends(valid_object_store_quota_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the object storage quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return object_store_quota_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@os_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ObjectStoreQuotaRead],
    dependencies=[
        Depends(validate_new_object_store_quota_values),
    ],
    summary="Edit a specific quota",
    description="Update attribute values of a specific quota. \
        The target quota is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message.",
)
@flaat.access_level("write")
@db.write_transaction
def put_object_store_quota(
    request: Request,
    update_data: ObjectStoreQuotaUpdate,
    response: Response,
    item: ObjectStoreQuota = Depends(valid_object_store_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the object storage quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = object_store_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@os_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific quota",
    description="Delete a specific quota using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_object_store_quotas(
    request: Request,
    item: ObjectStoreQuota = Depends(valid_object_store_quota_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the object storage quota matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not object_store_quota_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
