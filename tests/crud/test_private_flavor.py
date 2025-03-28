import re
from uuid import uuid4

import pytest
from fedreg.flavor.models import PrivateFlavor
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import PrivateFlavorCreateExtended
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import ComputeService
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.crud import private_flavor_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_flavor_model() -> PrivateFlavor:
    """Private flavor model belonging to a different provider.

    Already connected to a compute service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    flavor = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    service.flavors.connect(flavor)
    flavor.projects.connect(project)
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
def flavor_model(service_model: ComputeService) -> PrivateFlavor:
    """Private flavor model. Already connected to compute service."""
    flavor = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    flavor.projects.connect(project)

    service_model.flavors.connect(flavor)
    region = service_model.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return flavor


class CaseFlavor:
    def case_private_flavor_create_extended(
        self, service_model: ComputeService
    ) -> PrivateFlavorCreateExtended:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = service_model.region.single()
        provider = region.provider.single()
        provider.projects.connect(project)
        return PrivateFlavorCreateExtended(
            name=random_lower_string(), uuid=uuid4(), projects=[project.uuid]
        )


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create(
    item: PrivateFlavorCreateExtended, service_model: ComputeService
) -> None:
    """Create a new istance"""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = private_flavor_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    assert db_obj.services.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create_same_uuid_diff_provider(
    item: PrivateFlavorCreateExtended,
    service_model: ComputeService,
    stand_alone_flavor_model: PrivateFlavor,
) -> None:
    """A flavor with the given uuid already exists but on a different provider."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = stand_alone_flavor_model.uuid

    db_obj = private_flavor_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    assert db_obj.services.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create_already_exists(
    item: PrivateFlavorCreateExtended,
    flavor_model: PrivateFlavor,
) -> None:
    """A flavor with the given uuid already exists"""
    service = flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = flavor_model.uuid

    msg = (
        f"A private flavor with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        private_flavor_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create_with_invalid_projects(
    item: PrivateFlavorCreateExtended,
    flavor_model: PrivateFlavor,
) -> None:
    """None of the flavor projects belong to the target provider."""
    service = flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.projects = [uuid4()]

    msg = (
        f"None of the input projects {[i for i in item.projects]} in the "
        f"provider projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseFlavor)
def test_create_with_no_provider_projects(
    item: PrivateFlavorCreateExtended, service_model: ComputeService
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.create(
            obj_in=item, service=service_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseFlavor)
def test_update(
    item: PrivateFlavorCreateExtended,
    flavor_model: PrivateFlavor,
) -> None:
    """Completely update the flavor attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    service = flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=flavor_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseFlavor)
def test_update_no_changes(
    item: PrivateFlavorCreateExtended, flavor_model: PrivateFlavor
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = flavor_model.uuid
    item.name = flavor_model.name
    item.projects = [i.uuid for i in flavor_model.projects]

    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=flavor_model, provider_projects=projects
    )

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseFlavor)
def test_update_only_content(
    item: PrivateFlavorCreateExtended, flavor_model: PrivateFlavor
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.projects = [i.uuid for i in flavor_model.projects]

    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=flavor_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseFlavor)
def test_update_only_projects(
    item: PrivateFlavorCreateExtended, flavor_model: PrivateFlavor
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = flavor_model.uuid
    item.name = flavor_model.name

    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=flavor_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseFlavor)
def test_update_empy_provider_projects_list(
    item: PrivateFlavorCreateExtended, flavor_model: PrivateFlavor
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.update(
            obj_in=item, db_obj=flavor_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseFlavor)
def test_update_invalid_project(
    item: PrivateFlavorCreateExtended,
    flavor_model: PrivateFlavor,
    stand_alone_project_model: Project,
) -> None:
    """None of the new flavor projects belong to the target provider."""
    msg = (
        f"Input project {item.projects[0]} not in the provider "
        f"projects: {[stand_alone_project_model.uuid]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.update(
            obj_in=item,
            db_obj=flavor_model,
            provider_projects=[stand_alone_project_model],
        )
