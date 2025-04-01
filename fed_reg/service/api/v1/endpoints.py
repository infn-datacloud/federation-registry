"""Services endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fedreg.service.schemas import (
    BlockStorageServiceQuery,
    BlockStorageServiceRead,
    BlockStorageServiceUpdate,
    ComputeServiceQuery,
    ComputeServiceRead,
    ComputeServiceUpdate,
    IdentityServiceQuery,
    IdentityServiceRead,
    IdentityServiceUpdate,
    NetworkServiceQuery,
    NetworkServiceRead,
    NetworkServiceUpdate,
    ObjectStoreServiceQuery,
    ObjectStoreServiceRead,
    ObjectStoreServiceUpdate,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate
from fed_reg.service.api.dependencies import (
    block_storage_service_must_exist,
    compute_service_must_exist,
    get_block_storage_service_item,
    get_compute_service_item,
    get_identity_service_item,
    get_network_service_item,
    get_object_store_service_item,
    identity_service_must_exist,
    network_service_must_exist,
    object_store_service_must_exist,
    validate_new_block_storage_service_values,
    validate_new_compute_service_values,
    validate_new_identity_service_values,
    validate_new_network_service_values,
    validate_new_object_store_service_values,
)
from fed_reg.service.api.utils import (
    BlockStorageServiceReadMulti,
    BlockStorageServiceReadSingle,
    ComputeServiceReadMulti,
    ComputeServiceReadSingle,
    IdentityServiceReadMulti,
    IdentityServiceReadSingle,
    NetworkServiceReadMulti,
    NetworkServiceReadSingle,
    ObjectStoreServiceReadMulti,
    ObjectStoreServiceReadSingle,
    choose_block_storage_schema,
    choose_compute_schema,
    choose_identity_schema,
    choose_network_schema,
    choose_object_store_schema,
)
from fed_reg.service.crud import (
    block_storage_service_mng,
    compute_service_mng,
    identity_service_mng,
    network_service_mng,
    object_store_service_mng,
)

bs_router = APIRouter(prefix="/block_storage_services", tags=["block_storage_services"])


@bs_router.get(
    "/",
    response_model=BlockStorageServiceReadMulti,
    summary="Read all block_storage_services",
    description="Retrieve all block_storage_services stored in the database. \
        It is possible to filter on block_storage_services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_services(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[BlockStorageServiceQuery, Depends()],
):
    """GET operation to retrieve all block_storage_services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = block_storage_service_mng.get_multi(
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
    "/{service_uid}",
    response_model=BlockStorageServiceReadSingle,
    summary="Read a specific block_storage_service",
    description="Retrieve a specific block_storage_service using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_service(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[BlockStorageService, Depends(block_storage_service_must_exist)],
):
    """GET operation to retrieve the block_storage_service matching a specific uid.

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
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=BlockStorageServiceRead | None,
    summary="Patch only specific attribute of the target block_storage_service",
    description="Update only the received attribute values of a specific block storage \
        service. The target block_storage_service is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new block_storage_service values checking \
        there are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_block_storage_service(
    response: Response,
    validated_data: Annotated[
        tuple[BlockStorageService, BlockStorageServiceUpdate],
        Depends(validate_new_block_storage_service_values),
    ],
):
    """PATCH operation to update the block_storage_service matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = block_storage_service_mng.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@bs_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific block_storage_service",
    description="Delete a specific block_storage_service using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_block_storage_services(
    item: Annotated[BlockStorageService, Depends(get_block_storage_service_item)],
):
    """DELETE operation to remove the block_storage_service matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        block_storage_service_mng.remove(db_obj=item)


# @db.write_transaction
# @bs_router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=BlockStorageServiceReadExtended,
#
#     summary="Create service",
#     description="Create a service and connect it to its related entities: \
#         project and service. \
#         At first verify that target project and service exist. \
#         Then verify project does not already have an equal service type and \
#         check service and project belong to the same provider.",
# )
# def post_block_storage_service(
#     project: Project = Depends(valid_project_id),
#     service: Service = Depends(valid_service_id),
#     item: BlockStorageServiceCreate = Body(),
# ):
#     # Check project does not have duplicated service types
#     # for q in project.services.all():
#     #     if q.type == item.type and q.service.single() == service:
#     #         msg = f"Project '{project.name}' already has a service "
#     #         msg += f"with type '{item.type}' on service '{service.endpoint}'."
#     #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
#     # Check Project provider and service provider are equals
#     proj_prov = project.provider.single()
#     serv_prov = service.provider.single()
#     if proj_prov != serv_prov:
#         msg = f"Project provider '{proj_prov.name}' and service provider "
#         msg += f"'{serv_prov.name}' do not match."
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

#     return block_storage_service.create(
#         obj_in=item, project=project, service=service, force=True
#     )


c_router = APIRouter(prefix="/compute_services", tags=["compute_services"])


@c_router.get(
    "/",
    response_model=ComputeServiceReadMulti,
    summary="Read all compute_services",
    description="Retrieve all compute_services stored in the database. \
        It is possible to filter on compute_services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_services(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ComputeServiceQuery, Depends()],
):
    """GET operation to retrieve all compute_services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = compute_service_mng.get_multi(
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
    "/{service_uid}",
    response_model=ComputeServiceReadSingle,
    summary="Read a specific compute_service",
    description="Retrieve a specific compute_service using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_service(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ComputeService, Depends(compute_service_must_exist)],
):
    """GET operation to retrieve the compute_service matching a specific uid.

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
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ComputeServiceRead | None,
    summary="Patch only specific attribute of the target compute_service",
    description="Update only the received attribute values of a specific compute \
        service. The target compute_service is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new compute_service values checking there \
        are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_compute_service(
    response: Response,
    validated_data: Annotated[
        tuple[ComputeService, ComputeServiceUpdate],
        Depends(validate_new_compute_service_values),
    ],
):
    """PATCH operation to update the compute_service matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = compute_service_mng.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@c_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific compute_service",
    description="Delete a specific compute_service using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_compute_services(
    item: Annotated[ComputeService, Depends(get_compute_service_item)],
):
    """DELETE operation to remove the compute_service matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        compute_service_mng.remove(db_obj=item)


i_router = APIRouter(prefix="/identity_services", tags=["identity_services"])


@i_router.get(
    "/",
    response_model=IdentityServiceReadMulti,
    summary="Read all identity_services",
    description="Retrieve all identity_services stored in the database. \
        It is possible to filter on identity_services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_services(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[IdentityServiceQuery, Depends()],
):
    """GET operation to retrieve all identity_services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = identity_service_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_identity_schema(
        items,
        auth=user_infos is not None,
        short=shape.short,
        with_conn=shape.with_conn,
    )


