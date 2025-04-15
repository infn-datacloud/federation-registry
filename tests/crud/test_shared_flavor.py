from uuid import uuid4

import pytest
from fedreg.flavor.models import SharedFlavor
from fedreg.flavor.schemas import SharedFlavorCreate
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import ComputeService
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.crud import shared_flavor_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_flavor_model() -> SharedFlavor:
    """Shared flavor model belonging to a different provider.

    Already connected to a compute service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    flavor = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    region.services.connect(service)
    service.flavors.connect(flavor)
    return flavor


@pytest.fixture
def service_model() -> ComputeService:
    """Compute service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    provider.regions.connect(region)
    region.services.connect(service)
    return service


@pytest.fixture
def flavor_model(service_model: ComputeService) -> SharedFlavor:
    """Shared flavor model.

    Already connected to a compute service, a region and a provider.
    """
    flavor = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    service_model.flavors.connect(flavor)
    return flavor


class CaseFlavor:
    def case_shared_flavor_create(self) -> SharedFlavorCreate:
        return SharedFlavorCreate(name=random_lower_string(), uuid=uuid4())


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create(item: SharedFlavorCreate, service_model: ComputeService) -> None:
    """Create a new istance"""
    db_obj = shared_flavor_mng.create(obj_in=item, service=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedFlavor)
    assert db_obj.service.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create_same_uuid_diff_provider(
    item: SharedFlavorCreate,
    service_model: ComputeService,
    stand_alone_flavor_model: SharedFlavor,
) -> None:
    """A flavor with the given uuid already exists but on a different provider."""
    item.uuid = stand_alone_flavor_model.uuid

    db_obj = shared_flavor_mng.create(obj_in=item, service=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedFlavor)
    assert db_obj.service.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create_already_exists(
    item: SharedFlavorCreate,
    flavor_model: SharedFlavor,
) -> None:
    """A flavor with the given uuid already exists"""
    service = flavor_model.service.single()

    item.uuid = flavor_model.uuid

    msg = (
        f"A shared flavor with uuid {item.uuid} belonging to service "
        f"{service.endpoint} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        shared_flavor_mng.create(obj_in=item, service=service)
