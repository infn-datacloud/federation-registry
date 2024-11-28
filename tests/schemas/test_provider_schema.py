from typing import Any
from uuid import uuid4

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.provider.enum import ProviderStatus
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas import (
    ProviderBase,
    ProviderBasePublic,
    ProviderCreate,
    ProviderRead,
    ProviderReadPublic,
    ProviderUpdate,
)


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(ProviderBasePublic, BaseNode)

    assert issubclass(ProviderBase, ProviderBasePublic)

    assert issubclass(ProviderUpdate, ProviderBase)
    assert issubclass(ProviderUpdate, BaseNodeCreate)

    assert issubclass(ProviderReadPublic, BaseNodeRead)
    assert issubclass(ProviderReadPublic, BaseReadPublic)
    assert issubclass(ProviderReadPublic, ProviderBasePublic)
    assert ProviderReadPublic.__config__.orm_mode

    assert issubclass(ProviderRead, BaseNodeRead)
    assert issubclass(ProviderRead, BaseReadPrivate)
    assert issubclass(ProviderRead, ProviderBase)
    assert ProviderRead.__config__.orm_mode

    assert issubclass(ProviderCreate, ProviderBase)
    assert issubclass(ProviderCreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test ProviderBasePublic class' attribute values."""
    item = ProviderBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.type == data.get("type").value


@parametrize_with_cases("provider_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    provider_cls: type[ProviderBase] | type[ProviderCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on ProviderBase, PrivateProviderCreate
    and SharedProviderCreate.
    """
    item = provider_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.type == data.get("type").value
    assert item.status == data.get("status", ProviderStatus.ACTIVE).value
    assert item.is_public == data.get("is_public", False)
    assert item.support_emails == data.get("support_emails", [])


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test ProviderUpdate class' attribute values."""
    item = ProviderUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.type == (data.get("type").value if data.get("type", None) else None)
    assert item.status == data.get("status", ProviderStatus.ACTIVE).value
    assert item.is_public == data.get("is_public", False)
    assert item.support_emails == data.get("support_emails", [])


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test ProviderReadPublic class' attribute values."""
    uid = uuid4()
    item = ProviderReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.type == data.get("type").value


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test ProviderRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    uid = uuid4()
    item = ProviderRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.type == data.get("type").value
    assert item.status == data.get("status", ProviderStatus.ACTIVE).value
    assert item.is_public == data.get("is_public", False)
    assert item.support_emails == data.get("support_emails", [])


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Provider) -> None:
    """Use the from_orm function of ProviderReadPublic to read data from ORM."""
    item = ProviderReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.type == model.type


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Provider) -> None:
    """Use the from_orm function of ProviderRead to read data from an ORM."""
    item = ProviderRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.type == model.type
    assert item.status == model.status
    assert item.is_public == model.is_public
    assert item.support_emails == model.support_emails


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProviderBasePublic."""
    err_msg = rf"1 validation error for ProviderBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProviderBasePublic(**data)


@parametrize_with_cases("provider_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    provider_cls: type[ProviderBase] | type[ProviderCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to ProviderBase, PrivateProviderCreate and
    SharedProviderCreate.
    """
    err_msg = rf"1 validation error for {provider_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        provider_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProviderUpdate."""
    err_msg = rf"1 validation error for ProviderUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProviderUpdate(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProviderReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for ProviderReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProviderReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProviderRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for ProviderRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProviderRead(**data, uid=uid)
