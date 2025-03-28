import pytest
from fedreg.location.models import Location
from fedreg.location.schemas import LocationCreate
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from pytest_cases import parametrize_with_cases

from fed_reg.location.crud import location_mgr
from tests.utils import random_country, random_lower_string, random_provider_type


@pytest.fixture
def region_model() -> Region:
    """Region model. Already connected to a provider."""
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    provider.regions.connect(region)
    return region


@pytest.fixture
def location_model(region_model: Region) -> Location:
    """Location model belonging to region."""
    location = Location(site=random_lower_string(), country=random_country()).save()
    region_model.location.connect(location)
    return location


class CaseLocation:
    def case_location_create(self) -> LocationCreate:
        return LocationCreate(site=random_lower_string(), country=random_country())


@parametrize_with_cases("item", cases=CaseLocation)
def test_create(item: LocationCreate) -> None:
    """Create a new instance."""
    db_obj = location_mgr.create(obj_in=item)

    assert db_obj is not None
    assert isinstance(db_obj, Location)


@parametrize_with_cases("item", cases=CaseLocation)
def test_create_with_region(item: LocationCreate, region_model: Region) -> None:
    """Create a new istance and connect it to a region."""
    db_obj = location_mgr.create(obj_in=item, region=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Location)
    assert db_obj.regions.is_connected(region_model)


@parametrize_with_cases("item", cases=CaseLocation)
def test_create_replace_region_connection(
    item: LocationCreate, location_model: Location
) -> None:
    """Replace the previous location linked to the target region."""
    region = location_model.regions.single()

    db_obj = location_mgr.create(obj_in=item, region=region)

    assert db_obj is not None
    assert isinstance(db_obj, Location)
    assert db_obj.regions.is_connected(region)


@parametrize_with_cases("item", cases=CaseLocation)
def test_create_already_exists(
    item: LocationCreate,
    location_model: Location,
) -> None:
    """A location with the given site name already exists"""
    item.site = location_model.site

    msg = f"A location with site name {item.site} already exists"
    with pytest.raises(AssertionError, match=msg):
        location_mgr.create(obj_in=item)


@parametrize_with_cases("item", cases=CaseLocation)
def test_update(item: LocationCreate, location_model: Location) -> None:
    """Completely update the location attributes. Also override not set ones."""
    db_obj = location_mgr.update(obj_in=item, db_obj=location_model)

    assert db_obj is not None
    assert isinstance(db_obj, Location)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseLocation)
def test_update_no_changes(item: LocationCreate, location_model: Location) -> None:
    """The new item is equal to the existing one. No changes."""
    item.site = location_model.site
    item.country = location_model.country

    db_obj = location_mgr.update(obj_in=item, db_obj=location_model)

    assert db_obj is None
