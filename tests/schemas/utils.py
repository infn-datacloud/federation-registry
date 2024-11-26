from typing import Any
from uuid import uuid4

from fed_reg.service.enum import (
    BlockStorageServiceName,
    ComputeServiceName,
    IdentityServiceName,
    NetworkServiceName,
    ObjectStoreServiceName,
)
from tests.utils import (
    random_country,
    random_date_after,
    random_date_before,
    random_email,
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


def auth_method_schema_dict() -> dict[str, Any]:
    return {"idp_name": random_lower_string(), "protocol": random_lower_string()}


def flavor_schema_dict(read: bool = False) -> dict[str, Any]:
    """Return a dict with the flavor pydantic mandatory attributes.

    If 'read' is true add the 'uid' attribute.
    """
    data = {"name": random_lower_string(), "uuid": uuid4()}
    if read:
        data["uid"] = uuid4()
    return data


def identity_provider_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"endpoint": random_url(), "group_claim": random_lower_string()}
    if read:
        data["uid"] = uuid4()
    return data


def image_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"name": random_lower_string(), "uuid": uuid4()}
    if read:
        data["uid"] = uuid4()
    return data


def location_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"site": random_lower_string(), "country": random_country()}
    if read:
        data["uid"] = uuid4()
    return data


def network_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"name": random_lower_string(), "uuid": uuid4()}
    if read:
        data["uid"] = uuid4()
    return data


def project_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"name": random_lower_string(), "uuid": uuid4()}
    if read:
        data["uid"] = uuid4()
    return data


def provider_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"name": random_lower_string(), "type": random_provider_type()}
    if read:
        data["uid"] = uuid4()
    return data


def quota_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {}
    if read:
        data["uid"] = uuid4()
    return data


def region_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"name": random_lower_string()}
    if read:
        data["uid"] = uuid4()
    return data


def service_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"endpoint": random_lower_string(), "name": random_lower_string()}
    if read:
        data["uid"] = uuid4()
    return data


def sla_schema_dict(read: bool = False) -> dict[str, Any]:
    start_date, end_date = random_start_end_dates()
    data = {"doc_uuid": uuid4(), "start_date": start_date, "end_date": end_date}
    if read:
        data["uid"] = uuid4()
    return data


def user_group_schema_dict(read: bool = False) -> dict[str, Any]:
    data = {"name": random_lower_string()}
    if read:
        data["uid"] = uuid4()
    return data


