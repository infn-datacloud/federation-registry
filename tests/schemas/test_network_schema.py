from typing import Any

import pytest
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.network.schemas import (
    NetworkBase,
    NetworkBasePublic,
    NetworkRead,
    NetworkReadPublic,
    NetworkUpdate,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from tests.create_dict import network_schema_dict


def test_classes_inheritance():
    assert issubclass(NetworkBasePublic, BaseNode)

    assert issubclass(NetworkBase, NetworkBasePublic)

    assert issubclass(PrivateNetworkCreate, NetworkBase)
    assert issubclass(PrivateNetworkCreate, BaseNodeCreate)

    assert issubclass(SharedNetworkCreate, NetworkBase)
    assert issubclass(SharedNetworkCreate, BaseNodeCreate)

    assert issubclass(NetworkUpdate, NetworkBase)
    assert issubclass(NetworkUpdate, BaseNodeCreate)

    assert issubclass(NetworkReadPublic, BaseNodeRead)
    assert issubclass(NetworkReadPublic, BaseReadPublic)
    assert issubclass(NetworkReadPublic, NetworkBasePublic)

    assert issubclass(NetworkRead, BaseNodeRead)
    assert issubclass(NetworkRead, BaseReadPrivate)
    assert issubclass(NetworkRead, NetworkBase)


@parametrize_with_cases("key, value", has_tag="base_public")
def test_base_public(key: str, value: str) -> None:
    d = network_schema_dict()
    if key:
        d[key] = value
    item = NetworkBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = network_schema_dict()
    if key:
        d[key] = value
    item = NetworkBase(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.is_router_external == d.get("is_router_external", False)
    assert item.is_default == d.get("is_default", False)
    assert item.mtu == d.get("mtu")
    assert item.proxy_host == d.get("proxy_host")
    assert item.proxy_user == d.get("proxy_user")
    assert item.tags == d.get("tags", [])


@parametrize_with_cases("key, value", has_tag="base")
def test_create_private(key: str, value: Any) -> None:
    d = network_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = PrivateNetworkCreate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.is_router_external == d.get("is_router_external", False)
    assert item.is_default == d.get("is_default", False)
    assert item.mtu == d.get("mtu")
    assert item.proxy_host == d.get("proxy_host")
    assert item.proxy_user == d.get("proxy_user")
    assert item.tags == d.get("tags", [])
    assert item.is_shared is False


@parametrize_with_cases("key, value", has_tag="base")
def test_create_shared(key: str, value: Any) -> None:
    d = network_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = SharedNetworkCreate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.is_router_external == d.get("is_router_external", False)
    assert item.is_default == d.get("is_default", False)
    assert item.mtu == d.get("mtu")
    assert item.proxy_host == d.get("proxy_host")
    assert item.proxy_user == d.get("proxy_user")
    assert item.tags == d.get("tags", [])
    assert item.is_shared is True


def test_invalid_visibility() -> None:
    with pytest.raises(ValidationError):
        PrivateNetworkCreate(**network_schema_dict(), is_shared=True)
    with pytest.raises(ValidationError):
        SharedNetworkCreate(**network_schema_dict(), is_shared=False)


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = network_schema_dict()
    if key:
        d[key] = value
    item = NetworkUpdate(**d)
    assert item.name == d.get("name")
    assert item.uuid == (d.get("uuid").hex if d.get("uuid") else None)


@parametrize_with_cases("key, value", has_tag="base_public")
@parametrize_with_cases("network_model", has_tag="model")
def test_read_public(network_model: Network, key: str, value: str) -> None:
    if key:
        network_model.__setattr__(key, value)
    item = NetworkReadPublic.from_orm(network_model)

    assert item.uid
    assert item.uid == network_model.uid
    assert item.description == network_model.description
    assert item.name == network_model.name
    assert item.uuid == network_model.uuid


@parametrize_with_cases("key, value", has_tag="base")
@parametrize_with_cases("network_model", has_tag="model")
def test_read(network_model: Network, key: str, value: Any) -> None:
    if key:
        network_model.__setattr__(key, value)
    item = NetworkRead.from_orm(network_model)

    assert item.uid
    assert item.uid == network_model.uid
    assert item.description == network_model.description
    assert item.name == network_model.name
    assert item.uuid == network_model.uuid
    assert item.is_router_external == network_model.is_router_external
    assert item.is_default == network_model.is_default
    assert item.mtu == network_model.mtu
    assert item.proxy_host == network_model.proxy_host
    assert item.proxy_user == network_model.proxy_user
    assert item.tags == network_model.tags

    if isinstance(network_model, SharedNetwork):
        assert item.is_shared is True
    elif isinstance(network_model, PrivateNetwork):
        assert item.is_shared is False
    elif isinstance(network_model, Network):
        assert item.is_shared is None
