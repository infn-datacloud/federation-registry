import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.user_group.models import UserGroup
from fed_reg.user_group.schemas import (
    UserGroupBase,
    UserGroupBasePublic,
    UserGroupCreate,
    UserGroupRead,
    UserGroupReadPublic,
    UserGroupUpdate,
)
from tests.create_dict import user_group_model_dict, user_group_schema_dict


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(UserGroupBasePublic, BaseNode)

    assert issubclass(UserGroupBase, UserGroupBasePublic)

    assert issubclass(UserGroupUpdate, UserGroupBase)
    assert issubclass(UserGroupUpdate, BaseNodeCreate)

    assert issubclass(UserGroupReadPublic, BaseNodeRead)
    assert issubclass(UserGroupReadPublic, BaseReadPublic)
    assert issubclass(UserGroupReadPublic, UserGroupBasePublic)
    assert UserGroupReadPublic.__config__.orm_mode

    assert issubclass(UserGroupRead, BaseNodeRead)
    assert issubclass(UserGroupRead, BaseReadPrivate)
    assert issubclass(UserGroupRead, UserGroupBase)
    assert UserGroupRead.__config__.orm_mode

    assert issubclass(UserGroupCreate, UserGroupBase)
    assert issubclass(UserGroupCreate, BaseNodeCreate)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test UserGroupBasePublic class' attribute values."""
    d = user_group_schema_dict(attr)
    item = UserGroupBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("user_group_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    user_group_cls: type[UserGroupBase] | type[UserGroupCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on UserGroupBase, PrivateUserGroupCreate
    and SharedUserGroupCreate.
    """
    d = user_group_schema_dict(attr)
    item = user_group_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test UserGroupUpdate class' attribute values."""
    d = user_group_schema_dict(attr)
    item = UserGroupUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test UserGroupReadPublic class' attribute values."""
    d = user_group_schema_dict(attr, read=True)
    item = UserGroupReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test UserGroupRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = user_group_schema_dict(attr, read=True)
    item = UserGroupRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("user_group_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(user_group_cls: type[UserGroup], attr: str) -> None:
    """Use the from_orm function of UserGroupReadPublic to read data from ORM."""
    model = user_group_cls(**user_group_model_dict(attr)).save()
    item = UserGroupReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("user_group_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(user_group_cls: type[UserGroup], attr: str) -> None:
    """Use the from_orm function of UserGroupRead to read data from an ORM."""
    model = user_group_cls(**user_group_model_dict(attr)).save()
    item = UserGroupRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for UserGroupBasePublic."""
    with pytest.raises(ValueError):
        UserGroupBasePublic(**user_group_schema_dict(attr, valid=False))


@parametrize_with_cases("user_group_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    user_group_cls: type[UserGroupBase] | type[UserGroupCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to UserGroupBase, PrivateUserGroupCreate and
    SharedUserGroupCreate.
    """
    with pytest.raises(ValueError):
        user_group_cls(**user_group_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for UserGroupUpdate."""
    with pytest.raises(ValueError):
        UserGroupUpdate(**user_group_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for UserGroupReadPublic."""
    with pytest.raises(ValueError):
        UserGroupReadPublic(**user_group_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for UserGroupRead."""
    with pytest.raises(ValueError):
        UserGroupRead(**user_group_schema_dict(attr, valid=False, read=True))
