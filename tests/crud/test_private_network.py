import re
from uuid import uuid4

import pytest
from fedreg.network.models import PrivateNetwork
from fedreg.network.schemas import NetworkUpdate, PrivateNetworkCreate
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import PrivateNetworkCreateExtended
from fedreg.region.models import Region
from fedreg.service.models import NetworkService
from pytest_cases import case, parametrize_with_cases

from fed_reg.network.crud import private_network_mng
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
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    return service


@pytest.fixture
def private_network_model() -> PrivateNetwork:
    """Network service model.

    Already connected to a network service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = NetworkService(
        endpoint=random_lower_string(), name=random_lower_string()
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
def project_model(private_network_model: PrivateNetwork) -> Project:
    """Project model.

    Connected to same provider of the existing private network.
    """
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return project


class CaseNetwork:
    @case(tags="create")
    def case_private_network_create(self) -> PrivateNetworkCreate:
        return PrivateNetworkCreate(name=random_lower_string(), uuid=uuid4())

    @case(tags="update")
    def case_network_update(self) -> NetworkUpdate:
        return NetworkUpdate(name=random_lower_string(), uuid=uuid4())

    @case(tags="extended")
    def case_private_network_create_extended(
        self, service_model: NetworkService
    ) -> PrivateNetworkCreateExtended:
        region = service_model.region.single()
        provider = region.provider.single()
        project = provider.projects.single()
        return PrivateNetworkCreateExtended(
            name=random_lower_string(), uuid=uuid4(), projects=[project.uuid]
        )


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
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


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_create_same_uuid_diff_provider(
    item: PrivateNetworkCreateExtended,
    service_model: NetworkService,
    private_network_model: PrivateNetwork,
) -> None:
    """A network with the given uuid already exists but on a different provider."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.uuid = private_network_model.uuid
    db_obj = private_network_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    assert db_obj.service.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_create_already_exists(
    item: PrivateNetworkCreate,
    private_network_model: PrivateNetwork,
) -> None:
    """A network with the given uuid already exists"""
    item.uuid = private_network_model.uuid
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"A private network with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        private_network_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_create_with_invalid_projects(
    item: PrivateNetworkCreateExtended,
    private_network_model: PrivateNetwork,
) -> None:
    """None of the network projects belong to the target provider."""
    item.projects = [uuid4()]
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"None of the input projects {[i for i in item.projects]} "
        f"belongs to provider {provider.name}"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        private_network_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_create_with_no_provider_projects(
    item: PrivateNetworkCreateExtended,
    private_network_model: PrivateNetwork,
) -> None:
    """Empty list passed to the provider_projects param."""
    item.projects = [uuid4()]
    service = private_network_model.service.single()
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.create(obj_in=item, service=service, provider_projects=[])


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="update")
def test_patch(item: NetworkUpdate, private_network_model: PrivateNetwork) -> None:
    """Update only a subset of the network attributes."""
    db_obj = private_network_mng.patch(obj_in=item, db_obj=private_network_model)
    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    d = item.dict(exclude_unset=True)
    exclude_properties = ["uid", "element_id_property"]
    for k, v in db_obj.__properties__.items():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k, v)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="update")
def test_patch_no_changes(
    item: NetworkUpdate, private_network_model: PrivateNetwork
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = private_network_model.uuid
    item.name = private_network_model.name
    db_obj = private_network_mng.patch(obj_in=item, db_obj=private_network_model)
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_update(
    item: PrivateNetworkCreateExtended,
    private_network_model: PrivateNetwork,
    project_model: Project,
) -> None:
    """Completely update the network attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    item.projects = [project_model.uuid]
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = private_network_mng.update(
        obj_in=item, db_obj=private_network_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_update_no_changes(
    item: PrivateNetworkCreateExtended, private_network_model: PrivateNetwork
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.uuid = private_network_model.uuid
    item.name = private_network_model.name
    item.projects = [i.uuid for i in projects]
    db_obj = private_network_mng.update(
        obj_in=item, db_obj=private_network_model, provider_projects=projects
    )
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_update_empy_provider_projects_list(
    item: PrivateNetworkCreateExtended, private_network_model: PrivateNetwork
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.update(
            obj_in=item, db_obj=private_network_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_update_same_projects(
    item: PrivateNetworkCreateExtended, private_network_model: PrivateNetwork
) -> None:
    """Completely update the network attributes. Also override not set ones.

    Keep the same projects.
    """
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.projects = [i.uuid for i in projects]
    db_obj = private_network_mng.update(
        obj_in=item, db_obj=private_network_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, PrivateNetwork)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseNetwork, has_tag="extended")
def test_update_invalid_project(
    item: PrivateNetworkCreateExtended, private_network_model: PrivateNetwork
) -> None:
    """None of the new network projects belong to the target provider."""
    service = private_network_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = f"Input project {item.projects[0]} not in the provider projects: {projects}"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_network_mng.update(
            obj_in=item, db_obj=private_network_model, provider_projects=projects
        )
