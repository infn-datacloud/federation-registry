from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from neomodel import DateProperty, DateTimeProperty, StringProperty, StructuredNode
from pydantic import Field

from fed_reg.models import BaseNode, BaseNodeRead
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


class TestEnum(Enum):
    __test__ = False
    VALUE_1 = "value_1"
    VALUE_2 = "value_2"


class TestModelBool(BaseNode):
    __test__ = False
    test_field: bool = Field(..., description="A test field for booleans")


class TestModelInt(BaseNode):
    __test__ = False
    test_field: int = Field(..., description="A test field for integers")


class TestModelFloat(BaseNode):
    __test__ = False
    test_field: float = Field(..., description="A test field for floats")


class TestModelDate(BaseNode):
    __test__ = False
    test_field: date = Field(..., description="A test field for dates")


class TestModelDateTime(BaseNode):
    __test__ = False
    test_field: datetime = Field(..., description="A test field for datetimes")


class TestModelStr(BaseNode):
    __test__ = False
    test_field: str = Field(..., description="A test field for strings")


class TestModelEnum(BaseNode):
    __test__ = False
    test_field: TestEnum = Field(..., description="A test field for enums")


class TestModelUUID(BaseNode):
    __test__ = False
    uuid: str = Field(default="", description="A test field for uuid")
    uuid_list: list[str] = Field(
        default_factory=list, description="A test field for list of uuids"
    )


class TestModelReadDate(BaseNodeRead):
    __test__ = False
    date_test: date = Field(..., description="A test field for dates")


class TestModelReadDateTime(BaseNodeRead):
    __test__ = False
    datetime_test: datetime = Field(..., description="A test field for dates")


class TestORMDate(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    date_test = DateProperty()


class TestORMDateTime(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    date_test = DateTimeProperty()


def auth_method_schema_dict() -> dict[str, Any]:
    return {"idp_name": random_lower_string(), "protocol": random_lower_string()}


def flavor_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
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
            data["is_public"] = True
        elif k in ("is_private",):
            data["is_public"] = False
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


def flavor_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return flavor_valid_dict(d, *args)
    return flavor_invalid_dict(d, *args)


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


def identity_provider_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"endpoint": random_url(), "group_claim": random_lower_string()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return identity_provider_valid_dict(d, *args)
    return identity_provider_invalid_dict(d, *args)


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
            data["is_public"] = True
        elif k in ("is_private",):
            data["is_public"] = False
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


def image_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return image_valid_dict(d, *args)
    return image_invalid_dict(d, *args)


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


def location_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"site": random_lower_string(), "country": random_country()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return location_valid_dict(d, *args)
    return location_invalid_dict(d, *args)


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


def network_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return network_valid_dict(d, *args)
    return network_invalid_dict(d, *args)


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


def project_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string(), "uuid": uuid4()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return project_valid_dict(d, *args)
    return project_invalid_dict(d, *args)


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


def provider_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string(), "type": random_provider_type()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return provider_valid_dict(d, *args)
    return provider_invalid_dict(d, *args)


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


def quota_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return quota_valid_dict(d, *args)
    return quota_invalid_dict(d, *args)


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


def region_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return region_valid_dict(d, *args)
    return region_invalid_dict(d, *args)


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


def service_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"endpoint": random_lower_string(), "name": random_lower_string()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return service_valid_dict(d, *args)
    return service_invalid_dict(d, *args)


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


def sla_schema_dict(*args, **kwargs) -> dict[str, Any]:
    start_date, end_date = random_start_end_dates()
    d = {"doc_uuid": uuid4(), "start_date": start_date, "end_date": end_date}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return sla_valid_dict(d, *args)
    return sla_invalid_dict(d, *args)


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


def user_group_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {"name": random_lower_string()}
    if kwargs.get("read", False):
        d["uid"] = uuid4()
    if kwargs.get("valid", True):
        return user_group_valid_dict(d, *args)
    return user_group_invalid_dict(d, *args)


def schema_size_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("short", "with_conn"):
            data[k] = True
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def schema_size_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("short", "with_conn"):
            data[k] = None
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def schema_size_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("valid", True):
        return schema_size_valid_dict(d, *args)
    return schema_size_invalid_dict(d, *args)


def pagination_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("page",):
            data["size"] = random_positive_int()
            data[k] = random_non_negative_int()
        elif k in ("size",):
            data[k] = random_positive_int()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def pagination_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("page",):
            data["size"] = random_positive_int()
            data[k] = -1
        elif k in ("size_0",):
            data["size"] = 0
        elif k in ("negative_size",):
            data["size"] = -1
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def pagination_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("valid", True):
        return pagination_valid_dict(d, *args)
    return pagination_invalid_dict(d, *args)


def db_query_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("skip", "limit"):
            data[k] = random_non_negative_int()
        elif k in ("sort",):
            data[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def db_query_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("limit", "skip"):
            data[k] = -1
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def db_query_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("valid", True):
        return db_query_valid_dict(d, *args)
    return db_query_invalid_dict(d, *args)
