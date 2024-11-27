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
from fed_reg.region.models import Region
from fed_reg.region.schemas import (
    RegionBase,
    RegionBasePublic,
    RegionCreate,
    RegionRead,
    RegionReadPublic,
    RegionUpdate,
)


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


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test RegionBasePublic class' attribute values."""
    item = RegionBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("region_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    region_cls: type[RegionBase] | type[RegionCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on RegionBase, PrivateRegionCreate
    and SharedRegionCreate.
    """
    item = region_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test RegionUpdate class' attribute values."""
    item = RegionUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test RegionReadPublic class' attribute values."""
    uid = uuid4()
    item = RegionReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test RegionRead class' attribute values."""
    uid = uuid4()
    item = RegionRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Region) -> None:
    """Use the from_orm function of RegionReadPublic to read data from ORM."""
    item = RegionReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Region) -> None:
    """Use the from_orm function of RegionRead to read data from an ORM."""
    item = RegionRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for RegionBasePublic."""
    err_msg = rf"1 validation error for RegionBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        RegionBasePublic(**data)


@parametrize_with_cases("region_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    region_cls: type[RegionBase] | type[RegionCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to RegionBase, PrivateRegionCreate and
    SharedRegionCreate.
    """
    err_msg = rf"1 validation error for {region_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        region_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for RegionUpdate."""
    err_msg = rf"1 validation error for RegionUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        RegionUpdate(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for RegionReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for RegionReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        RegionReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for RegionRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for RegionRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        RegionRead(**data, uid=uid)
