import re
from uuid import uuid4

import pytest
from fedreg.network.models import PrivateNetwork
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import PrivateNetworkCreateExtended
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import NetworkService
from pytest_cases import parametrize_with_cases

from fed_reg.network.crud import private_network_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_network_model() -> PrivateNetwork:
    """Private network model belonging to a different provider.

    Already connected to a network service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = NetworkService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    network = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    service.networks.connect(network)
    network.projects.connect(project)
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
def network_model(service_model: NetworkService) -> PrivateNetwork:
    """Private network model. Already connected to network service."""
    network = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    network.projects.connect(project)

    service_model.networks.connect(network)
    region = service_model.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return network


class CaseNetwork:
    def case_private_network_create_extended(
        self, service_model: NetworkService
    ) -> PrivateNetworkCreateExtended:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = service_model.region.single()
        provider = region.provider.single()
        provider.projects.connect(project)
        return PrivateNetworkCreateExtended(
            name=random_lower_string(), uuid=uuid4(), projects=[project.uuid]
        )


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create(
    item: PrivateNetworkCreateExtended, service_model: NetworkService
) -> None:
    """Create a new istance"""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = private_network_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    assert db_obj.service.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create_same_uuid_diff_provider(
    item: PrivateNetworkCreateExtended,
    service_model: NetworkService,
    stand_alone_network_model: PrivateNetwork,
) -> None:
    """A network with the given uuid already exists but on a different provider."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = stand_alone_network_model.uuid

    db_obj = private_network_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    assert db_obj.service.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create_already_exists(
    item: PrivateNetworkCreateExtended,
    network_model: PrivateNetwork,
) -> None:
    """A network with the given uuid already exists"""
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = network_model.uuid

    msg = (
        f"A private network with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        private_network_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create_with_invalid_projects(
    item: PrivateNetworkCreateExtended,
    network_model: PrivateNetwork,
) -> None:
    """None of the network projects belong to the target provider."""
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.projects = [uuid4()]

    msg = (
        f"None of the input projects {[i for i in item.projects]} in the "
        f"provider projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseNetwork)
def test_create_with_no_provider_projects(
    item: PrivateNetworkCreateExtended, service_model: NetworkService
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.create(
            obj_in=item, service=service_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseNetwork)
def test_update(
    item: PrivateNetworkCreateExtended,
    network_model: PrivateNetwork,
) -> None:
    """Completely update the network attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = private_network_mng.update(
        obj_in=item, db_obj=network_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseNetwork)
def test_update_no_changes(
    item: PrivateNetworkCreateExtended, network_model: PrivateNetwork
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = network_model.uuid
    item.name = network_model.name
    item.projects = [i.uuid for i in network_model.projects]

    db_obj = private_network_mng.update(
        obj_in=item, db_obj=network_model, provider_projects=projects
    )

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseNetwork)
def test_update_only_content(
    item: PrivateNetworkCreateExtended, network_model: PrivateNetwork
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.projects = [i.uuid for i in network_model.projects]

    db_obj = private_network_mng.update(
        obj_in=item, db_obj=network_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseNetwork)
def test_update_only_projects(
    item: PrivateNetworkCreateExtended, network_model: PrivateNetwork
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = network_model.uuid
    item.name = network_model.name

    db_obj = private_network_mng.update(
        obj_in=item, db_obj=network_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseNetwork)
def test_update_empy_provider_projects_list(
    item: PrivateNetworkCreateExtended, network_model: PrivateNetwork
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.update(
            obj_in=item, db_obj=network_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseNetwork)
def test_update_invalid_project(
    item: PrivateNetworkCreateExtended,
    network_model: PrivateNetwork,
    stand_alone_project_model: Project,
) -> None:
    """None of the new network projects belong to the target provider."""
    msg = (
        f"Input project {item.projects[0]} not in the provider "
        f"projects: {[stand_alone_project_model.uuid]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.update(
            obj_in=item,
            db_obj=network_model,
            provider_projects=[stand_alone_project_model],
        )
