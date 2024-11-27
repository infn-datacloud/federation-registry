from enum import Enum
from random import choice, randint, random
from typing import Any
from uuid import uuid4

from pycountry import countries

from fed_reg.image.enum import ImageOS
from fed_reg.models import BaseNodeRead
from fed_reg.provider.enum import ProviderStatus, ProviderType
from fed_reg.service.enum import (
    BlockStorageServiceName,
    ComputeServiceName,
    IdentityServiceName,
    NetworkServiceName,
    ObjectStoreServiceName,
)
from tests.utils import (
    random_date_after,
    random_date_before,
    random_email,
    random_float,
    random_lower_string,
    random_non_negative_int,
    random_start_end_dates,
    random_url,
)


def auth_method_schema_dict() -> dict[str, Any]:
    return {"idp_name": random_lower_string(), "protocol": random_lower_string()}


def flavor_schema_dict() -> dict[str, Any]:
    """Return a dict with the flavor pydantic mandatory attributes.

    If 'read' is true add the 'uid' attribute.
    """
    return {"name": random_lower_string(), "uuid": uuid4()}


def identity_provider_schema_dict() -> dict[str, Any]:
    return {"endpoint": random_url(), "group_claim": random_lower_string()}


def image_schema_dict() -> dict[str, Any]:
    return {"name": random_lower_string(), "uuid": uuid4()}


def location_schema_dict() -> dict[str, Any]:
    return {"site": random_lower_string(), "country": random_country()}


def network_schema_dict() -> dict[str, Any]:
    return {"name": random_lower_string(), "uuid": uuid4()}


def project_schema_dict() -> dict[str, Any]:
    return {"name": random_lower_string(), "uuid": uuid4()}


def provider_schema_dict() -> dict[str, Any]:
    return {"name": random_lower_string(), "type": random_provider_type()}


def quota_schema_dict() -> dict[str, Any]:
    return {}


def region_schema_dict() -> dict[str, Any]:
    return {"name": random_lower_string()}


def service_schema_dict() -> dict[str, Any]:
    return {"endpoint": random_lower_string(), "name": random_lower_string()}


def sla_schema_dict() -> dict[str, Any]:
    start_date, end_date = random_start_end_dates()
    return {"doc_uuid": uuid4(), "start_date": start_date, "end_date": end_date}


def user_group_schema_dict() -> dict[str, Any]:
    return {"name": random_lower_string()}


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


def random_country() -> str:
    """Return random country."""
    return choice([i.name for i in countries])


def random_latitude() -> float:
    """Return a valid latitude value."""
    return randint(-90, 89) + random()


def random_longitude() -> float:
    """Return a valid longitude value."""
    return randint(-180, 179) + random()


def random_provider_type() -> ProviderType:
    return choice([i for i in ProviderType])


def random_provider_status() -> ProviderStatus:
    return choice([i for i in ProviderStatus])


def random_service_name(enum_cls: Enum) -> Any:
    return choice([i for i in enum_cls])


def random_image_os_type() -> ImageOS:
    return choice([i for i in ImageOS])


def detect_public_extended_details(read_class: type[BaseNodeRead]) -> tuple[bool, bool]:
    """From class name detect if it public or not, extended or not."""
    cls_name = read_class.__name__
    is_public = False
    is_extended = False
    if "Public" in cls_name:
        is_public = True
    if "Extended" in cls_name:
        is_extended = True
    return is_public, is_extended
