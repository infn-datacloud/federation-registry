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
from tests.models.utils import identity_provider_model_dict
from tests.schemas.utils import identity_provider_schema_dict


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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test IdentityProviderBasePublic class' attribute values."""
    d = identity_provider_schema_dict(attr)
    item = IdentityProviderBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")


@parametrize_with_cases("identity_provider_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    identity_provider_cls: type[IdentityProviderBase] | type[IdentityProviderCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on IdentityProviderBase, PrivateIdentityProviderCreate
    and SharedIdentityProviderCreate.
    """
    d = identity_provider_schema_dict(attr)
    item = identity_provider_cls(**d)
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")
    assert item.group_claim == d.get("group_claim")


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test IdentityProviderUpdate class' attribute values."""
    d = identity_provider_schema_dict(attr)
    item = IdentityProviderUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")
    assert item.group_claim == d.get("group_claim")


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test IdentityProviderReadPublic class' attribute values."""
    d = identity_provider_schema_dict(attr, read=True)
    item = IdentityProviderReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test IdentityProviderRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = identity_provider_schema_dict(attr, read=True)
    item = IdentityProviderRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")
    assert item.group_claim == d.get("group_claim")


@parametrize_with_cases("identity_provider_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(
    identity_provider_cls: type[IdentityProvider], attr: str
) -> None:
    """Use the from_orm function of IdentityProviderReadPublic to read data from ORM."""
    model = identity_provider_cls(**identity_provider_model_dict(attr)).save()
    item = IdentityProviderReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.endpoint == model.endpoint


@parametrize_with_cases("identity_provider_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(
    identity_provider_cls: type[IdentityProvider], attr: str
) -> None:
    """Use the from_orm function of IdentityProviderRead to read data from an ORM."""
    model = identity_provider_cls(**identity_provider_model_dict(attr)).save()
    item = IdentityProviderRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.endpoint == model.endpoint
    assert item.group_claim == model.group_claim


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for IdentityProviderBasePublic."""
    with pytest.raises(ValueError):
        IdentityProviderBasePublic(**identity_provider_schema_dict(attr, valid=False))


@parametrize_with_cases("identity_provider_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    identity_provider_cls: type[IdentityProviderBase] | type[IdentityProviderCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to IdentityProviderBase, PrivateIdentityProviderCreate and
    SharedIdentityProviderCreate.
    """
    with pytest.raises(ValueError):
        identity_provider_cls(**identity_provider_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for IdentityProviderUpdate."""
    with pytest.raises(ValueError):
        IdentityProviderUpdate(**identity_provider_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for IdentityProviderReadPublic."""
    with pytest.raises(ValueError):
        IdentityProviderReadPublic(
            **identity_provider_schema_dict(attr, valid=False, read=True)
        )


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for IdentityProviderRead."""
    with pytest.raises(ValueError):
        IdentityProviderRead(
            **identity_provider_schema_dict(attr, valid=False, read=True)
        )
