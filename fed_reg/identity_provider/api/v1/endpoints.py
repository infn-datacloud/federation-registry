"""IdentityProvider endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.identity_provider.models import IdentityProvider
from fedreg.identity_provider.schemas import (
    IdentityProviderQuery,
    IdentityProviderRead,
    IdentityProviderUpdate,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.identity_provider.api.dependencies import (
    get_identity_provider_item,
    identity_provider_must_exist,
    validate_new_identity_provider_values,
)
from fed_reg.identity_provider.api.utils import (
    IdentityProviderReadMulti,
    IdentityProviderReadSingle,
    choose_schema,
)
from fed_reg.identity_provider.crud import identity_provider_mgr
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate

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
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[IdentityProviderQuery, Depends()],
):
    """GET operation to retrieve all identity providers.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - shape: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    If the user is authenticated the user_infos object is not None and it is used to
    determine the data to return to the user.
    Non-authenticated users can view this function.
    """
    items = identity_provider_mgr.get_multi(
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
    "/{identity_provider_uid}",
    response_model=IdentityProviderReadSingle,
    summary="Read a specific identity provider",
    description="Retrieve a specific identity provider using its *uid*. If no entity \
        matches the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_identity_provider(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[IdentityProvider, Depends(identity_provider_must_exist)],
):
    """GET operation to retrieve the identity provider matching a specific uid.

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
    "/{identity_provider_uid}",
    status_code=status.HTTP_200_OK,
    response_model=IdentityProviderRead | None,
    summary="Patch only specific attribute of the target identity provider",
    description="Update only the received attribute values of a specific identity \
        provider. The target identity provider is identified using its *uid*. If no \
        entity matches the given *uid*, the endpoint raises a `not found` error. \
        At first, the endpoint validates the new identity provider values checking \
        there are no other items with the given *endpoint*. In that case, the \
        endpoint raises the `conflict` error. If there are no differences between new \
        values and current ones, the database entity is left unchanged and the \
        endpoint returns the `not modified` message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_identity_provider(
    response: Response,
    validated_data: Annotated[
        tuple[IdentityProvider, IdentityProviderUpdate],
        Depends(validate_new_identity_provider_values),
    ],
):
    """PATCH operation to update the identity provider matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = identity_provider_mgr.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{identity_provider_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific identity provider",
    description="Delete a specific identity provider using its *uid*. \
        Returns `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_identity_providers(
    item: Annotated[IdentityProvider, Depends(get_identity_provider_item)],
):
    """DELETE operation to remove the identity provider matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        identity_provider_mgr.remove(db_obj=item)


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
