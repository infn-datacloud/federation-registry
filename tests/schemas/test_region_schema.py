import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.region.models import Region
from fed_reg.region.schemas import (
    RegionBase,
    RegionBasePublic,
    RegionCreate,
    RegionRead,
    RegionReadPublic,
    RegionUpdate,
)
from tests.models.utils import region_model_dict
from tests.schemas.utils import region_schema_dict


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(RegionBasePublic, BaseNode)

    assert issubclass(RegionBase, RegionBasePublic)

    assert issubclass(RegionUpdate, RegionBase)
    assert issubclass(RegionUpdate, BaseNodeCreate)

    assert issubclass(RegionReadPublic, BaseNodeRead)
    assert issubclass(RegionReadPublic, BaseReadPublic)
    assert issubclass(RegionReadPublic, RegionBasePublic)
    assert RegionReadPublic.__config__.orm_mode

    assert issubclass(RegionRead, BaseNodeRead)
    assert issubclass(RegionRead, BaseReadPrivate)
    assert issubclass(RegionRead, RegionBase)
    assert RegionRead.__config__.orm_mode

    assert issubclass(RegionCreate, RegionBase)
    assert issubclass(RegionCreate, BaseNodeCreate)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test RegionBasePublic class' attribute values."""
    d = region_schema_dict(attr)
    item = RegionBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("region_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    region_cls: type[RegionBase] | type[RegionCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on RegionBase, PrivateRegionCreate
    and SharedRegionCreate.
    """
    d = region_schema_dict(attr)
    item = region_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test RegionUpdate class' attribute values."""
    d = region_schema_dict(attr)
    item = RegionUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test RegionReadPublic class' attribute values."""
    d = region_schema_dict(attr, read=True)
    item = RegionReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test RegionRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = region_schema_dict(attr, read=True)
    item = RegionRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("region_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(region_cls: type[Region], attr: str) -> None:
    """Use the from_orm function of RegionReadPublic to read data from ORM."""
    model = region_cls(**region_model_dict(attr)).save()
    item = RegionReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("region_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(region_cls: type[Region], attr: str) -> None:
    """Use the from_orm function of RegionRead to read data from an ORM."""
    model = region_cls(**region_model_dict(attr)).save()
    item = RegionRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for RegionBasePublic."""
    with pytest.raises(ValueError):
        RegionBasePublic(**region_schema_dict(attr, valid=False))


@parametrize_with_cases("region_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    region_cls: type[RegionBase] | type[RegionCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to RegionBase, PrivateRegionCreate and
    SharedRegionCreate.
    """
    with pytest.raises(ValueError):
        region_cls(**region_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for RegionUpdate."""
    with pytest.raises(ValueError):
        RegionUpdate(**region_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for RegionReadPublic."""
    with pytest.raises(ValueError):
        RegionReadPublic(**region_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for RegionRead."""
    with pytest.raises(ValueError):
        RegionRead(**region_schema_dict(attr, valid=False, read=True))
