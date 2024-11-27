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
from fed_reg.project.models import Project
from fed_reg.project.schemas import (
    ProjectBase,
    ProjectBasePublic,
    ProjectCreate,
    ProjectRead,
    ProjectReadPublic,
    ProjectUpdate,
)
from tests.schemas.utils import project_schema_dict


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(ProjectBasePublic, BaseNode)

    assert issubclass(ProjectBase, ProjectBasePublic)

    assert issubclass(ProjectUpdate, ProjectBase)
    assert issubclass(ProjectUpdate, BaseNodeCreate)

    assert issubclass(ProjectReadPublic, BaseNodeRead)
    assert issubclass(ProjectReadPublic, BaseReadPublic)
    assert issubclass(ProjectReadPublic, ProjectBasePublic)
    assert ProjectReadPublic.__config__.orm_mode

    assert issubclass(ProjectRead, BaseNodeRead)
    assert issubclass(ProjectRead, BaseReadPrivate)
    assert issubclass(ProjectRead, ProjectBase)
    assert ProjectRead.__config__.orm_mode

    assert issubclass(ProjectCreate, ProjectBase)
    assert issubclass(ProjectCreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test ProjectBasePublic class' attribute values."""
    item = ProjectBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("project_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    project_cls: type[ProjectBase] | type[ProjectCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on ProjectBase, PrivateProjectCreate
    and SharedProjectCreate.
    """
    item = project_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test ProjectUpdate class' attribute values."""
    item = ProjectUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == (data.get("uuid").hex if data.get("uuid", None) else None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test ProjectReadPublic class' attribute values."""
    uid = uuid4()
    item = ProjectReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test ProjectRead class' attribute values."""
    uid = uuid4()
    item = ProjectRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Project) -> None:
    """Use the from_orm function of ProjectReadPublic to read data from ORM."""
    item = ProjectReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Project) -> None:
    """Use the from_orm function of ProjectRead to read data from an ORM."""
    item = ProjectRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProjectBasePublic."""
    err_msg = rf"1 validation error for ProjectBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProjectBasePublic(**data)


@parametrize_with_cases("project_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    project_cls: type[ProjectBase] | type[ProjectCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to ProjectBase, PrivateProjectCreate and
    SharedProjectCreate.
    """
    err_msg = rf"1 validation error for {project_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        project_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProjectUpdate."""
    err_msg = rf"1 validation error for ProjectUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProjectUpdate(**project_schema_dict(attr, valid=False))


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProjectReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for ProjectReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProjectReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ProjectRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for ProjectRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ProjectRead(**data, uid=uid)
