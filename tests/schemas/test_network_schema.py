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
from tests.models.utils import network_model_dict
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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test NetworkBasePublic class' attribute values."""
    d = network_schema_dict(attr)
    item = NetworkBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("network_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    network_cls: type[NetworkBase]
    | type[PrivateNetworkCreate]
    | type[SharedNetworkCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on NetworkBase, PrivateNetworkCreate and SharedNetworkCreate.
    """
    d = network_schema_dict(attr)
    item = network_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.is_router_external == d.get("is_router_external", False)
    assert item.is_default == d.get("is_default", False)
    assert item.mtu == d.get("mtu", None)
    assert item.proxy_host == d.get("proxy_host", None)
    assert item.proxy_user == d.get("proxy_user", None)
    assert item.tags == d.get("tags", [])


def test_create_private() -> None:
    """Test PrivateNetworkCreate class' attribute values."""
    item = PrivateNetworkCreate(**network_schema_dict())
    assert item.is_shared is False


def test_create_shared() -> None:
    """Test SharedNetworkCreate class' attribute values."""
    item = SharedNetworkCreate(**network_schema_dict())
    assert item.is_shared is True


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test NetworkUpdate class' attribute values."""
    d = network_schema_dict(attr)
    item = NetworkUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == (d.get("uuid").hex if d.get("uuid", None) else None)
    assert item.is_router_external == d.get("is_router_external", False)
    assert item.is_default == d.get("is_default", False)
    assert item.mtu == d.get("mtu", None)
    assert item.proxy_host == d.get("proxy_host", None)
    assert item.proxy_user == d.get("proxy_user", None)
    assert item.tags == d.get("tags", [])


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test NetworkReadPublic class' attribute values."""
    d = network_schema_dict(attr, read=True)
    item = NetworkReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test NetworkRead class' attribute values.

    Consider also cases where we need to set the is_shared attribute (usually populated
    by the correct model).
    """
    d = network_schema_dict(attr, read=True)
    item = NetworkRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == (d.get("uuid").hex if d.get("uuid") else None)
    assert item.is_router_external == d.get("is_router_external", False)
    assert item.is_default == d.get("is_default", False)
    assert item.mtu == d.get("mtu", None)
    assert item.proxy_host == d.get("proxy_host", None)
    assert item.proxy_user == d.get("proxy_user", None)
    assert item.tags == d.get("tags", [])


@parametrize_with_cases("network_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(
    network_cls: type[Network] | type[PrivateNetwork] | type[SharedNetwork], attr: str
) -> None:
    """Use the from_orm function of NetworkReadPublic to read data from an ORM."""
    model = network_cls(**network_model_dict(attr)).save()
    item = NetworkReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("network_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(
    network_cls: type[Network] | type[PrivateNetwork] | type[SharedNetwork], attr: str
) -> None:
    """Use the from_orm function of NetworkRead to read data from an ORM."""
    model = network_cls(**network_model_dict(attr)).save()
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


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for NetworkBasePublic."""
    with pytest.raises(ValueError):
        NetworkBasePublic(**network_schema_dict(attr, valid=False))


@parametrize_with_cases("network_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    network_cls: type[NetworkBase]
    | type[PrivateNetworkCreate]
    | type[SharedNetworkCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to NetworkBase, PrivateNetworkCreate and SharedNetworkCreate.
    """
    with pytest.raises(ValueError):
        network_cls(**network_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for NetworkUpdate."""
    with pytest.raises(ValueError):
        NetworkUpdate(**network_schema_dict(attr, valid=False))


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateNetworkCreate and SharedNetworkCreate."""
    with pytest.raises(ValidationError):
        PrivateNetworkCreate(**network_schema_dict(), is_shared=True)
    with pytest.raises(ValidationError):
        SharedNetworkCreate(**network_schema_dict(), is_shared=False)


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for NetworkReadPublic."""
    with pytest.raises(ValueError):
        NetworkReadPublic(**network_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for NetworkRead."""
    with pytest.raises(ValueError):
        NetworkRead(**network_schema_dict(attr, valid=False, read=True))
