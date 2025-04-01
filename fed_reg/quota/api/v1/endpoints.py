"""Quotas endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fedreg.quota.schemas import (
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
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate
from fed_reg.quota.api.dependencies import (
    block_storage_quota_must_exist,
    compute_quota_must_exist,
    get_block_storage_quota_item,
    get_compute_quota_item,
    get_network_quota_item,
    get_object_store_quota_item,
    network_quota_must_exist,
    object_store_quota_must_exist,
    validate_new_block_storage_quota_values,
    validate_new_compute_quota_values,
    validate_new_network_quota_values,
    validate_new_object_store_quota_values,
)
from fed_reg.quota.api.utils import (
    BlockStorageQuotaReadMulti,
    BlockStorageQuotaReadSingle,
    ComputeQuotaReadMulti,
    ComputeQuotaReadSingle,
    NetworkQuotaReadMulti,
    NetworkQuotaReadSingle,
    ObjectStoreQuotaReadMulti,
    ObjectStoreQuotaReadSingle,
    choose_block_storage_schema,
    choose_compute_schema,
    choose_network_schema,
    choose_object_store_schema,
)
from fed_reg.quota.crud import (
    block_storage_quota_mng,
    compute_quota_mng,
    network_quota_mng,
    object_store_quota_mng,
)

bs_router = APIRouter(prefix="/block_storage_quotas", tags=["block_storage_quotas"])


@bs_router.get(
    "/",
    response_model=BlockStorageQuotaReadMulti,
    summary="Read all block_storage_quotas",
    description="Retrieve all block_storage_quotas stored in the database. \
        It is possible to filter on block_storage_quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_quotas(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[BlockStorageQuotaQuery, Depends()],
):
    """GET operation to retrieve all block_storage_quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = block_storage_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_block_storage_schema(
        items,
        auth=user_infos is not None,
        short=shape.short,
        with_conn=shape.with_conn,
    )


@bs_router.get(
    "/{quota_uid}",
    response_model=BlockStorageQuotaReadSingle,
    summary="Read a specific block_storage_quota",
    description="Retrieve a specific block_storage_quota using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_quota(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[BlockStorageQuota, Depends(block_storage_quota_must_exist)],
):
    """GET operation to retrieve the block_storage_quota matching a specific uid.

    The endpoint expects a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - shape: parameters to define the number of information contained in each result.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    return choose_block_storage_schema(
        item, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@bs_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=BlockStorageQuotaRead | None,
    summary="Patch only specific attribute of the target block_storage_quota",
    description="Update only the received attribute values of a specific block storage \
        quota. The target block_storage_quota is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new block_storage_quota values checking \
        there are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_block_storage_quota(
    response: Response,
    validated_data: Annotated[
        tuple[BlockStorageQuota, BlockStorageQuotaUpdate],
        Depends(validate_new_block_storage_quota_values),
    ],
):
    """PATCH operation to update the block_storage_quota matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = block_storage_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@bs_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific block_storage_quota",
    description="Delete a specific block_storage_quota using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_block_storage_quotas(
    item: Annotated[BlockStorageQuota, Depends(get_block_storage_quota_item)],
):
    """DELETE operation to remove the block_storage_quota matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        block_storage_quota_mng.remove(db_obj=item)


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


c_router = APIRouter(prefix="/compute_quotas", tags=["compute_quotas"])


@c_router.get(
    "/",
    response_model=ComputeQuotaReadMulti,
    summary="Read all compute_quotas",
    description="Retrieve all compute_quotas stored in the database. \
        It is possible to filter on compute_quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_quotas(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ComputeQuotaQuery, Depends()],
):
    """GET operation to retrieve all compute_quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = compute_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_compute_schema(
        items,
        auth=user_infos is not None,
        short=shape.short,
        with_conn=shape.with_conn,
    )


