from typing import Any
from uuid import uuid4

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
from tests.schemas.utils import network_schema_dict


def test_classes_inheritance():
    """Test pydantic schema inheritance."""
    assert issubclass(NetworkBasePublic, BaseNode)

    assert issubclass(NetworkBase, NetworkBasePublic)

    assert issubclass(NetworkUpdate, NetworkBase)
    assert issubclass(NetworkUpdate, BaseNodeCreate)

    assert issubclass(NetworkReadPublic, BaseNodeRead)
    assert issubclass(NetworkReadPublic, BaseReadPublic)
    assert issubclass(NetworkReadPublic, NetworkBasePublic)
    assert NetworkReadPublic.__config__.orm_mode

    assert issubclass(NetworkRead, BaseNodeRead)
    assert issubclass(NetworkRead, BaseReadPrivate)
    assert issubclass(NetworkRead, NetworkBase)
    assert NetworkRead.__config__.orm_mode

    assert issubclass(PrivateNetworkCreate, NetworkBase)
    assert issubclass(PrivateNetworkCreate, BaseNodeCreate)

    assert issubclass(SharedNetworkCreate, NetworkBase)
    assert issubclass(SharedNetworkCreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test NetworkBasePublic class' attribute values."""
    item = NetworkBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("network_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    network_cls: type[NetworkBase]
    | type[PrivateNetworkCreate]
    | type[SharedNetworkCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on NetworkBase, PrivateNetworkCreate and SharedNetworkCreate.
    """
    item = network_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex
    assert item.is_router_external == data.get("is_router_external", False)
    assert item.is_default == data.get("is_default", False)
    assert item.mtu == data.get("mtu", None)
    assert item.proxy_host == data.get("proxy_host", None)
    assert item.proxy_user == data.get("proxy_user", None)
    assert item.tags == data.get("tags", [])

    if isinstance(item, PrivateNetworkCreate):
        assert not item.is_shared
    if isinstance(item, SharedNetworkCreate):
        assert item.is_shared


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test NetworkUpdate class' attribute values."""
    item = NetworkUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == (data.get("uuid").hex if data.get("uuid", None) else None)
    assert item.is_router_external == data.get("is_router_external", False)
    assert item.is_default == data.get("is_default", False)
    assert item.mtu == data.get("mtu", None)
    assert item.proxy_host == data.get("proxy_host", None)
    assert item.proxy_user == data.get("proxy_user", None)
    assert item.tags == data.get("tags", [])


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test NetworkReadPublic class' attribute values."""
    uid = uuid4()
    item = NetworkReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test NetworkRead class' attribute values.

    Consider also cases where we need to set the is_shared attribute (usually populated
    by the correct model).
    """
    uid = uuid4()
    item = NetworkRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == (data.get("uuid").hex if data.get("uuid") else None)
    assert item.is_router_external == data.get("is_router_external", False)
    assert item.is_default == data.get("is_default", False)
    assert item.mtu == data.get("mtu", None)
    assert item.proxy_host == data.get("proxy_host", None)
    assert item.proxy_user == data.get("proxy_user", None)
    assert item.tags == data.get("tags", [])


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Network | PrivateNetwork | SharedNetwork) -> None:
    """Use the from_orm function of NetworkReadPublic to read data from an ORM."""
    item = NetworkReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Network | PrivateNetwork | SharedNetwork) -> None:
    """Use the from_orm function of NetworkRead to read data from an ORM."""
    item = NetworkRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid
    assert item.is_router_external == model.is_router_external
    assert item.is_default == model.is_default
    assert item.mtu == model.mtu
    assert item.proxy_host == model.proxy_host
    assert item.proxy_user == model.proxy_user
    assert item.tags == model.tags
    if isinstance(model, (PrivateNetwork, SharedNetwork)):
        assert item.is_shared == model.is_shared
    else:
        assert item.is_shared is None


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for NetworkBasePublic."""
    err_msg = rf"1 validation error for NetworkBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        NetworkBasePublic(**data)


@parametrize_with_cases("network_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    network_cls: type[NetworkBase]
    | type[PrivateNetworkCreate]
    | type[SharedNetworkCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to NetworkBase, PrivateNetworkCreate and SharedNetworkCreate.
    """
    err_msg = rf"1 validation error for {network_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        network_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for NetworkUpdate."""
    err_msg = rf"1 validation error for NetworkUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        NetworkUpdate(**data)


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateNetworkCreate and SharedNetworkCreate."""
    err_msg = r"1 validation error for PrivateNetworkCreate\sis_shared"
    with pytest.raises(ValidationError, match=err_msg):
        PrivateNetworkCreate(**network_schema_dict(), is_shared=True)
    err_msg = r"1 validation error for SharedNetworkCreate\sis_shared"
    with pytest.raises(ValidationError, match=err_msg):
        SharedNetworkCreate(**network_schema_dict(), is_shared=False)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for NetworkReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for NetworkReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        NetworkReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for NetworkRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for NetworkRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        NetworkRead(**data, uid=uid)
