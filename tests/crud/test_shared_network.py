from uuid import uuid4

import pytest
from fedreg.network.models import SharedNetwork
from fedreg.network.schemas import SharedNetworkCreate
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import NetworkService
from pytest_cases import parametrize_with_cases

from fed_reg.network.crud import shared_network_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_network_model() -> SharedNetwork:
    """Shared network model belonging to a different provider.

    Already connected to a network service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = NetworkService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    network = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    region.services.connect(service)
    service.networks.connect(network)
    return network


@pytest.fixture
def service_model() -> NetworkService:
    """Network service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = NetworkService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    provider.regions.connect(region)
    region.services.connect(service)
    return service


@pytest.fixture
def network_model(service_model: NetworkService) -> SharedNetwork:
    """Shared network model.

    Already connected to a network service, a region and a provider.
    """
    network = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
    service_model.networks.connect(network)
    return network


class CaseNetwork:
    def case_shared_network_create(self) -> SharedNetworkCreate:
        return SharedNetworkCreate(name=random_lower_string(), uuid=uuid4())


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create(item: SharedNetworkCreate, service_model: NetworkService) -> None:
    """Create a new istance"""
    db_obj = shared_network_mng.create(obj_in=item, service=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedNetwork)
    assert db_obj.service.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create_same_uuid_diff_provider(
    item: SharedNetworkCreate,
    service_model: NetworkService,
    stand_alone_network_model: SharedNetwork,
) -> None:
    """A network with the given uuid already exists but on a different provider."""
    item.uuid = stand_alone_network_model.uuid

    db_obj = shared_network_mng.create(obj_in=item, service=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedNetwork)
    assert db_obj.service.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create_already_exists(
    item: SharedNetworkCreate,
    network_model: SharedNetwork,
) -> None:
    """A network with the given uuid already exists"""
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()

    item.uuid = network_model.uuid

    msg = (
        f"A shared network with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        shared_network_mng.create(obj_in=item, service=service)
