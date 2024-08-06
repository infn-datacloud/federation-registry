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
from tests.models.utils import location_model_dict
from tests.schemas.utils import location_schema_dict


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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test LocationBasePublic class' attribute values."""
    d = location_schema_dict(attr)
    item = LocationBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.site == d.get("site")
    assert item.country == d.get("country")


@parametrize_with_cases("location_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    location_cls: type[LocationBase] | type[LocationCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on LocationBase, PrivateLocationCreate
    and SharedLocationCreate.
    """
    d = location_schema_dict(attr)
    item = location_cls(**d)
    assert item.description == d.get("description", "")
    assert item.site == d.get("site")
    assert item.country == d.get("country")
    assert item.latitude == d.get("latitude", None)
    assert item.longitude == d.get("longitude", None)


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test LocationUpdate class' attribute values."""
    d = location_schema_dict(attr)
    item = LocationUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.site == d.get("site", None)
    assert item.country == d.get("country", None)
    assert item.latitude == d.get("latitude", None)
    assert item.longitude == d.get("longitude", None)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test LocationReadPublic class' attribute values."""
    d = location_schema_dict(attr, read=True)
    item = LocationReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.site == d.get("site")
    assert item.country == d.get("country")


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test LocationRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = location_schema_dict(attr, read=True)
    item = LocationRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.site == d.get("site")
    assert item.country == d.get("country")
    assert item.latitude == d.get("latitude", None)
    assert item.longitude == d.get("longitude", None)


@parametrize_with_cases("location_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(location_cls: type[Location], attr: str) -> None:
    """Use the from_orm function of LocationReadPublic to read data from ORM."""
    model = location_cls(**location_model_dict(attr)).save()
    item = LocationReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.site == model.site
    assert item.country == model.country


@parametrize_with_cases("location_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(location_cls: type[Location], attr: str) -> None:
    """Use the from_orm function of LocationRead to read data from an ORM."""
    model = location_cls(**location_model_dict(attr)).save()
    item = LocationRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.site == model.site
    assert item.country == model.country
    assert item.latitude == model.latitude
    assert item.longitude == model.longitude


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for LocationBasePublic."""
    with pytest.raises(ValueError):
        LocationBasePublic(**location_schema_dict(attr, valid=False))


@parametrize_with_cases("location_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    location_cls: type[LocationBase] | type[LocationCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to LocationBase, PrivateLocationCreate and
    SharedLocationCreate.
    """
    with pytest.raises(ValueError):
        location_cls(**location_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for LocationUpdate."""
    with pytest.raises(ValueError):
        LocationUpdate(**location_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for LocationReadPublic."""
    with pytest.raises(ValueError):
        LocationReadPublic(**location_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for LocationRead."""
    with pytest.raises(ValueError):
        LocationRead(**location_schema_dict(attr, valid=False, read=True))
