from typing import Any
from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    DoesNotExist,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize_with_cases

from fed_reg.location.models import Location
from fed_reg.provider.models import Provider
from fed_reg.region.models import Region
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
    Service,
)
from tests.models.utils import (
    location_model_dict,
    provider_model_dict,
    region_model_dict,
)


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_region_attr(data: dict[str, Any]) -> None:
    """Test attribute values (default and set)."""
    item = Region(**data)
    assert isinstance(item, Region)
    assert item.uid is not None
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid"))
def test_region_missing_mandatory_attr(data: dict[str, Any], attr: str) -> None:
    """Test Region required attributes.

    Creating a model without required values raises a RequiredProperty error.
    """
    err_msg = f"property '{attr}' on objects of class {Region.__name__}"
    with pytest.raises(RequiredProperty, match=err_msg):
        Region(**data).save()


def test_rel_def(region_model: Region) -> None:
    """Test relationships definition."""
    assert isinstance(region_model.location, RelationshipManager)
    assert region_model.location.name
    assert region_model.location.source
    assert isinstance(region_model.location.source, Region)
    assert region_model.location.source.uid == region_model.uid
    assert region_model.location.definition
    assert region_model.location.definition["node_class"] == Location

    assert isinstance(region_model.provider, RelationshipManager)
    assert region_model.provider.name
    assert region_model.provider.source
    assert isinstance(region_model.provider.source, Region)
    assert region_model.provider.source.uid == region_model.uid
    assert region_model.provider.definition
    assert region_model.provider.definition["node_class"] == Provider

    assert isinstance(region_model.services, RelationshipManager)
    assert region_model.services.name
    assert region_model.services.source
    assert isinstance(region_model.services.source, Region)
    assert region_model.services.source.uid == region_model.uid
    assert region_model.services.definition
    assert region_model.services.definition["node_class"] == Service


def test_required_rel(region_model: Region) -> None:
    """Test Region required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        region_model.provider.all()
    with pytest.raises(CardinalityViolation):
        region_model.provider.single()


def test_single_linked_provider(region_model: Region, provider_model: Provider) -> None:
    """Verify `provider` relationship works correctly.

    Connect a single Provider to a Region.
    """
    r = region_model.provider.connect(provider_model)
    assert r is True

    assert len(region_model.provider.all()) == 1
    provider = region_model.provider.single()
    assert isinstance(provider, Provider)
    assert provider.uid == provider_model.uid


def test_multiple_linked_provider(region_model: Region) -> None:
    """Verify `provider` relationship works correctly.

    Trying to connect multiple Provider to a Region raises an
    AttemptCardinalityViolation error.
    """
    item = Provider(**provider_model_dict()).save()
    region_model.provider.connect(item)
    item = Provider(**provider_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        region_model.provider.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        region_model.provider.connect(item)
        with pytest.raises(CardinalityViolation):
            region_model.provider.all()


def test_optional_rel(region_model: Region) -> None:
    """Test Region optional relationships."""
    assert len(region_model.location.all()) == 0
    assert region_model.location.single() is None
    assert len(region_model.services.all()) == 0
    assert region_model.services.single() is None


def test_single_linked_location(region_model: Region, location_model: Location) -> None:
    """Verify `location` relationship works correctly.

    Connect a single Location to a Region.
    """
    r = region_model.location.connect(location_model)
    assert r is True

    assert len(region_model.location.all()) == 1
    location = region_model.location.single()
    assert isinstance(location, Location)
    assert location.uid == location_model.uid


def test_multiple_linked_location(region_model: Region) -> None:
    """Verify `location` relationship works correctly.

    Trying to connect multiple Location to a Region raises an
    AttemptCardinalityViolation error.
    """
    item = Location(**location_model_dict()).save()
    region_model.location.connect(item)
    item = Location(**location_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        region_model.location.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        region_model.location.connect(item)
        with pytest.raises(CardinalityViolation):
            region_model.location.all()


@parametrize_with_cases("service_model", has_tag=("service", "single"))
def test_single_linked_service(
    region_model: Region,
    service_model: BlockStorageService
    | ComputeService
    | IdentityService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect a single Quota to a Project.
    Execute this test for these quota types: BlockStorage, Compute, Indentity, Network
    and ObjectStore.
    """
    r = region_model.services.connect(service_model)
    assert r is True

    assert len(region_model.services.all()) == 1
    service = region_model.services.single()
    assert isinstance(service, Service)
    assert service.uid == service_model.uid


@parametrize_with_cases("service_models", has_tag=("service", "multi"))
def test_multiple_linked_services(
    region_model: Region,
    service_models: list[BlockStorageService]
    | list[ComputeService]
    | list[IdentityService]
    | list[NetworkService]
    | list[ObjectStoreService],
) -> None:
    """Verify `services` relationship works correctly.

    Connect multiple Service to a Region.
    Execute this test for these quota types: BlockStorage, Compute, Identity, Network
    and ObjectStore.
    """
    for service_model in service_models:
        region_model.services.connect(service_model)
    assert len(region_model.services.all()) == len(service_models)


@parametrize_with_cases("service_models", has_tag=("service", "multi"))
def test_pre_delete_hook(
    service_models: list[BlockStorageService]
    | list[ComputeService]
    | list[IdentityService]
    | list[NetworkService]
    | list[ObjectStoreService],
    region_model: Region,
) -> None:
    """Delete region and all related services."""
    for item in service_models:
        region_model.services.connect(item)

    assert region_model.delete()
    assert region_model.deleted
    for item in service_models:
        with pytest.raises(DoesNotExist):
            item.refresh()


def test_pre_delete_hook_remove_location(
    region_model: Region, location_model: Location
) -> None:
    """Delete region and related location"""
    region_model.location.connect(location_model)

    assert region_model.delete()
    assert region_model.deleted
    with pytest.raises(DoesNotExist):
        location_model.refresh()


def test_pre_delete_hook_dont_remove_location(location_model: Location) -> None:
    """Location with multiple regions is not deleted when deleting one region."""
    item1 = Region(**region_model_dict()).save()
    location_model.regions.connect(item1)
    item2 = Region(**region_model_dict()).save()
    location_model.regions.connect(item2)

    assert item1.delete()
    assert item1.deleted
    assert location_model.regions.single() == item2
