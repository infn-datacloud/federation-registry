from typing import Any
from uuid import uuid4

from fed_reg.service.enum import (
    BlockStorageServiceName,
    ComputeServiceName,
    IdentityServiceName,
    NetworkServiceName,
    ObjectStoreServiceName,
    ServiceType,
)
from tests.utils import (
    random_country,
    random_date,
    random_float,
    random_image_os_type,
    random_lower_string,
    random_non_negative_int,
    random_positive_int,
    random_provider_status,
    random_provider_type,
    random_service_name,
    random_start_end_dates,
    random_url,
)


def auth_method_dict() -> dict[str, str]:
    return {"idp_name": random_lower_string(), "protocol": random_lower_string()}


def flavor_model_dict(*args) -> dict[str, str]:
    d = flavor_schema_dict(*args)
    d["uuid"] = d["uuid"].hex
    return d


def flavor_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    for k in args:
        if k in (
            "description",
            "name",
            "gpu_model",
            "gpu_vendor",
            "local_storage",
        ):
            d[k] = random_lower_string()
        elif k in ("uuid",):
            d[k] = uuid4()
        elif k in ("disk", "ram", "vcpus", "swap", "ephemeral", "gpus"):
            d[k] = random_positive_int()
        elif k in ("infiniband",):
            d[k] = True
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def identity_provider_model_dict(*args) -> dict[str, str]:
    return identity_provider_schema_dict(*args)


def identity_provider_schema_dict(*args) -> dict[str, str]:
    d = {"endpoint": random_url(), "group_claim": random_lower_string()}
    for k in args:
        if k in ("description", "group_claim"):
            d[k] = random_lower_string()
        elif k in ("endpoint",):
            d[k] = random_url()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def image_model_dict(*args) -> dict[str, str]:
    d = image_schema_dict(*args)
    d["uuid"] = d["uuid"].hex
    if d.get("os_type", None) is not None:
        d["os_type"] = d.get("os_type", None).value
    return d


def image_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    for k in args:
        if k in (
            "description",
            "name",
            "os_distro",
            "os_version",
            "architecture",
            "kernel_id",
        ):
            d[k] = random_lower_string()
        elif k in ("uuid",):
            d[k] = uuid4()
        elif k in ("cuda_support", "gpu_driver"):
            d[k] = True
        elif k in ("os_type",):
            d[k] = random_image_os_type()
        elif k in ("tags",):
            d[k] = [random_image_os_type()]
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def location_model_dict(*args) -> dict[str, str]:
    return location_schema_dict(*args)


def location_schema_dict(*args) -> dict[str, str]:
    d = {"site": random_lower_string(), "country": random_country()}
    for k in args:
        if k in ("description", "site"):
            d[k] = random_lower_string()
        elif k in ("country",):
            d[k] = random_country()
        elif k in ("latitude", "longitude"):
            d[k] = random_float(0, 90)
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def network_model_dict(*args) -> dict[str, str]:
    d = network_schema_dict(*args)
    d["uuid"] = d["uuid"].hex
    return d


def network_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    for k in args:
        if k in ("description", "name", "proxy_host", "proxy_user"):
            d[k] = random_lower_string()
        elif k in ("uuid",):
            d[k] = uuid4()
        elif k in ("mtu",):
            d[k] = random_positive_int()
        elif k in ("is_router_external", "is_default"):
            d[k] = True
        elif k in ("tags",):
            d[k] = [random_image_os_type()]
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def project_model_dict(*args) -> dict[str, str]:
    d = project_schema_dict(*args)
    d["uuid"] = d["uuid"].hex
    return d


def project_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    for k in args:
        if k in ("description", "name"):
            d[k] = random_lower_string()
        elif k in ("uuid",):
            d[k] = uuid4()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def provider_model_dict(*args) -> dict[str, str]:
    d = provider_schema_dict(*args)
    d["type"] = d["type"].value
    return d


def provider_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string(), "type": random_provider_type()}
    for k in args:
        if k in ("description", "name"):
            d[k] = random_lower_string()
        elif k in ("type",):
            d[k] = random_provider_type()
        elif k in ("status",):
            d[k] = random_provider_status()
        elif k in ("is_public",):
            d[k] = True
        elif k in ("support_emails",):
            d[k] = [random_image_os_type()]
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def quota_model_dict(*args) -> dict[str, str]:
    return quota_schema_dict(*args)


def quota_schema_dict(*args) -> dict[str, str]:
    d = {}
    for k in args:
        if k in ("description",):
            d[k] = random_lower_string()
        elif k in ("per_user", "usage"):
            d[k] = True
        elif k in (
            "gigabytes",
            "volumes",
            "per_volume_gigabytes",
            "cores",
            "instances",
            "ram",
            "public_ips",
            "networks",
            "ports",
            "security_groups",
            "security_group_rules",
            "bytes",
            "containers",
            "objects",
        ):
            d[k] = random_non_negative_int()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def region_model_dict(*args) -> dict[str, str]:
    return region_schema_dict(*args)


def region_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string()}
    for k in args:
        if k in ("description", "name"):
            d[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def service_model_dict(*args) -> dict[str, str]:
    return service_schema_dict(*args)


def service_schema_dict(*args) -> dict[str, str]:
    d = {"endpoint": random_lower_string(), "name": random_lower_string()}
    for k in args:
        if k in ("description", "name"):
            d[k] = random_lower_string()
        elif k in ("endpoint",):
            d[k] = random_url()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def block_storage_service_schema_dict(*args) -> dict[str, str]:
    d = service_schema_dict(*args)
    d["name"] = random_service_name(BlockStorageServiceName)
    return d


def compute_service_schema_dict(*args) -> dict[str, str]:
    d = service_schema_dict(*args)
    d["name"] = random_service_name(ComputeServiceName)
    return d


def identity_service_schema_dict(*args) -> dict[str, str]:
    d = service_schema_dict(*args)
    d["name"] = random_service_name(IdentityServiceName)
    return d


def network_service_model_dict(*args) -> dict[str, str]:
    d = network_service_schema_dict(*args)
    d["name"] = d["name"].value
    d["type"] = ServiceType.NETWORK.value
    return d


def network_service_schema_dict(*args) -> dict[str, str]:
    d = service_schema_dict(*args)
    d["name"] = random_service_name(NetworkServiceName)
    return d


def object_store_service_model_dict(*args) -> dict[str, str]:
    d = object_store_service_schema_dict(*args)
    d["name"] = d["name"].value
    d["type"] = ServiceType.OBJECT_STORE.value
    return d


def object_store_service_schema_dict(*args) -> dict[str, str]:
    d = service_schema_dict(*args)
    d["name"] = random_service_name(ObjectStoreServiceName)
    return d


def sla_model_dict(*args) -> dict[str, Any]:
    d = sla_schema_dict(*args)
    d["doc_uuid"] = d["doc_uuid"].hex
    return d


def sla_schema_dict(*args) -> dict[str, Any]:
    start_date, end_date = random_start_end_dates()
    d = {"doc_uuid": uuid4(), "start_date": start_date, "end_date": end_date}
    for k in args:
        if k in ("description",):
            d[k] = random_lower_string()
        elif k in ("doc_uuid",):
            d[k] = uuid4()
        elif k in ("start_date", "end_date"):
            d[k] = random_date()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d


def user_group_model_dict(*args) -> dict[str, str]:
    return user_group_schema_dict(*args)


def user_group_schema_dict(*args) -> dict[str, str]:
    d = {"name": random_lower_string()}
    for k in args:
        if k in ("description", "name"):
            d[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return d
