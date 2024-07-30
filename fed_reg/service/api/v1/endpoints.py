"""Services endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
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

# from app.identity_provider.crud import identity_provider
# from app.identity_provider.schemas import (
#     IdentityProviderRead,
#     IdentityProviderReadPublic,
#     IdentityProviderReadShort,
# )
# from app.identity_provider.schemas_extended import (
#     IdentityProviderReadExtended,
#     IdentityProviderReadExtendedPublic,
# )
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize
from fed_reg.service.api.dependencies import (
    valid_block_storage_service_id,
    valid_compute_service_id,
    valid_identity_service_id,
    valid_network_service_id,
    valid_object_store_service_id,
    validate_new_block_storage_service_values,
    validate_new_compute_service_values,
    validate_new_identity_service_values,
    validate_new_network_service_values,
    validate_new_object_store_service_values,
)
from fed_reg.service.crud import (
    block_storage_service_mng,
    compute_service_mng,
    identity_service_mng,
    network_service_mng,
    object_store_service_mng,
)
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fed_reg.service.schemas import (
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
from fed_reg.service.schemas_extended import (
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
)

bs_router = APIRouter(prefix="/block_storage_services", tags=["block_storage_services"])


@bs_router.get(
    "/",
    response_model=BlockStorageServiceReadMulti,
    summary="Read all BlockStorage services",
    description="Retrieve all services stored in the database. \
        It is possible to filter on services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_services(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: BlockStorageServiceQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all block storage services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = block_storage_service_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = block_storage_service_mng.paginate(
        items=items, page=page.page, size=page.size
    )
    return block_storage_service_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@bs_router.get(
    "/{service_uid}",
    response_model=BlockStorageServiceReadSingle,
    summary="Read a specific BlockStorage service",
    description="Retrieve a specific service using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_block_storage_service(
    size: SchemaSize = Depends(),
    item: BlockStorageService = Depends(valid_block_storage_service_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the block storage service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return block_storage_service_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@bs_router.patch(
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[BlockStorageServiceRead],
    dependencies=[
        Depends(validate_new_block_storage_service_values),
    ],
    summary="Edit a specific BlockStorage service",
    description="Update attribute values of a specific service. \
        The target service is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new service values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_block_storage_service(
    request: Request,
    update_data: BlockStorageServiceUpdate,
    response: Response,
    item: BlockStorageService = Depends(valid_block_storage_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the block storage service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = block_storage_service_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@bs_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific BlockStorage service",
    description="Delete a specific service using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related quotas. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_block_storage_services(
    request: Request,
    item: BlockStorageService = Depends(valid_block_storage_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the block storage service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not block_storage_service_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


c_router = APIRouter(prefix="/compute_services", tags=["compute_services"])


@c_router.get(
    "/",
    response_model=ComputeServiceReadMulti,
    summary="Read all Compute services",
    description="Retrieve all services stored in the database. \
        It is possible to filter on services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_services(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ComputeServiceQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all compute services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = compute_service_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = compute_service_mng.paginate(items=items, page=page.page, size=page.size)
    return compute_service_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@c_router.get(
    "/{service_uid}",
    response_model=ComputeServiceReadSingle,
    summary="Read a specific Compute service",
    description="Retrieve a specific service using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_compute_service(
    size: SchemaSize = Depends(),
    item: ComputeService = Depends(valid_compute_service_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the compute service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return compute_service_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@c_router.patch(
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ComputeServiceRead],
    dependencies=[
        Depends(validate_new_compute_service_values),
    ],
    summary="Edit a specific Compute service",
    description="Update attribute values of a specific service. \
        The target service is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new service values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_compute_service(
    request: Request,
    update_data: ComputeServiceUpdate,
    response: Response,
    item: ComputeService = Depends(valid_compute_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the compute service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = compute_service_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@c_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific Compute service",
    description="Delete a specific service using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related quotas. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_compute_services(
    request: Request,
    item: ComputeService = Depends(valid_compute_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the compute service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not compute_service_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


i_router = APIRouter(prefix="/identity_services", tags=["identity_services"])


@i_router.get(
    "/",
    response_model=IdentityServiceReadMulti,
    summary="Read all Identity services",
    description="Retrieve all services stored in the database. \
        It is possible to filter on services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_services(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: IdentityServiceQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all identity services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = identity_service_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = identity_service_mng.paginate(items=items, page=page.page, size=page.size)
    return identity_service_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@i_router.get(
    "/{service_uid}",
    response_model=IdentityServiceReadSingle,
    summary="Read a specific Identity service",
    description="Retrieve a specific service using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_service(
    size: SchemaSize = Depends(),
    item: IdentityService = Depends(valid_identity_service_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the identity service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return identity_service_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@i_router.patch(
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[IdentityServiceRead],
    dependencies=[
        Depends(validate_new_identity_service_values),
    ],
    summary="Edit a specific Identity service",
    description="Update attribute values of a specific service. \
        The target service is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new service values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_identity_service(
    request: Request,
    update_data: IdentityServiceUpdate,
    response: Response,
    item: IdentityService = Depends(valid_identity_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the identity service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = identity_service_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@i_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific Identity service",
    description="Delete a specific service using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related quotas. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_identity_services(
    request: Request,
    item: IdentityService = Depends(valid_identity_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the identity service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not identity_service_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


n_router = APIRouter(prefix="/network_services", tags=["network_services"])


@n_router.get(
    "/",
    response_model=NetworkServiceReadMulti,
    summary="Read all Network services",
    description="Retrieve all services stored in the database. \
        It is possible to filter on services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_services(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: NetworkServiceQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all network services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = network_service_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = network_service_mng.paginate(items=items, page=page.page, size=page.size)
    return network_service_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@n_router.get(
    "/{service_uid}",
    response_model=NetworkServiceReadSingle,
    summary="Read a specific Network service",
    description="Retrieve a specific service using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_network_service(
    size: SchemaSize = Depends(),
    item: NetworkService = Depends(valid_network_service_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the network service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return network_service_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@n_router.patch(
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[NetworkServiceRead],
    dependencies=[
        Depends(validate_new_network_service_values),
    ],
    summary="Edit a specific Network service",
    description="Update attribute values of a specific service. \
        The target service is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new service values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_network_service(
    request: Request,
    update_data: NetworkServiceUpdate,
    response: Response,
    item: NetworkService = Depends(valid_network_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the network service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = network_service_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@n_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific Network service",
    description="Delete a specific service using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related quotas. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_network_services(
    request: Request,
    item: NetworkService = Depends(valid_network_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the network service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not network_service_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


os_router = APIRouter(prefix="/object_store_services", tags=["object_store_services"])


@os_router.get(
    "/",
    response_model=ObjectStoreServiceReadMulti,
    summary="Read all ObjectStore services",
    description="Retrieve all services stored in the database. \
        It is possible to filter on services attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_services(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ObjectStoreServiceQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all object storage services.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = object_store_service_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = object_store_service_mng.paginate(
        items=items, page=page.page, size=page.size
    )
    return object_store_service_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@os_router.get(
    "/{service_uid}",
    response_model=ObjectStoreServiceReadSingle,
    summary="Read a specific ObjectStore service",
    description="Retrieve a specific service using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_object_store_service(
    size: SchemaSize = Depends(),
    item: ObjectStoreService = Depends(valid_object_store_service_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the object storage service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return object_store_service_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@os_router.patch(
    "/{service_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ObjectStoreServiceRead],
    dependencies=[
        Depends(validate_new_object_store_service_values),
    ],
    summary="Edit a specific ObjectStore service",
    description="Update attribute values of a specific service. \
        The target service is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new service values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_object_store_service(
    request: Request,
    update_data: ObjectStoreServiceUpdate,
    response: Response,
    item: ObjectStoreService = Depends(valid_object_store_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the object storage service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = object_store_service_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@os_router.delete(
    "/{service_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific ObjectStore service",
    description="Delete a specific service using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related quotas. \
        If the deletion procedure fails, raises a `internal \
        server` error",
)
@flaat.access_level("write")
@db.write_transaction
def delete_object_store_services(
    request: Request,
    item: ObjectStoreService = Depends(valid_object_store_service_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the object storage service matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not object_store_service_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


# @db.read_transaction
# @router.get(
#     "/{service_uid}/identity_providers",
#     response_model=     list[IdentityProviderReadExtended]|
#         list[IdentityProviderRead]|
#         list[IdentityProviderReadShort]|
#         list[IdentityProviderReadExtendedPublic]|
#         list[IdentityProviderReadPublic],
#     summary="Read service accessible identity providers",
#     description="Retrieve all the identity providers the \
#         service has access to. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error.",
# )
# def get_service_identity_providers(
#     auth: bool = Depends(check_read_access),
#     size: SchemaSize = Depends(),
#     item: Service = Depends(valid_service_id),
# ):
#     items = item.provider.single().identity_providers.all()
#     return identity_provider.choose_out_schema(
#         items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
#     )
