"""Provider endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
from typing import Optional

# from app.service.api.dependencies import valid_service_endpoint
# from app.service.crud import (
#     block_storage_service,
#     compute_service,
#     identity_service,
#     network_service,
# )
# from app.service.schemas import (
#     BlockStorageServiceCreate,
#     ComputeServiceCreate,
#     IdentityServiceCreate,
#     NetworkServiceCreate,
# )
# from app.service.schemas_extended import (
#     BlockStorageServiceReadExtended,
#     ComputeServiceReadExtended,
#     IdentityServiceReadExtended,
# )
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

# from app.auth_method.schemas import AuthMethodCreate
# from app.identity_provider.api.dependencies import (
#     valid_identity_provider_endpoint,
#     valid_identity_provider_id,
# )
# from app.identity_provider.crud import identity_provider
# from app.identity_provider.models import IdentityProvider
# from app.identity_provider.schemas import IdentityProviderCreate
# from app.identity_provider.schemas_extended import IdentityProviderReadExtended
# from app.project.api.dependencies import valid_project_name, valid_project_uuid
# from app.project.crud import project
# from app.project.schemas import ProjectCreate
# from app.project.schemas_extended import ProjectReadExtended
from fed_reg.provider.api.dependencies import (
    valid_provider,
    valid_provider_id,
    validate_new_provider_values,
)
from fed_reg.provider.crud import provider_mng
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas import (
    ProviderQuery,
    ProviderRead,
    ProviderUpdate,
)
from fed_reg.provider.schemas_extended import (
    ProviderCreateExtended,
    ProviderReadExtended,
    ProviderReadMulti,
    ProviderReadSingle,
)
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get(
    "/",
    response_model=ProviderReadMulti,
    summary="Read all providers",
    description="Retrieve all providers stored in the database. \
        It is possible to filter on providers attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
async def get_providers(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: ProviderQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all providers.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = provider_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = provider_mng.paginate(items=items, page=page.page, size=page.size)
    return provider_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProviderReadExtended,
    dependencies=[Depends(valid_provider)],
    summary="Create provider",
    description="Create a provider and its related entities: \
        flavors, identity providers, images, location, \
        projects and services. \
        At first validate new provider values checking there are \
        no other items with the given *name*. \
        Moreover check the received lists do not contain duplicates.",
)
@flaat.access_level("write")
@db.write_transaction
def post_provider(
    request: Request,
    item: ProviderCreateExtended,
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """POST operation to create a new provider and all its related items.

    The endpoints expect an object with a provider information all the new related
    entities' data to add to the DB.

    Only authenticated users can view this function.
    """
    return provider_mng.create(obj_in=item)


@router.get(
    "/{provider_uid}",
    response_model=ProviderReadSingle,
    summary="Read a specific provider",
    description="Retrieve a specific provider using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_provider(
    size: SchemaSize = Depends(),
    item: Provider = Depends(valid_provider_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return provider_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{provider_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ProviderRead],
    dependencies=[
        Depends(validate_new_provider_values),
    ],
    summary="Edit a specific provider",
    description="Update attribute values of a specific provider. \
        The target provider is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new provider values checking there are \
        no other items with the given *name* and *type*.",
)
@flaat.access_level("write")
@db.write_transaction
def patch_provider(
    request: Request,
    update_data: ProviderUpdate,
    response: Response,
    item: Provider = Depends(valid_provider_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = provider_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.put(
    "/{provider_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[ProviderReadExtended],
    dependencies=[
        Depends(validate_new_provider_values),
    ],
    summary="Edit a specific provider and all nested relationships and items",
    description="Update attribute values of a specific provider. \
        The target provider is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new provider values checking there are \
        no other items with the given *name* and *type*. \
        Recursively update relationships and related nodes.",
)
@flaat.access_level("write")
@db.write_transaction
def put_provider(
    request: Request,
    update_data: ProviderCreateExtended,
    response: Response,
    item: Provider = Depends(valid_provider_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PUT operation to update the provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = provider_mng.update(db_obj=item, obj_in=update_data, force=True)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{provider_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific provider",
    description="Delete a specific provider using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related flavors, images, projects \
        and services.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_providers(
    request: Request,
    item: Provider = Depends(valid_provider_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not provider_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


# @db.write_transaction
# @router.post(
#    "/{provider_uid}/flavors/",
#    response_model=FlavorReadExtended,
#    status_code=status.HTTP_201_CREATED,
#    dependencies=[
#
#        Depends(valid_flavor_name),
#        Depends(valid_flavor_uuid),
#    ],
#    summary="Add new flavor to provider",
#    description="Create a flavor and connect it to a \
#        provider knowing it *uid*. \
#        If no entity matches the given *uid*, the endpoint \
#        raises a `not found` error. \
#        At first validate new flavor values checking there are \
#        no other items with the given *name* or *uuid*.",
# )
# def add_flavor_to_provider(
#    item: FlavorCreate,
#    provider: Provider = Depends(valid_provider_id),
# ):
#    return flavor.create(obj_in=item, provider=provider, force=True)
#


# @db.write_transaction
# @router.post(
#     "/{provider_uid}/identity_providers/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=IdentityProviderReadExtended,
#     dependencies=[
#
#         Depends(valid_identity_provider_endpoint),
#     ],
#     summary="Create location",
#     description="Create a location. \
#         At first validate new location values checking there are \
#         no other items with the given *name*.",
# )
# def post_location(item: IdentityProviderCreate):
#     return identity_provider.create(obj_in=item, force=True)


# @db.write_transaction
# @router.put(
#     "/{provider_uid}/identity_providers/{identity_provider_uid}",
#     response_model=Optional[ProviderReadExtended],
#
#     summary="Connect provider to identity provider",
#     description="Connect a provider to a specific identity \
#         provider knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def connect_provider_to_identity_providers(
#     data: AuthMethodCreate,
#     response: Response,
#     item: Provider = Depends(valid_provider_id),
#     identity_provider: IdentityProvider = Depends(valid_identity_provider_id),
# ):
#     if item.identity_providers.is_connected(identity_provider):
#         db_item = item.identity_providers.relationship(identity_provider)
#         if all(
#             [
#                 db_item.__getattribute__(k) == v
#                 for k, v in data.dict(exclude_unset=True).items()
#             ]
#         ):
#             response.status_code = status.HTTP_304_NOT_MODIFIED
#             return None
#         item.identity_providers.disconnect(identity_provider)
#     item.identity_providers.connect(identity_provider, data.dict())
#     return item


# @db.write_transaction
# @router.delete(
#     "/{provider_uid}/identity_providers/{identity_provider_uid}",
#     response_model=Optional[ProviderReadExtended],
#
#     summary="Disconnect provider from identity provider",
#     description="Disconnect a provider from a specific identity \
#         provider knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def disconnect_provider_from_identity_providers(
#     response: Response,
#     item: Provider = Depends(valid_provider_id),
#     identity_provider: IdentityProvider = Depends(valid_identity_provider_id),
# ):
#     if not item.identity_providers.is_connected(identity_provider):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.identity_providers.disconnect(identity_provider)
#     return item


# @db.write_transaction
# @router.post(
#    "/{provider_uid}/images/",
#    response_model=ImageReadExtended,
#    status_code=status.HTTP_201_CREATED,
#    dependencies=[
#
#        Depends(valid_image_name),
#        Depends(valid_image_uuid),
#    ],
#    summary="Add new image to provider",
#    description="Create a image and connect it to a \
#        provider knowing it *uid*. \
#        If no entity matches the given *uid*, the endpoint \
#        raises a `not found` error. \
#        At first validate new image values checking there are \
#        no other items with the given *name* or *uuid*.",
# )
# def add_image_to_provider(
#    item: ImageCreate,
#    provider: Provider = Depends(valid_provider_id),
# ):
#    return image.create(obj_in=item, provider=provider, force=True)


# @db.write_transaction
# @router.post(
#     "/{provider_uid}/projects/",
#     response_model=ProjectReadExtended,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[
#
#         Depends(valid_project_name),
#         Depends(valid_project_uuid),
#     ],
#     summary="Add new project to provider",
#     description="Create a project and connect it to a \
#         provider knowing it *uid*. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error. \
#         At first validate new project values checking there are \
#         no other items with the given *name* or *uuid*.",
# )
# def add_project_to_provider(
#     item: ProjectCreate,
#     provider: Provider = Depends(valid_provider_id),
# ):
#     return project.create(obj_in=item, provider=provider, force=True)


# @db.write_transaction
# @router.post(
#     "/{provider_uid}/services/",
#     response_model=         BlockStorageServiceReadExtended|
#         IdentityServiceReadExtended|
#         ComputeServiceReadExtended,
#     status_code=status.HTTP_201_CREATED,
#       # , Depends(valid_service_endpoint)],
#     summary="Add new service to provider",
#     description="Create a service and connect it to a \
#         provider knowing it *uid*. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error. \
#         At first validate new service values checking there are \
#         no other items with the given *name* or *uuid*.",
# )
# def add_service_to_provider(
#     item: BlockStorageServiceCreate|
#         IdentityServiceCreate|
#         ComputeServiceCreate|
#         NetworkServiceCreate,
#     provider: Provider = Depends(valid_provider_id),
# ):
#     if isinstance(item, BlockStorageServiceCreate):
#         return block_storage_service.create(obj_in=item, provider=provider,
# force=True)
#     if isinstance(item, ComputeServiceCreate):
#         return compute_service.create(obj_in=item, provider=provider, force=True)
#     if isinstance(item, IdentityServiceCreate):
#         return identity_service.create(obj_in=item, provider=provider, force=True)
#     if isinstance(item, NetworkServiceCreate):
#         return network_service.create(obj_in=item, provider=provider, force=True)