@c_router.get(
    "/{quota_uid}",
    response_model=ComputeQuotaReadSingle,
    summary="Read a specific compute_quota",
    description="Retrieve a specific compute_quota using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_quota(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ComputeQuota, Depends(compute_quota_must_exist)],
):
    """GET operation to retrieve the compute_quota matching a specific uid.

    The endpoint expects a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - shape: parameters to define the number of information contained in each result.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    return choose_compute_schema(
        item, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@c_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ComputeQuotaRead | None,
    summary="Patch only specific attribute of the target compute_quota",
    description="Update only the received attribute values of a specific compute \
        quota. The target compute_quota is identified using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.  At first, \
        the endpoint validates the new compute_quota values checking there are no \
        other items with the given *uuid* and *name*. In that case, the endpoint \
        raises the `conflict` error. If there are no differences between new values \
        and current ones, the database entity is left unchanged and the endpoint \
        returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_compute_quota(
    response: Response,
    validated_data: Annotated[
        tuple[ComputeQuota, ComputeQuotaUpdate],
        Depends(validate_new_compute_quota_values),
    ],
):
    """PATCH operation to update the compute_quota matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = compute_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@c_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific compute_quota",
    description="Delete a specific compute_quota using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_compute_quotas(
    item: Annotated[ComputeQuota, Depends(get_compute_quota_item)],
):
    """DELETE operation to remove the compute_quota matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        compute_quota_mng.remove(db_obj=item)


n_router = APIRouter(prefix="/network_quotas", tags=["network_quotas"])


@n_router.get(
    "/",
    response_model=NetworkQuotaReadMulti,
    summary="Read all network_quotas",
    description="Retrieve all network_quotas stored in the database. \
        It is possible to filter on network_quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_quotas(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[NetworkQuotaQuery, Depends()],
):
    """GET operation to retrieve all network_quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = network_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_network_schema(
        items,
        auth=user_infos is not None,
        short=shape.short,
        with_conn=shape.with_conn,
    )


@n_router.get(
    "/{quota_uid}",
    response_model=NetworkQuotaReadSingle,
    summary="Read a specific network_quota",
    description="Retrieve a specific network_quota using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_quota(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[NetworkQuota, Depends(network_quota_must_exist)],
):
    """GET operation to retrieve the network_quota matching a specific uid.

    The endpoint expects a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - shape: parameters to define the number of information contained in each result.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    return choose_network_schema(
        item, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@n_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=NetworkQuotaRead | None,
    summary="Patch only specific attribute of the target network_quota",
    description="Update only the received attribute values of a specific network \
        quota. The target network_quota is identified using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.  At first, \
        the endpoint validates the new network_quota values checking there are no \
        other items with the given *uuid* and *name*. In that case, the endpoint \
        raises the `conflict` error. If there are no differences between new values \
        and current ones, the database entity is left unchanged and the endpoint \
        returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_network_quota(
    response: Response,
    validated_data: Annotated[
        tuple[NetworkQuota, NetworkQuotaUpdate],
        Depends(validate_new_network_quota_values),
    ],
):
    """PATCH operation to update the network_quota matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = network_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@n_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific network_quota",
    description="Delete a specific network_quota using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_network_quotas(
    item: Annotated[NetworkQuota, Depends(get_network_quota_item)],
):
    """DELETE operation to remove the network_quota matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        network_quota_mng.remove(db_obj=item)


os_router = APIRouter(prefix="/object_store_quotas", tags=["object_store_quotas"])


@os_router.get(
    "/",
    response_model=ObjectStoreQuotaReadMulti,
    summary="Read all object_store_quotas",
    description="Retrieve all object_store_quotas stored in the database. \
        It is possible to filter on object_store_quotas attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_quotas(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ObjectStoreQuotaQuery, Depends()],
):
    """GET operation to retrieve all object_store_quotas.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = object_store_quota_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_object_store_schema(
        items,
        auth=user_infos is not None,
        short=shape.short,
        with_conn=shape.with_conn,
    )


@os_router.get(
    "/{quota_uid}",
    response_model=ObjectStoreQuotaReadSingle,
    summary="Read a specific object_store_quota",
    description="Retrieve a specific object_store_quota using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_quota(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ObjectStoreQuota, Depends(object_store_quota_must_exist)],
):
    """GET operation to retrieve the object_store_quota matching a specific uid.

    The endpoint expects a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - shape: parameters to define the number of information contained in each result.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    return choose_object_store_schema(
        item, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@os_router.patch(
    "/{quota_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ObjectStoreQuotaRead | None,
    summary="Patch only specific attribute of the target object_store_quota",
    description="Update only the received attribute values of a specific object store \
        quota. The target object_store_quota is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new object_store_quota values checking there \
        are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_object_store_quota(
    response: Response,
    validated_data: Annotated[
        tuple[ObjectStoreQuota, ObjectStoreQuotaUpdate],
        Depends(validate_new_object_store_quota_values),
    ],
):
    """PATCH operation to update the object_store_quota matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = object_store_quota_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@os_router.delete(
    "/{quota_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific object_store_quota",
    description="Delete a specific object_store_quota using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_object_store_quotas(
    item: Annotated[ObjectStoreQuota, Depends(get_object_store_quota_item)],
):
    """DELETE operation to remove the object_store_quota matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        object_store_quota_mng.remove(db_obj=item)
