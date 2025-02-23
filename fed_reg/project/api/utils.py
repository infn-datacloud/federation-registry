"""Utilities used in Project endpoints."""

from fedreg.project.models import Project
from fedreg.region.schemas import RegionQuery
from fedreg.service.schemas import IdentityServiceQuery


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