def flavor_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    """Return a valid dict for flavor."""
    for k in args:
        if k in (
            "description",
            "name",
            "gpu_model",
            "gpu_vendor",
            "local_storage",
        ):
            data[k] = random_lower_string()
            if k.startswith("gpu_"):
                data["gpus"] = 1
        elif k in ("uuid",):
            data[k] = uuid4()
        elif k in ("disk", "ram", "vcpus", "swap", "ephemeral", "gpus"):
            data[k] = random_positive_int()
        elif k in ("infiniband",):
            data[k] = True
        elif k in ("is_shared",):
            data["is_shared"] = True
        elif k in ("is_private",):
            data["is_shared"] = False
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def flavor_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "uuid", "uid"):
            data.pop(k)
        elif k in ("disk", "ram", "vcpus", "swap", "ephemeral", "gpus"):
            data[k] = -1
        elif k in ("gpu_model", "gpu_vendor"):
            data[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def identity_provider_valid_dict(
    data: dict[str, Any], *args, **kwargs
) -> dict[str, Any]:
    for k in args:
        if k in ("description", "group_claim"):
            data[k] = random_lower_string()
        elif k in ("endpoint",):
            data[k] = random_url()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def identity_provider_invalid_dict(
    data: dict[str, Any], *args, **kwargs
) -> dict[str, Any]:
    for k in args:
        if k in ("endpoint", "group_claim", "uid"):
            data.pop(k)
        elif k in ("not_an_endpoint",):
            data["country"] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def image_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in (
            "description",
            "name",
            "os_distro",
            "os_version",
            "architecture",
            "kernel_id",
        ):
            data[k] = random_lower_string()
        elif k in ("uuid",):
            data[k] = uuid4()
        elif k in ("cuda_support", "gpu_driver"):
            data[k] = True
        elif k in ("os_type",):
            data[k] = random_image_os_type()
        elif k in ("tags",):
            data[k] = [random_lower_string()]
        elif k in ("is_shared",):
            data["is_shared"] = True
        elif k in ("is_private",):
            data["is_shared"] = False
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def image_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "uuid", "uid"):
            data.pop(k)
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def location_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "site"):
            data[k] = random_lower_string()
        elif k in ("country",):
            data[k] = random_country()
        elif k in ("latitude", "longitude"):
            data[k] = random_float(0, 90)
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def location_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("country", "site", "uid"):
            data.pop(k)
        elif k in ("not_a_country",):
            data["country"] = random_lower_string()
        elif k in ("under_min_latitude",):
            data["latitude"] = -91
        elif k in ("over_max_latitude",):
            data["latitude"] = 91
        elif k in ("under_min_longitude",):
            data["longitude"] = -181
        elif k in ("over_max_longitude",):
            data["longitude"] = 181
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def network_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "name", "proxy_host", "proxy_user"):
            data[k] = random_lower_string()
        elif k in ("uuid",):
            data[k] = uuid4()
        elif k in ("mtu",):
            data[k] = random_positive_int()
        elif k in ("is_router_external", "is_default"):
            data[k] = True
        elif k in ("tags",):
            data[k] = [random_lower_string()]
        elif k in ("is_shared",):
            data["is_shared"] = True
        elif k in ("is_private",):
            data["is_shared"] = False
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def network_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "uuid", "uid"):
            data.pop(k)
        elif k in ("mtu",):
            data["mtu"] = -1
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def project_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "name"):
            data[k] = random_lower_string()
        elif k in ("uuid",):
            data[k] = uuid4()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def project_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "uuid", "uid"):
            data.pop(k)
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def provider_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "name"):
            data[k] = random_lower_string()
        elif k in ("type",):
            data[k] = random_provider_type()
        elif k in ("status",):
            data[k] = random_provider_status()
        elif k in ("is_public",):
            data[k] = True
        elif k in ("support_emails",):
            data[k] = [random_email()]
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def provider_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "type", "uid"):
            data.pop(k)
        elif k in ("not_a_type",):
            data["type"] = random_lower_string()
        elif k in ("not_a_status",):
            data["status"] = random_lower_string()
        elif k in ("not_an_email",):
            data["support_emails"] = [random_lower_string()]
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def quota_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description",):
            data[k] = random_lower_string()
        elif k in ("per_user", "usage"):
            data[k] = True
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
            data[k] = random_non_negative_int()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def quota_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    return data


def region_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "name"):
            data[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def region_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "uid"):
            data.pop(k)
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def service_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "name"):
            data[k] = random_lower_string()
        elif k in ("endpoint",):
            data[k] = random_url()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def service_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    return data


def block_storage_service_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = service_schema_dict(*args, **kwargs)
    d["name"] = random_service_name(BlockStorageServiceName)
    return d


def compute_service_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = service_schema_dict(*args, **kwargs)
    d["name"] = random_service_name(ComputeServiceName)
    return d


def identity_service_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = service_schema_dict(*args, **kwargs)
    d["name"] = random_service_name(IdentityServiceName)
    return d


def network_service_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = service_schema_dict(*args, **kwargs)
    d["name"] = random_service_name(NetworkServiceName)
    return d


def object_store_service_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = service_schema_dict(*args, **kwargs)
    d["name"] = random_service_name(ObjectStoreServiceName)
    return d


def sla_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description",):
            data[k] = random_lower_string()
        elif k in ("doc_uuid",):
            data[k] = uuid4()
        elif k in ("start_date",):
            data[k] = random_date_before(data["end_date"])
        elif k in ("end_date",):
            data[k] = random_date_after(data["start_date"])
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def sla_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("doc_uuid", "start_date", "end_date", "uid"):
            data.pop(k)
        elif k in ("inverted_dates",):
            data["end_date"], data["start_date"] = random_start_end_dates()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def user_group_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("description", "name"):
            data[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def user_group_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("name", "uid"):
            data.pop(k)
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data
