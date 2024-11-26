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


def auth_method_model_dict() -> dict[str, Any]:
    return auth_method_schema_dict()


def flavor_model_dict() -> dict[str, Any]:
    """Return a dict with the flavor neomodel mandatory attributes."""
    d = flavor_schema_dict()
    d["uuid"] = d["uuid"].hex
    return d


def identity_provider_model_dict() -> dict[str, Any]:
    d = identity_provider_schema_dict()
    d["endpoint"] = str(d["endpoint"])
    return d


def image_model_dict() -> dict[str, Any]:
    d = image_schema_dict()
    d["uuid"] = d["uuid"].hex
    return d


def location_model_dict() -> dict[str, Any]:
    return location_schema_dict()


def network_model_dict() -> dict[str, Any]:
    d = network_schema_dict()
    d["uuid"] = d["uuid"].hex
    return d


def project_model_dict() -> dict[str, Any]:
    d = project_schema_dict()
    d["uuid"] = d["uuid"].hex
    return d


def provider_model_dict() -> dict[str, Any]:
    d = provider_schema_dict()
    d["type"] = d["type"].value
    return d


def quota_model_dict() -> dict[str, Any]:
    return quota_schema_dict()


def region_model_dict() -> dict[str, Any]:
    return region_schema_dict()


def service_model_dict() -> dict[str, Any]:
    d = service_schema_dict()
    d["endpoint"] = str(d["endpoint"])
    return d


def sla_model_dict() -> dict[str, Any]:
    d = sla_schema_dict()
    d["doc_uuid"] = d["doc_uuid"].hex
    return d


def user_group_model_dict() -> dict[str, Any]:
    return user_group_schema_dict()
