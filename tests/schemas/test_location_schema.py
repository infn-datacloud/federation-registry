from typing import Any
from uuid import uuid4

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.location.models import Location
from fed_reg.location.schemas import (
    LocationBase,
    LocationBasePublic,
    LocationCreate,
    LocationRead,
    LocationReadPublic,
    LocationUpdate,
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
    assert issubclass(LocationBasePublic, BaseNode)

    assert issubclass(LocationBase, LocationBasePublic)

    assert issubclass(LocationUpdate, LocationBase)
    assert issubclass(LocationUpdate, BaseNodeCreate)

    assert issubclass(LocationReadPublic, BaseNodeRead)
    assert issubclass(LocationReadPublic, BaseReadPublic)
    assert issubclass(LocationReadPublic, LocationBasePublic)
    assert LocationReadPublic.__config__.orm_mode

    assert issubclass(LocationRead, BaseNodeRead)
    assert issubclass(LocationRead, BaseReadPrivate)
    assert issubclass(LocationRead, LocationBase)
    assert LocationRead.__config__.orm_mode

    assert issubclass(LocationCreate, LocationBase)
    assert issubclass(LocationCreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test LocationBasePublic class' attribute values."""
    item = LocationBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.site == data.get("site")
    assert item.country == data.get("country")


@parametrize_with_cases("location_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    location_cls: type[LocationBase] | type[LocationCreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on LocationBase, PrivateLocationCreate
    and SharedLocationCreate.
    """
    item = location_cls(**data)
    assert item.description == data.get("description", "")
    assert item.site == data.get("site")
    assert item.country == data.get("country")
    assert item.latitude == data.get("latitude", None)
    assert item.longitude == data.get("longitude", None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test LocationUpdate class' attribute values."""
    item = LocationUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.site == data.get("site", None)
    assert item.country == data.get("country", None)
    assert item.latitude == data.get("latitude", None)
    assert item.longitude == data.get("longitude", None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test LocationReadPublic class' attribute values."""
    uid = uuid4()
    item = LocationReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.site == data.get("site")
    assert item.country == data.get("country")


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test LocationRead class' attribute values."""
    uid = uuid4()
    item = LocationRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.site == data.get("site")
    assert item.country == data.get("country")
    assert item.latitude == data.get("latitude", None)
    assert item.longitude == data.get("longitude", None)


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Location) -> None:
    """Use the from_orm function of LocationReadPublic to read data from ORM."""
    item = LocationReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.site == model.site
    assert item.country == model.country


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Location) -> None:
    """Use the from_orm function of LocationRead to read data from an ORM."""
    item = LocationRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.site == model.site
    assert item.country == model.country
    assert item.latitude == model.latitude
    assert item.longitude == model.longitude


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for LocationBasePublic."""
    err_msg = rf"1 validation error for LocationBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        LocationBasePublic(**data)


@parametrize_with_cases("location_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    location_cls: type[LocationBase] | type[LocationCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to LocationBase, PrivateLocationCreate and
    SharedLocationCreate.
    """
    err_msg = rf"1 validation error for {location_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        location_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for LocationUpdate."""
    err_msg = rf"1 validation error for LocationUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        LocationUpdate(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for LocationReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for LocationReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        LocationReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for LocationRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for LocationRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        LocationRead(**data, uid=uid)
