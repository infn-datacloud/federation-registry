from typing import Any

from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    NetworkQuotaCreateExtended,
    NetworkServiceCreateExtended,
    PrivateNetworkCreateExtended,
    SharedNetworkCreateExtended,
)
from fed_reg.service.enum import NetworkServiceName, ServiceType
from fed_reg.service.models import NetworkService
from fed_reg.service.schemas import (
    NetworkServiceBase,
    NetworkServiceRead,
    NetworkServiceReadPublic,
    NetworkServiceUpdate,
)
from tests.create_dict import network_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = network_service_schema_dict()
    if key:
        d[key] = value
    item = NetworkServiceBase(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.NETWORK.value
    assert item.name == d.get("name").value


@parametrize_with_cases("key, value", has_tag="base_public")
def test_read_public(
    network_service_model: NetworkService, key: str, value: str
) -> None:
    if key:
        network_service_model.__setattr__(key, value)
    item = NetworkServiceReadPublic.from_orm(network_service_model)

    assert item.uid
    assert item.uid == network_service_model.uid
    assert item.description == network_service_model.description
    assert item.endpoint == network_service_model.endpoint


@parametrize_with_cases("key, value", has_tag="base")
def test_read(network_service_model: NetworkService, key: str, value: Any) -> None:
    if key:
        if isinstance(value, NetworkServiceName):
            value = value.value
        network_service_model.__setattr__(key, value)
    item = NetworkServiceRead.from_orm(network_service_model)

    assert item.uid
    assert item.uid == network_service_model.uid
    assert item.description == network_service_model.description
    assert item.endpoint == network_service_model.endpoint
    assert item.type == network_service_model.type
    assert item.name == network_service_model.name


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = network_service_schema_dict()
    if key:
        d[key] = value
    item = NetworkServiceUpdate(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.NETWORK.value
    assert item.name == (d.get("name").value if d.get("name") else None)


@parametrize_with_cases("attr, values", has_tag="create_extended")
def test_create_extended(
    attr: str,
    values: list[NetworkQuotaCreateExtended]
    | list[PrivateNetworkCreateExtended | SharedNetworkCreateExtended],
) -> None:
    d = network_service_schema_dict()
    d[attr] = values
    item = NetworkServiceCreateExtended(**d)
    assert item.__getattribute__(attr) == values


# TODO Test read extended classes
