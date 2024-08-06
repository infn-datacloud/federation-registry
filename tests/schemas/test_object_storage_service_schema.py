from typing import Any

from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    ObjectStoreQuotaCreateExtended,
    ObjectStoreServiceCreateExtended,
)
from fed_reg.service.enum import ObjectStoreServiceName, ServiceType
from fed_reg.service.models import ObjectStoreService
from fed_reg.service.schemas import (
    ObjectStoreServiceBase,
    ObjectStoreServiceRead,
    ObjectStoreServiceReadPublic,
    ObjectStoreServiceUpdate,
)
from tests.schemas.utils import object_store_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = object_store_service_schema_dict()
    if key:
        d[key] = value
    item = ObjectStoreServiceBase(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.OBJECT_STORE.value
    assert item.name == d.get("name").value


@parametrize_with_cases("key, value", has_tag="base_public")
def test_read_public(
    object_store_service_model: ObjectStoreService, key: str, value: str
) -> None:
    if key:
        object_store_service_model.__setattr__(key, value)
    item = ObjectStoreServiceReadPublic.from_orm(object_store_service_model)

    assert item.uid
    assert item.uid == object_store_service_model.uid
    assert item.description == object_store_service_model.description
    assert item.endpoint == object_store_service_model.endpoint


@parametrize_with_cases("key, value", has_tag="base")
def test_read(
    object_store_service_model: ObjectStoreService, key: str, value: Any
) -> None:
    if key:
        if isinstance(value, ObjectStoreServiceName):
            value = value.value
        object_store_service_model.__setattr__(key, value)
    item = ObjectStoreServiceRead.from_orm(object_store_service_model)

    assert item.uid
    assert item.uid == object_store_service_model.uid
    assert item.description == object_store_service_model.description
    assert item.endpoint == object_store_service_model.endpoint
    assert item.type == object_store_service_model.type
    assert item.name == object_store_service_model.name


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = object_store_service_schema_dict()
    if key:
        d[key] = value
    item = ObjectStoreServiceUpdate(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.OBJECT_STORE.value
    assert item.name == (d.get("name").value if d.get("name") else None)


@parametrize_with_cases("quotas", has_tag="create_extended")
def test_create_extended(quotas: list[ObjectStoreQuotaCreateExtended]) -> None:
    d = object_store_service_schema_dict()
    d["quotas"] = quotas
    item = ObjectStoreServiceCreateExtended(**d)
    assert item.quotas == quotas


# TODO Test read extended classes
