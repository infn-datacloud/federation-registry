from typing import Any

from tests.schemas.utils import (
    auth_method_schema_dict,
    flavor_schema_dict,
    identity_provider_schema_dict,
    image_schema_dict,
    location_schema_dict,
    network_schema_dict,
    project_schema_dict,
    provider_schema_dict,
    quota_schema_dict,
    region_schema_dict,
    service_schema_dict,
    sla_schema_dict,
    user_group_schema_dict,
)


def auth_method_model_dict(*args, **kwargs) -> dict[str, str]:
    return auth_method_schema_dict(*args, **kwargs)


def flavor_model_dict(*args, **kwargs) -> dict[str, str]:
    d = flavor_schema_dict(*args, **kwargs)
    d["uuid"] = d["uuid"].hex
    return d


def identity_provider_model_dict(*args, **kwargs) -> dict[str, str]:
    return identity_provider_schema_dict(*args, **kwargs)


def image_model_dict(*args, **kwargs) -> dict[str, str]:
    d = image_schema_dict(*args, **kwargs)
    d["uuid"] = d["uuid"].hex
    if d.get("os_type", None) is not None:
        d["os_type"] = d.get("os_type", None).value
    return d


def location_model_dict(*args, **kwargs) -> dict[str, str]:
    return location_schema_dict(*args, **kwargs)


def network_model_dict(*args, **kwargs) -> dict[str, str]:
    d = network_schema_dict(*args, **kwargs)
    d["uuid"] = d["uuid"].hex
    return d


def project_model_dict(*args, **kwargs) -> dict[str, str]:
    d = project_schema_dict(*args, **kwargs)
    d["uuid"] = d["uuid"].hex
    return d


def provider_model_dict(*args, **kwargs) -> dict[str, str]:
    d = provider_schema_dict(*args, **kwargs)
    d["type"] = d["type"].value
    return d


def quota_model_dict(*args, **kwargs) -> dict[str, str]:
    return quota_schema_dict(*args, **kwargs)


def region_model_dict(*args, **kwargs) -> dict[str, str]:
    return region_schema_dict(*args, **kwargs)


def service_model_dict(*args, **kwargs) -> dict[str, str]:
    return service_schema_dict(*args, **kwargs)


def sla_model_dict(*args, **kwargs) -> dict[str, Any]:
    d = sla_schema_dict(*args, **kwargs)
    d["doc_uuid"] = d["doc_uuid"].hex
    return d


def user_group_model_dict(*args, **kwargs) -> dict[str, str]:
    return user_group_schema_dict(*args, **kwargs)
