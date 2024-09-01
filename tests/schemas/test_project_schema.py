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
from tests.models.utils import project_model_dict
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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test ProjectBasePublic class' attribute values."""
    d = project_schema_dict(attr)
    item = ProjectBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("project_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    project_cls: type[ProjectBase] | type[ProjectCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on ProjectBase, PrivateProjectCreate
    and SharedProjectCreate.
    """
    d = project_schema_dict(attr)
    item = project_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test ProjectUpdate class' attribute values."""
    d = project_schema_dict(attr)
    item = ProjectUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == (d.get("uuid").hex if d.get("uuid", None) else None)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test ProjectReadPublic class' attribute values."""
    d = project_schema_dict(attr, read=True)
    item = ProjectReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test ProjectRead class' attribute values."""
    d = project_schema_dict(attr, read=True)
    item = ProjectRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("project_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(project_cls: type[Project], attr: str) -> None:
    """Use the from_orm function of ProjectReadPublic to read data from ORM."""
    model = project_cls(**project_model_dict(attr)).save()
    item = ProjectReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("project_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(project_cls: type[Project], attr: str) -> None:
    """Use the from_orm function of ProjectRead to read data from an ORM."""
    model = project_cls(**project_model_dict(attr)).save()
    item = ProjectRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for ProjectBasePublic."""
    with pytest.raises(ValueError):
        ProjectBasePublic(**project_schema_dict(attr, valid=False))


@parametrize_with_cases("project_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    project_cls: type[ProjectBase] | type[ProjectCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to ProjectBase, PrivateProjectCreate and
    SharedProjectCreate.
    """
    with pytest.raises(ValueError):
        project_cls(**project_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for ProjectUpdate."""
    with pytest.raises(ValueError):
        ProjectUpdate(**project_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for ProjectReadPublic."""
    with pytest.raises(ValueError):
        ProjectReadPublic(**project_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for ProjectRead."""
    with pytest.raises(ValueError):
        ProjectRead(**project_schema_dict(attr, valid=False, read=True))
