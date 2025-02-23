"""Utilities used in User Group endpoints."""

from fedreg.provider.schemas import ProviderQuery
from fedreg.region.schemas import RegionQuery
from fedreg.user_group.models import UserGroup


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
