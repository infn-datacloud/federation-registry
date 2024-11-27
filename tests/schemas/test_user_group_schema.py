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
from fed_reg.user_group.models import UserGroup
from fed_reg.user_group.schemas import (
    UserGroupBase,
    UserGroupBasePublic,
    UserGroupCreate,
    UserGroupRead,
    UserGroupReadPublic,
    UserGroupUpdate,
)


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


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test UserGroupBasePublic class' attribute values."""
    item = UserGroupBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("user_group_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    user_group_cls: type[UserGroupBase] | type[UserGroupCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on UserGroupBase, PrivateUserGroupCreate
    and SharedUserGroupCreate.
    """
    item = user_group_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test UserGroupUpdate class' attribute values."""
    item = UserGroupUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test UserGroupReadPublic class' attribute values."""
    uid = uuid4()
    item = UserGroupReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test UserGroupRead class' attribute values."""
    uid = uuid4()
    item = UserGroupRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: UserGroup) -> None:
    """Use the from_orm function of UserGroupReadPublic to read data from ORM."""
    item = UserGroupReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: UserGroup) -> None:
    """Use the from_orm function of UserGroupRead to read data from an ORM."""
    item = UserGroupRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for UserGroupBasePublic."""
    err_msg = rf"1 validation error for UserGroupBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        UserGroupBasePublic(**data)


@parametrize_with_cases("user_group_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    user_group_cls: type[UserGroupBase] | type[UserGroupCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to UserGroupBase, PrivateUserGroupCreate and
    SharedUserGroupCreate.
    """
    err_msg = rf"1 validation error for {user_group_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        user_group_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for UserGroupUpdate."""
    err_msg = rf"1 validation error for UserGroupUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        UserGroupUpdate(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for UserGroupReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for UserGroupReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        UserGroupReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for UserGroupRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for UserGroupRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        UserGroupRead(**data, uid=uid)
