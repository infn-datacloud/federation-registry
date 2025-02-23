"""User Group endpoints to execute POST, GET, PUT, PATCH and DELETE operations."""
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
from fedreg.provider.enum import ProviderStatus, ProviderType
from fedreg.provider.schemas import ProviderQuery
from fedreg.region.schemas import RegionQuery
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import (
    UserGroupQuery,
    UserGroupRead,
    UserGroupUpdate,
)
from fedreg.user_group.schemas_extended import (
    UserGroupReadMulti,
    UserGroupReadSingle,
)
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.auth import custom, flaat, get_user_infos, security

# from app.flavor.crud import flavor
# from app.flavor.schemas import FlavorRead, FlavorReadPublic, FlavorReadShort
# from app.flavor.schemas_extended import FlavorReadExtended, FlavorReadExtendedPublic
# from app.identity_provider.schemas_extended import (
#     ProviderReadExtended,
#     ProviderReadExtendedPublic,
# )
# from app.image.crud import image
# from app.image.schemas import ImageRead, ImageReadPublic, ImageReadShort
# from app.image.schemas_extended import ImageReadExtended, ImageReadExtendedPublic
# from app.provider.crud import provider
# from app.provider.schemas import ProviderRead, ProviderReadPublic, ProviderReadShort
from fed_reg.query import DbQueryCommonParams, Pagination, SchemaSize

# from app.service.schemas import (
#     BlockStorageServiceRead,
#     BlockStorageServiceReadPublic,
#     BlockStorageServiceReadShort,
#     ComputeServiceRead,
#     ComputeServiceReadPublic,
#     ComputeServiceReadShort,
#     IdentityServiceRead,
#     IdentityServiceReadPublic,
#     IdentityServiceReadShort,
# )
# from app.service.schemas_extended import (
#     BlockStorageServiceReadExtended,
#     BlockStorageServiceReadExtendedPublic,
#     ComputeServiceReadExtended,
#     ComputeServiceReadExtendedPublic,
#     IdentityServiceReadExtended,
#     IdentityServiceReadExtendedPublic,
# )
from fed_reg.user_group.api.dependencies import (
    valid_user_group_id,
    validate_new_user_group_values,
)
from fed_reg.user_group.api.utils import filter_on_provider_attr, filter_on_region_attr
from fed_reg.user_group.crud import user_group_mng

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
    comm: DbQueryCommonParams = Depends(),
    page: Pagination = Depends(),
    size: SchemaSize = Depends(),
    item: UserGroupQuery = Depends(),
    idp_endpoint: Optional[str] = None,
    provider_name: Optional[str] = None,
    provider_type: Optional[ProviderType] = None,
    provider_status: Optional[ProviderStatus] = None,
    region_name: Optional[str] = None,
    user_infos: UserInfos | None = Security(get_user_infos),
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
    items = user_group_mng.get_multi(
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

    items = user_group_mng.paginate(items=items, page=page.page, size=page.size)
    return user_group_mng.choose_out_schema(
        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
    )


@router.get(
    "/{user_group_uid}",
    response_model=UserGroupReadSingle,
    summary="Read a specific user group",
    description="Retrieve a specific user group using its *uid*. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error.",
)
@custom.decorate_view_func
@db.read_transaction
def get_user_group(
    size: SchemaSize = Depends(),
    item: UserGroup = Depends(valid_user_group_id),
    user_infos: UserInfos | None = Security(get_user_infos),
):
    """GET operation to retrieve the user group matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    It can receive the following group op parameters:
    - size: parameters to define the number of information contained in each result.

    Non-authenticated users can view this function. If the user is authenticated the
    user_infos object is not None and it is used to determine the data to return to the
    user.
    """
    return user_group_mng.choose_out_schema(
        items=[item], auth=user_infos, short=size.short, with_conn=size.with_conn
    )[0]


@router.patch(
    "/{user_group_uid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[UserGroupRead],
    dependencies=[Depends(validate_new_user_group_values)],
    summary="Edit a specific user group",
    description="Update attribute values of a specific user group. \
        The target user group is identified using its uid. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. If new values equal \
        current ones, the database entity is left unchanged \
        and the endpoint returns the `not modified` message. \
        At first validate new user group values checking there are \
        no other items, belonging to same identity provider, \
        with the given *name*.",
)
@flaat.access_level("write")
@db.write_transaction
def put_user_group(
    request: Request,
    update_data: UserGroupUpdate,
    response: Response,
    item: UserGroup = Depends(valid_user_group_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """PATCH operation to update the user group matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence. It also
    expects the new data to write in the database. It updates only the item attributes,
    not its relationships.

    If the new data equals the current data, no update is performed and the function
    returns a response with an empty body and the 304 status code.

    Only authenticated users can view this function.
    """
    db_item = user_group_mng.update(db_obj=item, obj_in=update_data)
    if not db_item:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@router.delete(
    "/{user_group_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific user group",
    description="Delete a specific user group using its *uid*. \
        Returns `no content`. \
        If no entity matches the given *uid*, the endpoint \
        raises a `not found` error. \
        On cascade, delete related SLAs.",
)
@flaat.access_level("write")
@db.write_transaction
def delete_user_group(
    request: Request,
    item: UserGroup = Depends(valid_user_group_id),
    client_credentials: HTTPBasicCredentials = Security(security),
):
    """DELETE operation to remove the user group matching a specific uid.

    The endpoints expect a uid and uses a dependency to check its existence.

    Only authenticated users can view this function.
    """
    if not user_group_mng.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


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
#     size: SchemaSize = Depends(),
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
#     size: SchemaSize = Depends(),
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
#     size: SchemaSize = Depends(),
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
#    size: SchemaSize = Depends(),
#    item: UserGroup = Depends(valid_user_group_id),
#    srv: ServiceQuery = Depends(),
# ):
#    items = item.services(**srv.dict(exclude_none=True))
#    return service.choose_out_schema(
#        items=items, auth=user_infos, short=size.short, with_conn=size.with_conn
#    )
