"""User Group endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security, status
from fedreg.provider.enum import ProviderStatus, ProviderType
from fedreg.provider.schemas import ProviderQuery
from fedreg.region.schemas import RegionQuery
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import UserGroupQuery, UserGroupRead, UserGroupUpdate
from fedreg.user_group.schemas_extended import UserGroupReadMulti, UserGroupReadSingle
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, get_user_infos, strict_security
from fed_reg.project.api.utils import choose_schema
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaShape, paginate
from fed_reg.user_group.api.dependencies import (
    get_user_group_item,
    user_group_must_exist,
    validate_new_user_group_values,
)
from fed_reg.user_group.api.utils import filter_on_provider_attr, filter_on_region_attr
from fed_reg.user_group.crud import user_group_mgr

router = APIRouter(prefix="/user_groups", tags=["user_groups"])


@router.get(
    "/",
    response_model=UserGroupReadMulti,
    summary="Read all user groups",
    description="Retrieve all user groups stored in the database. \
        It is possible to filter on user groups attributes and other \
        common query parameters.",
)
@custom.decorate_view_func
@db.read_transaction
def get_user_groups(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    comm: Annotated[DbQueryCommonParams, Depends()],
    page: Annotated[Pagination, Depends()],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[UserGroupQuery, Depends()],
    idp_endpoint: str | None = None,
    region_name: str | None = None,
    provider_name: str | None = None,
    provider_type: ProviderType | None = None,
    provider_status: ProviderStatus | None = None,
):
    """GET operation to retrieve all user groups.

    It can receive the following group op parameters:
    - comm: parameters common to all DB queries to limit, skip or sort results.
    - page: parameters to limit and select the number of results to return to the user.
    - size: parameters to define the number of information contained in each result.
    - item: parameters specific for this item typology. Used to apply filters.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    items = user_group_mgr.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    if idp_endpoint:
        items = list(
            filter(
                lambda x: x.identity_provider.single().endpoint == idp_endpoint, items
            )
        )
    if provider_type:
        provider_type = provider_type.value
    if provider_status:
        provider_status = provider_status.value
    provider_query = ProviderQuery(
        name=provider_name, type=provider_type, status=provider_status
    )
    items = filter_on_provider_attr(items=items, provider_query=provider_query)
    region_query = RegionQuery(name=region_name)
    items = filter_on_region_attr(items=items, region_query=region_query)

    items = paginate(items=items, page=page.page, size=page.size)
    return choose_schema(
        items, auth=user_infos is not None, short=shape.short, with_conn=shape.with_conn
    )


