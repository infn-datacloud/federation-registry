"""Identity Provider endpoints to execute POST, GET, PUT, PATCH, DELETE operations."""
from typing import Optional

# from app.user_group.api.dependencies import is_unique_user_group
# from app.user_group.crud import user_group
# from app.user_group.schemas import UserGroupCreate
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
from fedreg.identity_provider.models import IdentityProvider
from fedreg.identity_provider.schemas import (
    IdentityProviderQuery,
    IdentityProviderRead,
    IdentityProviderUpdate,
)
from fedreg.identity_provider.schemas_extended import (
    IdentityProviderReadMulti,
    IdentityProviderReadSingle,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security

# from app.auth_method.schemas import AuthMethodCreate
from fed_reg.identity_provider.api.dependencies import (
    valid_identity_provider_id,
    validate_new_identity_provider_values,
)
from fed_reg.identity_provider.crud import identity_provider_mng

# from app.project.schemas_extended import UserGroupReadExtended
# from app.provider.api.dependencies import valid_provider_id
# from app.provider.models import Provider
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize

router = APIRouter(prefix="/identity_providers", tags=["identity_providers"])


@router.get(
    "/",
    response_model=IdentityProviderReadMulti,
    summary="Read all identity providers",
    description="Retrieve all identity providers stored in the database. \
        It is possible to filter on identity providers attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_providers(
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: IdentityProviderQuery = Depends(),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve all identity providers.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = identity_provider_mng.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    items = identity_provider_mng.paginate(items=items, page=page.page, size=page.size)
    return identity_provider_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{identity_provider_uid}",
    response_model=IdentityProviderReadSingle,
    summary="Read a specific identity provider",
    description="Retrieve a specific identity provider using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_provider(
    size: SchemaSize = Depends(),
    item: IdentityProvider = Depends(valid_identity_provider_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the identity provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return identity_provider_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{identity_provider_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[IdentityProviderRead],
    dependencies=[
        Depends(validate_new_identity_provider_values),
    ],
    summary="Edit a specific identity provider",
    description="Update attribute values of a specific identity provider. \
        The target identity provider is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new identity provider values checking there are \
        no other items with the given *endpoint*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_identity_provider(
    request: Request,
    update_data: IdentityProviderUpdate,
    response: Response,
    item: IdentityProvider = Depends(valid_identity_provider_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the identity provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = identity_provider_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{identity_provider_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific identity provider",
    description="Delete a specific identity provider using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related user groups.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_identity_providers(
    request: Request,
    item: IdentityProvider = Depends(valid_identity_provider_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the identity provider matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not identity_provider_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


# @db.write_transaction
# @router.put(
#     "/{identity_provider_uid}/providers/{provider_uid}",
#     response_model=Optional[IdentityProviderReadExtended],
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
#     item: IdentityProvider = Depends(valid_identity_provider_id),
#     provider: Provider = Depends(valid_provider_id),
# ):
#     if item.providers.is_connected(provider):
#         db_item = item.providers.relationship(provider)
#         if all(
#             [
#                 db_item.__getattribute__(k) == v
#                 for k, v in data.dict(exclude_unset=True).items()
#             ]
#         ):
#             response.status_code = status.HTTP_304_NOT_MODIFIED
#             return None
#         item.providers.disconnect(provider)
#     item.providers.connect(provider, data.dict())
#     return item


# @db.write_transaction
# @router.delete(
#     "/{identity_provider_uid}/providers/{provider_uid}",
#     response_model=Optional[IdentityProviderReadExtended],
#
#     summary="Disconnect provider from identity provider",
#     description="Disconnect a provider from a specific identity \
#         provider knowing their *uid*s. \
#         If no entity matches the given *uid*s, the endpoint \
#         raises a `not found` error.",
# )
# def disconnect_provider_from_identity_providers(
#     response: Response,
#     item: IdentityProvider = Depends(valid_provider_id),
#     provider: Provider = Depends(valid_provider_id),
# ):
#     if not item.providers.is_connected(provider):
#         response.status_code = status.HTTP_304_NOT_MODIFIED
#         return None
#     item.providers.disconnect(provider)
#     return item


# @db.write_transaction
# @router.post(
#     "/{identity_provider_uid}/user_groups",
#     status_code=status.HTTP_201_CREATED,
#     response_model=UserGroupReadExtended,
#     dependencies=[ Depends(is_unique_user_group)],
#     summary="Create a user group",
#     description="Create a user group belonging to identity provider \
#         identified by the given *uid*. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error. \
#         At first validate new user group values checking there are \
#         no other items, belonging to same identity provider, \
#         with the given *name*.",
# )
# def post_user_group(
#     item: UserGroupCreate,
#     db_item: IdentityProvider = Depends(valid_identity_provider_id),
# ):
#     return user_group.create(obj_in=item, identity_provider=db_item, force=True)
