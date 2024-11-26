from typing import Any

import pytest
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize_with_cases

from fed_reg.location.models import Location
from fed_reg.region.models import Region
from tests.utils import random_lower_string


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_location_valid_attr(data: dict[str, Any]) -> None:
    """Test Location mandatory and optional attributes."""
    item = Location(**data)
    assert isinstance(item, Location)
    assert item.uid is not None
    assert item.description == data.get("description", "")
    assert item.site == data.get("site")
    assert item.country == data.get("country")
    assert item.latitude is data.get("latitude", None)
    assert item.longitude is data.get("longitude", None)

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("data", has_tag=("dict", "invalid"))
def test_location_missing_mandatory_attr(data: dict[str, Any]) -> None:
    """Test Location required attributes.

    Creating a model without required values raises a RequiredProperty error.
    """
    with pytest.raises(RequiredProperty):
        Location(**data).save()


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
    """Test Location required relationships.

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
    item = Region(name=random_lower_string()).save()
    location_model.regions.connect(item)
    item = Region(name=random_lower_string()).save()
    location_model.regions.connect(item)
    assert len(location_model.regions.all()) == 2
