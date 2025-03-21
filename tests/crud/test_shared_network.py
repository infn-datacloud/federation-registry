from uuid import uuid4

import pytest
from fedreg.network.models import SharedNetwork
from fedreg.network.schemas import NetworkUpdate, SharedNetworkCreate
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.service.models import NetworkService
from pytest_cases import case, parametrize_with_cases

from fed_reg.network.crud import shared_network_mng
from tests.utils import random_lower_string


@pytest.fixture
def service_model() -> NetworkService:
    """Network service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = NetworkService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    provider.regions.connect(region)
    region.services.connect(service)
    return service


@pytest.fixture
def shared_network_model() -> SharedNetwork:
    """Network service model.

    Already connected to a network service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = NetworkService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    network = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    region.services.connect(service)
    service.networks.connect(network)
    return network


class CaseNetwork:
    @case(tags="create")
    def case_shared_network_create(self) -> SharedNetworkCreate:
        return SharedNetworkCreate(name=random_lower_string(), uuid=uuid4())

    @case(tags="update")
    def case_network_update(self) -> NetworkUpdate:
        return NetworkUpdate(name=random_lower_string(), uuid=uuid4())


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="create")
def test_create(item: SharedNetworkCreate, service_model: NetworkService) -> None:
    """Create a new istance"""
    db_obj = shared_network_mng.create(obj_in=item, service=service_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedNetwork)
    assert db_obj.service.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="create")
def test_create_same_uuid_diff_provider(
    item: SharedNetworkCreate,
    service_model: NetworkService,
    shared_network_model: SharedNetwork,
) -> None:
    """A network with the given uuid already exists but on a different provider."""
    item.uuid = shared_network_model.uuid
    db_obj = shared_network_mng.create(obj_in=item, service=service_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedNetwork)
    assert db_obj.service.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="create")
def test_create_already_exists(
    item: SharedNetworkCreate,
    shared_network_model: SharedNetwork,
) -> None:
    """A network with the given uuid already exists"""
    item.uuid = shared_network_model.uuid
    service = shared_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    msg = (
        f"A shared network with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        shared_network_mng.create(obj_in=item, service=service)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="update")
def test_patch(item: NetworkUpdate, shared_network_model: SharedNetwork) -> None:
    """Update only a subset of the network attributes."""
    db_obj = shared_network_mng.patch(obj_in=item, db_obj=shared_network_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedNetwork)
    d = item.dict(exclude_unset=True)
    exclude_properties = ["uid", "element_id_property"]
    for k, v in db_obj.__properties__.items():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k, v)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="update")
def test_patch_no_changes(
    item: NetworkUpdate, shared_network_model: SharedNetwork
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = shared_network_model.uuid
    item.name = shared_network_model.name
    db_obj = shared_network_mng.patch(obj_in=item, db_obj=shared_network_model)
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="create")
def test_update(item: SharedNetworkCreate, shared_network_model: SharedNetwork) -> None:
    """Completely update the network attributes. Also override not set ones."""
    db_obj = shared_network_mng.update(obj_in=item, db_obj=shared_network_model)
    assert db_obj is not None
    assert isinstance(db_obj, SharedNetwork)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="create")
def test_update_no_changes(
    item: SharedNetworkCreate, shared_network_model: SharedNetwork
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = shared_network_model.uuid
    item.name = shared_network_model.name
    db_obj = shared_network_mng.update(obj_in=item, db_obj=shared_network_model)
    assert db_obj is None
