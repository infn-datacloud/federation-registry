"""Provider endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from fastapi.security import HTTPBasicCredentials
from fedreg.provider.models import Provider
from fedreg.provider.schemas import ProviderQuery, ProviderRead, ProviderUpdate
from fedreg.provider.schemas_extended import (
    ProviderCreateExtended,
    ProviderReadExtended,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security
from fed_reg.provider.api.dependencies import (
    get_provider_item,
    provider_must_exist,
    provider_must_not_exist,
    validate_new_provider_values,
)
from fed_reg.provider.api.utils import (
    ProviderReadMulti,
    ProviderReadSingle,
    choose_schema,
)
from fed_reg.provider.crud import provider_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

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
def get_providers(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[ProviderQuery, Depends()],
):
    """GET operation to retrieve all providers.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = provider_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = paginate(items=items, page=page.page, size=page.size)
    return choose_schema(
        items, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@router.get(
    "/{provider_uid}",
    response_model=ProviderReadSingle,
    summary="Read a specific provider",
    description="Retrieve a specific provider using its *uid*. If no entity matches \
        the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_provider(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[Provider, Depends(provider_must_exist)],
):
    """GET operation to retrieve the provider matching a specific uid.

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
    "/{provider_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ProviderRead | None,
    summary="Patch only specific attribute of the target provider",
    description="Update only the received attribute values of a specific provider. The \
        target provider is identified using its *uid*. If no entity matches the given \
        *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new provider values checking there are no other items with the \
        given *uuid* and *name*. In that case, the endpoint raises the `conflict` \
        error. If there are no differences between new values and current ones, the \
        database entity is left unchanged and the endpoint returns the `not modified` \
        message.",
)
@flaat.access_level("write")
@db.write_transaction
def patch_provider(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    response: Response,
    validated_data: Annotated[
        tuple[Provider, ProviderUpdate], Depends(validate_new_provider_values)
    ],
):
    """PATCH operation to update the provider matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = provider_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{provider_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific provider",
    description="Delete a specific provider using its *uid*. Returns `no content`.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_providers(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    item: Annotated[Provider, Depends(get_provider_item)],
):
    """DELETE operation to remove the provider matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    provider_mgr.remove(db_obj=item)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProviderReadExtended,
    dependencies=[],
    summary="Create provider",
    description="Create a provider and its related entities: flavors, identity \
        providers, images, provider, projects and services. At first validate new \
        provider values checking there are no other items with the given *name*. \
        Moreover check the received lists do not contain duplicates.",
)
@flaat.access_level("write")
@db.write_transaction
def post_provider(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    item: Annotated[ProviderCreateExtended, Depends(provider_must_not_exist)],
):
    """POST operation to create a new provider and all its related items.

    The endpoints expect an object with a provider information all the new related
    entities' data to add to the DB.

    Only authenticated users can view this function.
    """
    return provider_mgr.create(obj_in=item)


@router.put(
    "/{provider_uid}",
    status_code=status.HTTP_200_OK,
    response_model=ProviderReadExtended | None,
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
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
    response: Response,
    validated_data: Annotated[
        tuple[Provider, ProviderCreateExtended], Depends(validate_new_provider_values)
    ],
):
    """PUT operation to update the provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = provider_mgr.update(db_obj=item, obj_in=update_data, force=True)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


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
#     summary="Create provider",
#     description="Create a provider. \
#         At first validate new provider values checking there are \
#         no other items with the given *name*.",
# )
# def post_provider(item: IdentityProviderCreate):
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
