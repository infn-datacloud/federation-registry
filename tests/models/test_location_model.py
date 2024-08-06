import pytest
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize_with_cases

from fed_reg.location.models import Location
from fed_reg.region.models import Region
from tests.models.utils import location_model_dict, region_model_dict


@parametrize_with_cases("attr", has_tag="attr")
def test_location_attr(attr: str) -> None:
    """Test attribute values (default and set)."""
    d = location_model_dict(attr)
    item = Location(**d)
    assert isinstance(item, Location)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.site == d.get("site")
    assert item.country == d.get("country")
    assert item.latitude is d.get("latitude", None)
    assert item.longitude is d.get("longitude", None)

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_location_missing_mandatory_attr(attr: str) -> None:
    """Test IdentityProvider required attributes.

    Creating a model without required values raises a RequiredProperty error.
    """
    err_msg = f"property '{attr}' on objects of class {Location.__name__}"
    d = location_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        Location(**d).save()


def test_rel_def(location_model: Location) -> None:
    """Test relationships definition."""
    assert isinstance(location_model.regions, RelationshipManager)
    assert location_model.regions.name
    assert location_model.regions.source
    assert isinstance(location_model.regions.source, Location)
    assert location_model.regions.source.uid == location_model.uid
    assert location_model.regions.definition
    assert location_model.regions.definition["node_class"] == Region


def test_required_rel(location_model: Location) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        location_model.regions.all()
    with pytest.raises(CardinalityViolation):
        location_model.regions.single()


def test_single_linked_region(location_model: Location, region_model: Region) -> None:
    """Verify `regions` relationship works correctly.

    Connect a single Region to a Location.
    """
    r = location_model.regions.connect(region_model)
    assert r is True

    assert len(location_model.regions.all()) == 1
    region = location_model.regions.single()
    assert isinstance(region, Region)
    assert region.uid == region_model.uid


def test_multiple_linked_regions(location_model: Location) -> None:
    """Verify `regions` relationship works correctly.

    Connect a multiple Region to a Location.
    """
    item = Region(**region_model_dict()).save()
    location_model.regions.connect(item)
    item = Region(**region_model_dict()).save()
    location_model.regions.connect(item)
    assert len(location_model.regions.all()) == 2
