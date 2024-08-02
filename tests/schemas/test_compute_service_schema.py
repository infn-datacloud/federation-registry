from typing import Any

from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    ComputeQuotaCreateExtended,
    ComputeServiceCreateExtended,
    PrivateFlavorCreateExtended,
    PrivateImageCreateExtended,
    SharedFlavorCreateExtended,
    SharedImageCreateExtended,
)
from fed_reg.service.enum import ComputeServiceName, ServiceType
from fed_reg.service.models import ComputeService
from fed_reg.service.schemas import (
    ComputeServiceBase,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    ComputeServiceUpdate,
)
from tests.create_dict import compute_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = compute_service_schema_dict()
    if key:
        d[key] = value
    item = ComputeServiceBase(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.COMPUTE.value
    assert item.name == d.get("name").value


@parametrize_with_cases("key, value", has_tag="base_public")
def test_read_public(
    compute_service_model: ComputeService, key: str, value: str
) -> None:
    if key:
        compute_service_model.__setattr__(key, value)
    item = ComputeServiceReadPublic.from_orm(compute_service_model)

    assert item.uid
    assert item.uid == compute_service_model.uid
    assert item.description == compute_service_model.description
    assert item.endpoint == compute_service_model.endpoint


@parametrize_with_cases("key, value", has_tag="base")
def test_read(compute_service_model: ComputeService, key: str, value: Any) -> None:
    if key:
        if isinstance(value, ComputeServiceName):
            value = value.value
        compute_service_model.__setattr__(key, value)
    item = ComputeServiceRead.from_orm(compute_service_model)

    assert item.uid
    assert item.uid == compute_service_model.uid
    assert item.description == compute_service_model.description
    assert item.endpoint == compute_service_model.endpoint
    assert item.type == compute_service_model.type
    assert item.name == compute_service_model.name


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = compute_service_schema_dict()
    if key:
        d[key] = value
    item = ComputeServiceUpdate(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.COMPUTE.value
    assert item.name == (d.get("name").value if d.get("name") else None)


@parametrize_with_cases("attr, values", has_tag="create_extended")
def test_create_extended(
    attr: str,
    values: list[ComputeQuotaCreateExtended]
    | list[PrivateFlavorCreateExtended | SharedFlavorCreateExtended]
    | list[PrivateImageCreateExtended | SharedImageCreateExtended],
) -> None:
    d = compute_service_schema_dict()
    d[attr] = values
    item = ComputeServiceCreateExtended(**d)
    assert item.__getattribute__(attr) == values


# TODO Test read extended classes
