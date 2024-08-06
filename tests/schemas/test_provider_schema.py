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
from tests.models.utils import provider_model_dict
from tests.schemas.utils import provider_schema_dict


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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test ProviderBasePublic class' attribute values."""
    d = provider_schema_dict(attr)
    item = ProviderBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.type == d.get("type").value


@parametrize_with_cases("provider_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    provider_cls: type[ProviderBase] | type[ProviderCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on ProviderBase, PrivateProviderCreate
    and SharedProviderCreate.
    """
    d = provider_schema_dict(attr)
    item = provider_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.type == d.get("type").value
    assert item.status == d.get("status", ProviderStatus.ACTIVE).value
    assert item.is_public == d.get("is_public", False)
    assert item.support_emails == d.get("support_emails", [])


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test ProviderUpdate class' attribute values."""
    d = provider_schema_dict(attr)
    item = ProviderUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.type == (d.get("type").value if d.get("type", None) else None)
    assert item.status == d.get("status", ProviderStatus.ACTIVE).value
    assert item.is_public == d.get("is_public", False)
    assert item.support_emails == d.get("support_emails", [])


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test ProviderReadPublic class' attribute values."""
    d = provider_schema_dict(attr, read=True)
    item = ProviderReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.type == d.get("type").value


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test ProviderRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = provider_schema_dict(attr, read=True)
    item = ProviderRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.type == d.get("type").value
    assert item.status == d.get("status", ProviderStatus.ACTIVE).value
    assert item.is_public == d.get("is_public", False)
    assert item.support_emails == d.get("support_emails", [])


@parametrize_with_cases("provider_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(provider_cls: type[Provider], attr: str) -> None:
    """Use the from_orm function of ProviderReadPublic to read data from ORM."""
    model = provider_cls(**provider_model_dict(attr)).save()
    item = ProviderReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.type == model.type


@parametrize_with_cases("provider_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(provider_cls: type[Provider], attr: str) -> None:
    """Use the from_orm function of ProviderRead to read data from an ORM."""
    model = provider_cls(**provider_model_dict(attr)).save()
    item = ProviderRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.type == model.type
    assert item.status == model.status
    assert item.is_public == model.is_public
    assert item.support_emails == model.support_emails


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for ProviderBasePublic."""
    with pytest.raises(ValueError):
        ProviderBasePublic(**provider_schema_dict(attr, valid=False))


@parametrize_with_cases("provider_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    provider_cls: type[ProviderBase] | type[ProviderCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to ProviderBase, PrivateProviderCreate and
    SharedProviderCreate.
    """
    with pytest.raises(ValueError):
        provider_cls(**provider_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for ProviderUpdate."""
    with pytest.raises(ValueError):
        ProviderUpdate(**provider_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for ProviderReadPublic."""
    with pytest.raises(ValueError):
        ProviderReadPublic(**provider_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for ProviderRead."""
    with pytest.raises(ValueError):
        ProviderRead(**provider_schema_dict(attr, valid=False, read=True))
