from uuid import uuid4

import pytest
from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import NetworkServiceCreateExtended
from fedreg.quota.models import NetworkQuota
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import NetworkService
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.service.crud import network_service_mng
from tests.utils import random_lower_string, random_service_name, random_url


@pytest.fixture
def region_model() -> Region:
    """Network service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    provider.regions.connect(region)
    return region


@pytest.fixture
def network_service_model(region_model: Region) -> NetworkService:
    """Network service model.

    Already connected to a block storage service, a region and a provider.
    """
    provider = region_model.provider.single()
    service = NetworkService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
    ).save()
    quota = NetworkQuota().save()
    shared_network = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
    private_network = PrivateNetwork(
        name=random_lower_string(), uuid=str(uuid4())
    ).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region_model)
    provider.projects.connect(project)
    region_model.services.connect(service)
    service.quotas.connect(quota)
    service.networks.connect(shared_network)
    service.networks.connect(private_network)
    quota.project.connect(project)
    private_network.projects.connect(project)
    return service


class CaseService:
    @case(tags="base")
    def case_network_service(self) -> NetworkServiceCreateExtended:
        return NetworkServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.NETWORK),
        )

    @case(tags="quotas")
    @parametrize(tot_quotas=(1, 2))
    def case_network_service_with_quotas(
        self, tot_quotas: int, region_model: Region
    ) -> NetworkServiceCreateExtended:
        provider = region_model.provider.single()
        quotas = []
        for _ in range(tot_quotas):
            project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
            provider.projects.connect(project)
            quotas.append({"project": project.uuid})
        return NetworkServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.NETWORK),
            quotas=quotas,
        )

    @case(tags="networks")
    def case_network_service_with_private_networks(
        self, region_model: Region
    ) -> NetworkServiceCreateExtended:
        provider = region_model.provider.single()
        networks = []
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        networks.append(
            {"name": random_lower_string(), "uuid": uuid4(), "projects": [project.uuid]}
        )
        networks.append({"name": random_lower_string(), "uuid": uuid4()})
        return NetworkServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.NETWORK),
            networks=networks,
        )


@parametrize_with_cases("item", cases=CaseService)
def test_create(item: NetworkServiceCreateExtended, region_model: Region) -> None:
    """Create a new istance"""
    provider = region_model.provider.single()
    projects = provider.projects.all()
    db_obj = network_service_mng.create(
        obj_in=item, region=region_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, NetworkService)
    assert db_obj.region.is_connected(region_model)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.networks) == len(item.networks)


@parametrize_with_cases("item", cases=CaseService)
def test_create_already_exists(
    item: NetworkServiceCreateExtended,
    network_service_model: NetworkService,
) -> None:
    """A flavor with the given uuid already exists"""
    item.endpoint = network_service_model.endpoint
    region = network_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"A network service with endpoint {item.endpoint} "
        f"belonging to provider {provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        network_service_mng.create(
            obj_in=item, region=region, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_with_no_provider_projects(
    item: NetworkServiceCreateExtended, region_model: Region
) -> None:
    """No provider_projects param.

    ValueError is raised only when the list of quotas is not empty.
    In fact it is the quota's create operation that raises that error.
    """
    db_obj = network_service_mng.create(obj_in=item, region=region_model)
    assert db_obj is not None


@parametrize_with_cases("item", cases=CaseService)
def test_update(
    item: NetworkServiceCreateExtended,
    network_service_model: NetworkService,
) -> None:
    """Completely update the service attributes. Also override not set ones.

    Replace existing quotas with new ones. Remove no more used and add new ones.
    """
    region = network_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = network_service_mng.update(
        obj_in=item, db_obj=network_service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, NetworkService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.networks) == len(item.networks)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_no_changes(
    item: NetworkServiceCreateExtended,
    network_service_model: NetworkService,
) -> None:
    """The new item is equal to the existing one. No changes."""
    region = network_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.endpoint = network_service_model.endpoint
    item.quotas = [{"project": projects[0].uuid}]
    networks = []
    for network in network_service_model.networks:
        d = {"name": network.name, "uuid": network.uuid}
        if not network.is_shared:
            d["projects"] = [x.uuid for x in network.projects]
        networks.append(d)
    item.networks = networks
    db_obj = network_service_mng.update(
        obj_in=item, db_obj=network_service_model, provider_projects=projects
    )
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_service_details(
    item: NetworkServiceCreateExtended,
    network_service_model: NetworkService,
) -> None:
    """Change only item content. Keep same relationships."""
    region = network_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.quotas = [{"project": projects[0].uuid}]
    networks = []
    for network in network_service_model.networks:
        d = {"name": network.name, "uuid": network.uuid}
        if not network.is_shared:
            d["projects"] = [x.uuid for x in network.projects]
        networks.append(d)
    item.networks = networks
    db_obj = network_service_mng.update(
        obj_in=item, db_obj=network_service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, NetworkService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.networks) == len(item.networks)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_same_quotas(
    item: NetworkServiceCreateExtended,
    network_service_model: NetworkService,
) -> None:
    """Change only networks."""
    region = network_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.endpoint = network_service_model.endpoint
    item.quotas = [{"project": projects[0].uuid}]
    db_obj = network_service_mng.update(
        obj_in=item, db_obj=network_service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, NetworkService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.networks) == len(item.networks)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_same_networks(
    item: NetworkServiceCreateExtended,
    network_service_model: NetworkService,
) -> None:
    """Change only quotas."""
    region = network_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.endpoint = network_service_model.endpoint
    networks = []
    for network in network_service_model.networks:
        d = {"name": network.name, "uuid": network.uuid}
        if not network.is_shared:
            d["projects"] = [x.uuid for x in network.projects]
        networks.append(d)
    item.networks = networks

    db_obj = network_service_mng.update(
        obj_in=item, db_obj=network_service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, NetworkService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.networks) == len(item.networks)
