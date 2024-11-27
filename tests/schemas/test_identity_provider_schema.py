from typing import Any
from uuid import uuid4

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.identity_provider.schemas import (
    IdentityProviderBase,
    IdentityProviderBasePublic,
    IdentityProviderCreate,
    IdentityProviderRead,
    IdentityProviderReadPublic,
    IdentityProviderUpdate,
)
from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(IdentityProviderBasePublic, BaseNode)

    assert issubclass(IdentityProviderBase, IdentityProviderBasePublic)

    assert issubclass(IdentityProviderUpdate, IdentityProviderBase)
    assert issubclass(IdentityProviderUpdate, BaseNodeCreate)

    assert issubclass(IdentityProviderReadPublic, BaseNodeRead)
    assert issubclass(IdentityProviderReadPublic, BaseReadPublic)
    assert issubclass(IdentityProviderReadPublic, IdentityProviderBasePublic)
    assert IdentityProviderReadPublic.__config__.orm_mode

    assert issubclass(IdentityProviderRead, BaseNodeRead)
    assert issubclass(IdentityProviderRead, BaseReadPrivate)
    assert issubclass(IdentityProviderRead, IdentityProviderBase)
    assert IdentityProviderRead.__config__.orm_mode

    assert issubclass(IdentityProviderCreate, IdentityProviderBase)
    assert issubclass(IdentityProviderCreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test IdentityProviderBasePublic class' attribute values."""
    item = IdentityProviderBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.endpoint == data.get("endpoint")


@parametrize_with_cases("identity_provider_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    identity_provider_cls: type[IdentityProviderBase] | type[IdentityProviderCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on IdentityProviderBase, PrivateIdentityProviderCreate
    and SharedIdentityProviderCreate.
    """
    item = identity_provider_cls(**data)
    assert item.description == data.get("description", "")
    assert item.endpoint == data.get("endpoint")
    assert item.group_claim == data.get("group_claim")


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test IdentityProviderUpdate class' attribute values."""
    item = IdentityProviderUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.endpoint == data.get("endpoint")
    assert item.group_claim == data.get("group_claim")


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test IdentityProviderReadPublic class' attribute values."""
    uid = uuid4()
    item = IdentityProviderReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.endpoint == data.get("endpoint")


@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_read(data: dict[str, Any]) -> None:
    """Test IdentityProviderRead class' attribute values."""
    uid = uuid4()
    item = IdentityProviderRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.endpoint == data.get("endpoint")
    assert item.group_claim == data.get("group_claim")


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: IdentityProvider) -> None:
    """Use the from_orm function of IdentityProviderReadPublic to read data from ORM."""
    item = IdentityProviderReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.endpoint == model.endpoint


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: IdentityProvider) -> None:
    """Use the from_orm function of IdentityProviderRead to read data from an ORM."""
    item = IdentityProviderRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.endpoint == model.endpoint
    assert item.group_claim == model.group_claim


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for IdentityProviderBasePublic."""
    err_msg = rf"1 validation error for IdentityProviderBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        IdentityProviderBasePublic(**data)


@parametrize_with_cases("identity_provider_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    identity_provider_cls: type[IdentityProviderBase] | type[IdentityProviderCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create."""
    err_msg = rf"1 validation error for {identity_provider_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        identity_provider_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for IdentityProviderUpdate."""
    err_msg = rf"1 validation error for IdentityProviderUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        IdentityProviderUpdate(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for IdentityProviderReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for IdentityProviderReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        IdentityProviderReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for IdentityProviderRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for IdentityProviderRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        IdentityProviderRead(**data, uid=uid)
