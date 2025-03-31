"""Project REST API utils."""

from fedreg.project.models import Project
from fedreg.project.schemas import ProjectRead, ProjectReadPublic
from fedreg.project.schemas_extended import (
    ProjectReadExtended,
    ProjectReadExtendedPublic,
)
from fedreg.region.schemas import RegionQuery
from fedreg.service.schemas import IdentityServiceQuery
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class ProjectReadSingle(BaseModel):
    __root__: (
        ProjectReadExtended
        | ProjectRead
        | ProjectReadExtendedPublic
        | ProjectReadPublic
    ) = Field(..., discriminator="schema_type")


class ProjectReadMulti(BaseModel):
    __root__: (
        list[ProjectReadExtended]
        | list[ProjectRead]
        | list[ProjectReadExtendedPublic]
        | list[ProjectReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[Project],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[ProjectRead]
    | list[ProjectReadPublic]
    | list[ProjectReadExtended]
    | list[ProjectReadExtendedPublic]
    | ProjectRead
    | ProjectReadPublic
    | ProjectReadExtended
    | ProjectReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ProjectRead,
        read_public_schema=ProjectReadPublic,
        read_private_extended_schema=ProjectReadExtended,
        read_public_extended_schema=ProjectReadExtendedPublic,
    )


def filter_on_region_attr(  # noqa: C901
    items: list[Project], region_query: RegionQuery
) -> list[Project]:
    """Filter projects based on region access."""
    attrs = region_query.dict(exclude_none=True)
    if not attrs:
        return items

    new_items = []
    for item in items:
        for quota in item.quotas:
            service = quota.service.single()
            if not service.region.get_or_none(**attrs):
                item.quotas = item.quotas.exclude(uid=quota.uid)
        if len(item.quotas) > 0:
            for flavor in item.private_flavors:
                service = flavor.services.single()
                if not service.region.get_or_none(**attrs):
                    item.private_flavors = item.private_flavors.exclude(uid=flavor.uid)
            for image in item.private_images:
                service = image.services.single()
                if not service.region.get_or_none(**attrs):
                    item.private_images = item.private_images.exclude(uid=image.uid)
            for network in item.private_networks:
                service = network.service.single()
                if not service.region.get_or_none(**attrs):
                    item.private_networks = item.private_networks.exclude(
                        uid=network.uid
                    )
            new_items.append(item)
    return new_items


def filter_on_service_attr(
    items: list[Project], service_query: IdentityServiceQuery
) -> list[Project]:
    """Filter projects based on region access."""
    attrs = service_query.dict(exclude_none=True)
    if not attrs:
        return items

    new_items = []
    for item in items:
        for region in item.provider.single().regions:
            if region.services.get_or_none(**attrs):
                new_items.append(item)
                break
    return new_items