@i_router.get(
    "/{service_uid}",
    response_model=IdentityServiceReadSingle,
    summary="Read a specific identity_service",
    description="Retrieve a specific identity_service using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_service(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[IdentityService, Depends(identity_service_must_exist)],
):
    """GET operation to retrieve the identity_service matching a specific uid.

    The endpoint expects a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - shape: parameters to define the number of information contained in each result.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    return choose_identity_schema(
        item, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@i_router.patch(
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=IdentityServiceRead | None,
    summary="Patch only specific attribute of the target identity_service",
    description="Update only the received attribute values of a specific identity \
        service. The target identity_service is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new identity_service values checking there \
        are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_identity_service(
    response: Response,
    validated_data: Annotated[
        tuple[IdentityService, IdentityServiceUpdate],
        Depends(validate_new_identity_service_values),
    ],
):
    """PATCH operation to update the identity_service matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = identity_service_mng.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@i_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific identity_service",
    description="Delete a specific identity_service using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_identity_services(
    item: Annotated[IdentityService, Depends(get_identity_service_item)],
):
    """DELETE operation to remove the identity_service matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        identity_service_mng.remove(db_obj=item)


n_router = APIRouter(prefix="/network_services", tags=["network_services"])


@n_router.get(
    "/",
    response_model=NetworkServiceReadMulti,
    summary="Read all network_services",
    description="Retrieve all network_services stored in the database. \
        It is possible to filter on network_services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_services(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[NetworkServiceQuery, Depends()],
):
    """GET operation to retrieve all network_services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = network_service_mng.get_multi(
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
    "/{service_uid}",
    response_model=NetworkServiceReadSingle,
    summary="Read a specific network_service",
    description="Retrieve a specific network_service using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_service(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[NetworkService, Depends(network_service_must_exist)],
):
    """GET operation to retrieve the network_service matching a specific uid.

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
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=NetworkServiceRead | None,
    summary="Patch only specific attribute of the target network_service",
    description="Update only the received attribute values of a specific network \
        service. The target network_service is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new network_service values checking there \
        are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_network_service(
    response: Response,
    validated_data: Annotated[
        tuple[NetworkService, NetworkServiceUpdate],
        Depends(validate_new_network_service_values),
    ],
):
    """PATCH operation to update the network_service matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = network_service_mng.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@n_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific network_service",
    description="Delete a specific network_service using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_network_services(
    item: Annotated[NetworkService, Depends(get_network_service_item)],
):
    """DELETE operation to remove the network_service matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        network_service_mng.remove(db_obj=item)


os_router = APIRouter(prefix="/object_store_services", tags=["object_store_services"])


@os_router.get(
    "/",
    response_model=ObjectStoreServiceReadMulti,
    summary="Read all object_store_services",
    description="Retrieve all object_store_services stored in the database. \
        It is possible to filter on object_store_services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_services(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ObjectStoreServiceQuery, Depends()],
):
    """GET operation to retrieve all object_store_services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = object_store_service_mng.get_multi(
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
    "/{service_uid}",
    response_model=ObjectStoreServiceReadSingle,
    summary="Read a specific object_store_service",
    description="Retrieve a specific object_store_service using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_service(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ObjectStoreService, Depends(object_store_service_must_exist)],
):
    """GET operation to retrieve the object_store_service matching a specific uid.

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
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ObjectStoreServiceRead | None,
    summary="Patch only specific attribute of the target object_store_service",
    description="Update only the received attribute values of a specific object store \
        service. The target object_store_service is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. At \
        first, the endpoint validates the new object_store_service values checking \
        there are no other items with the given *uuid* and *name*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_object_store_service(
    response: Response,
    validated_data: Annotated[
        tuple[ObjectStoreService, ObjectStoreServiceUpdate],
        Depends(validate_new_object_store_service_values),
    ],
):
    """PATCH operation to update the object_store_service matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = object_store_service_mng.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@os_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific object_store_service",
    description="Delete a specific object_store_service using its *uid*. Returns \
        `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_object_store_services(
    item: Annotated[ObjectStoreService, Depends(get_object_store_service_item)],
):
    """DELETE operation to remove the object_store_service matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        object_store_service_mng.remove(db_obj=item)
