from uuid import uuid4

import pytest
from fedreg.flavor.models import SharedFlavor
from fedreg.flavor.schemas import FlavorUpdate, SharedFlavorCreate
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.service.models import ComputeService
from pytest_cases import case, parametrize_with_cases

from fed_reg.flavor.crud import shared_flavor_mng
from tests.utils import random_lower_string


@pytest.fixture
def service_model() -> ComputeService:
    """Compute service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    provider.regions.connect(region)
    region.services.connect(service)
    return service


@pytest.fixture
def shared_flavor_model() -> SharedFlavor:
    """Compute service model.

    Already connected to a compute service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    flavor = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    region.services.connect(service)
    service.flavors.connect(flavor)
    return flavor


class CaseFlavor:
    @case(tags="create")
    def case_shared_flavor_create(self) -> SharedFlavorCreate:
        return SharedFlavorCreate(name=random_lower_string(), uuid=uuid4())

    @case(tags="update")
    def case_flavor_update(self) -> FlavorUpdate:
        return FlavorUpdate(name=random_lower_string(), uuid=uuid4())


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="create")
def test_create(item: SharedFlavorCreate, service_model: ComputeService) -> None:
    """Create a new istance"""
    db_obj = shared_flavor_mng.create(obj_in=item, service=service_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedFlavor)
    assert db_obj.services.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="create")
def test_create_same_uuid_diff_provider(
    item: SharedFlavorCreate,
    service_model: ComputeService,
    shared_flavor_model: SharedFlavor,
) -> None:
    """A flavor with the given uuid already exists but on a different provider."""
    item.uuid = shared_flavor_model.uuid
    db_obj = shared_flavor_mng.create(obj_in=item, service=service_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedFlavor)
    assert db_obj.services.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="create")
def test_create_already_exists(
    item: SharedFlavorCreate,
    shared_flavor_model: SharedFlavor,
) -> None:
    """A flavor with the given uuid already exists"""
    item.uuid = shared_flavor_model.uuid
    service = shared_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    msg = (
        f"A shared flavor with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        shared_flavor_mng.create(obj_in=item, service=service)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="update")
def test_patch(item: FlavorUpdate, shared_flavor_model: SharedFlavor) -> None:
    """Update only a subset of the flavor attributes."""
    db_obj = shared_flavor_mng.patch(obj_in=item, db_obj=shared_flavor_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedFlavor)
    d = item.dict(exclude_unset=True)
    exclude_properties = ["uid", "element_id_property"]
    for k, v in db_obj.__properties__.items():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k, v)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="update")
def test_patch_no_changes(
    item: FlavorUpdate, shared_flavor_model: SharedFlavor
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = shared_flavor_model.uuid
    item.name = shared_flavor_model.name
    db_obj = shared_flavor_mng.patch(obj_in=item, db_obj=shared_flavor_model)
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="create")
def test_update(item: SharedFlavorCreate, shared_flavor_model: SharedFlavor) -> None:
    """Completely update the flavor attributes. Also override not set ones."""
    db_obj = shared_flavor_mng.update(obj_in=item, db_obj=shared_flavor_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedFlavor)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="create")
def test_update_no_changes(
    item: SharedFlavorCreate, shared_flavor_model: SharedFlavor
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = shared_flavor_model.uuid
    item.name = shared_flavor_model.name
    db_obj = shared_flavor_mng.update(obj_in=item, db_obj=shared_flavor_model)
    assert db_obj is None
