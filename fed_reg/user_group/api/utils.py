"""UserGroup REST API utils."""

from fedreg.provider.schemas import ProviderQuery
from fedreg.region.schemas import RegionQuery
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import UserGroupRead, UserGroupReadPublic
from fedreg.user_group.schemas_extended import (
    UserGroupReadExtended,
    UserGroupReadExtendedPublic,
)
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class UserGroupReadSingle(BaseModel):
    __root__: (
        UserGroupReadExtended
        | UserGroupRead
        | UserGroupReadExtendedPublic
        | UserGroupReadPublic
    ) = Field(..., discriminator="schema_type")


class UserGroupReadMulti(BaseModel):
    __root__: (
        list[UserGroupReadExtended]
        | list[UserGroupRead]
        | list[UserGroupReadExtendedPublic]
        | list[UserGroupReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[UserGroup],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[UserGroupRead]
    | list[UserGroupReadPublic]
    | list[UserGroupReadExtended]
    | list[UserGroupReadExtendedPublic]
    | UserGroupRead
    | UserGroupReadPublic
    | UserGroupReadExtended
    | UserGroupReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=UserGroupRead,
        read_public_schema=UserGroupReadPublic,
        read_private_extended_schema=UserGroupReadExtended,
        read_public_extended_schema=UserGroupReadExtendedPublic,
    )


def filter_on_provider_attr(
    items: list[UserGroup], provider_query: ProviderQuery
) -> list[UserGroup]:
    """Filter projects based on provider access."""
    attrs = provider_query.dict(exclude_none=True)
    if not attrs:
        return items

    for item in items:
        for sla in item.slas:
            for project in sla.projects:
                if not project.provider.get_or_none(**attrs):
                    sla.projects = sla.projects.exclude(uid=project.uid)
            if len(sla.projects) == 0:
                item.slas = item.slas.exclude(uid=sla.uid)
        if len(item.slas) == 0:
            items.remove(item)

    return items


def filter_on_region_attr(
    items: list[UserGroup], region_query: RegionQuery
) -> list[UserGroup]:
    """Filter projects based on region access."""
    attrs = region_query.dict(exclude_none=True)
    if not attrs:
        return items

    for item in items:
        for sla in item.slas:
            for project in sla.projects:
                for quota in project.quotas:
                    service = quota.service.single()
                    if not service.region.get_or_none(**attrs):
                        project.quotas = project.quotas.exclude(uid=quota.uid)
                if len(project.quotas) == 0:
                    sla.projects = sla.projects.exclude(uid=project.uid)
            if len(sla.projects) == 0:
                item.slas = item.slas.exclude(uid=sla.uid)
        if len(item.slas) == 0:
            items.remove(item)

    return items