@router.get(
    "/{user_group_uid}",
    response_model=UserGroupReadSingle,
    summary="Read a specific user group",
    description="Retrieve a specific user group using its *uid*. If no entity matches \
        the given *uid*, the endpoint raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_user_group(
    user_infos: Annotated[UserInfos | None, Security(get_user_infos)],
    shape: Annotated[SchemaShape, Depends()],
    item: Annotated[UserGroup, Depends(user_group_must_exist)],
):
    """GET operation to retrieve the user group matching a specific uid.

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
    "/{user_group_uid}",
    status_code=status.HTTP_200_OK,
    response_model=UserGroupRead | None,
    summary="Patch only specific attribute of the target user group",
    description="Update only the received attribute values of a specific user group. \
        The target user group is identified using its *uid*. If no entity matches the \
        given *uid*, the endpoint raises a `not found` error.  At first, the endpoint \
        validates the new user group values checking there are no other items with the \
        given *uuid* and *name*. In that case, the endpoint raises the `conflict` \
        error. If there are no differences between new values and current ones, the \
        database entity is left unchanged and the endpoint returns the `not modified` \
        message.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def put_user_group(
    response: Response,
    validated_data: Annotated[
        tuple[UserGroup, UserGroupUpdate], Depends(validate_new_user_group_values)
    ],
):
    """PATCH operation to update the user group matching a specific uid.

    The endpoint expects the item's uid and uses a dependency to check its existence.
    It expects the new data to write in the database.
    It updates only the received attributes. It leaves unchanged the other item's
    attributes and its relationships.

    If new data equals current data, no update is performed and the endpoint returns a
    response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    item, update_data = validated_data
    db_item = user_group_mgr.patch(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{user_group_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific user group",
    description="Delete a specific user group using its *uid*. Returns `no content`.",
    dependencies=[Security(strict_security)],
)
@db.write_transaction
def delete_user_groups(item: Annotated[UserGroup, Depends(get_user_group_item)]):
    """DELETE operation to remove the user group matching a specific uid.

    The endpoint expects the item's uid.

    Only authenticated users can view this endpoint.
    """
    if item is not None:
        user_group_mgr.remove(db_obj=item)


# @db.read_transaction
# @router.get(
#     "/{user_group_uid}/flavors",
#     response_model=list[FlavorReadExtended]|
#         list[FlavorRead]|
#         list[FlavorReadShort]|
#         list[FlavorReadExtendedPublic]|
#         list[FlavorReadPublic],
#     summary="Read user group accessible flavors",
#     description="Retrieve all the flavors the user group \
#         has access to thanks to its SLA. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error.",
# )
# def get_user_group_flavors(
#     auth: bool = Depends(check_read_access),
#     size: SchemaShape = Depends(),
#     item: UserGroup = Depends(valid_user_group_id),
# ):
#     return flavor.choose_out_schema(
#         items=item.flavors(), auth=user_infos, short=size.short,
# with_conn=size.with_conn
#     )


# @db.read_transaction
# @router.get(
#     "/{user_group_uid}/images",
#     response_model=
#         list[ImageReadExtended]|
#         list[ImageRead]|
#         list[ImageReadShort]|
#         list[ImageReadExtendedPublic]|
#         list[ImageReadPublic],
#     summary="Read user group accessible images",
#     description="Retrieve all the images the user group \
#         has access to thanks to its SLA. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error.",
# )
# def get_user_group_images(
#     auth: bool = Depends(check_read_access),
#     size: SchemaShape = Depends(),
#     item: UserGroup = Depends(valid_user_group_id),
# ):
#     return image.choose_out_schema(
#         items=item.images(), auth=user_infos, short=size.short,
# with_conn=size.with_conn
#     )


# @db.read_transaction
# @router.get(
#     "/{user_group_uid}/providers",
#     response_model=
#         list[ProviderReadExtended]|
#         list[ProviderRead]|
#         list[ProviderReadShort]|
#         list[ProviderReadExtendedPublic]|
#         list[ProviderReadPublic],
#     summary="Read user group accessible providers",
#     description="Retrieve all the providers the user group \
#         has access to thanks to its SLA. \
#         If no entity matches the given *uid*, the endpoint \
#         raises a `not found` error.",
# )
# def get_user_group_providers(
#     auth: bool = Depends(check_read_access),
#     size: SchemaShape = Depends(),
#     item: UserGroup = Depends(valid_user_group_id),
# ):
#     return provider.choose_out_schema(
#         items=item.providers(), auth=user_infos, short=size.short,
# with_conn=size.with_conn
#     )


# @db.read_transaction
# @router.get(
#    "/{user_group_uid}/services",
#    response_model=
#        list[
#                BlockStorageServiceReadExtended|
#                IdentityServiceReadExtended|
#                ComputeServiceReadExtended
#        ]|
#        list[BlockStorageServiceRead| IdentityServiceRead| ComputeServiceRead]|
#        list[
#                BlockStorageServiceReadShort|
#                IdentityServiceReadShort|
#                ComputeServiceReadShort
#        ]|
#        list[
#                BlockStorageServiceReadExtendedPublic|
#                IdentityServiceReadExtendedPublic|
#                ComputeServiceReadExtendedPublic,
#        ]|
#        list[
#                BlockStorageServiceReadPublic|
#                IdentityServiceReadPublic|
#                ComputeServiceReadPublic,
#        ],
#    summary="Read user group accessible services",
#    description="Retrieve all the services the user group \
#        has access to thanks to its SLA. \
#        If no entity matches the given *uid*, the endpoint \
#        raises a `not found` error.",
# )
# def get_user_group_services(
#    auth: bool = Depends(check_read_access),
#    size: SchemaShape = Depends(),
#    item: UserGroup = Depends(valid_user_group_id),
#    srv: ServiceQuery = Depends(),
# ):
#    items = item.services(**srv.dict(exclude_none=True))
#    return service.choose_out_schema(
#        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
#    )
