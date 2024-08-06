from typing import Any

from pytest_cases import parametrize_with_cases

from fed_reg.service.enum import IdentityServiceName, ServiceType
from fed_reg.service.models import IdentityService
from fed_reg.service.schemas import (
    IdentityServiceBase,
    IdentityServiceRead,
    IdentityServiceReadPublic,
    IdentityServiceUpdate,
)
from tests.schemas.utils import identity_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = identity_service_schema_dict()
    if key:
        d[key] = value
    item = IdentityServiceBase(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.IDENTITY.value
    assert item.name == d.get("name").value


@parametrize_with_cases("key, value", has_tag="base_public")
def test_read_public(
    identity_service_model: IdentityService, key: str, value: str
) -> None:
    if key:
        identity_service_model.__setattr__(key, value)
    item = IdentityServiceReadPublic.from_orm(identity_service_model)

    assert item.uid
    assert item.uid == identity_service_model.uid
    assert item.description == identity_service_model.description
    assert item.endpoint == identity_service_model.endpoint


@parametrize_with_cases("key, value", has_tag="base")
def test_read(identity_service_model: IdentityService, key: str, value: Any) -> None:
    if key:
        if isinstance(value, IdentityServiceName):
            value = value.value
        identity_service_model.__setattr__(key, value)
    item = IdentityServiceRead.from_orm(identity_service_model)

    assert item.uid
    assert item.uid == identity_service_model.uid
    assert item.description == identity_service_model.description
    assert item.endpoint == identity_service_model.endpoint
    assert item.type == identity_service_model.type
    assert item.name == identity_service_model.name


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = identity_service_schema_dict()
    if key:
        d[key] = value
    item = IdentityServiceUpdate(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.IDENTITY.value
    assert item.name == (d.get("name").value if d.get("name") else None)


# TODO Test read extended classes
