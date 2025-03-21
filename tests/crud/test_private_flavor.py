import re
from uuid import uuid4

import pytest
from fedreg.flavor.models import PrivateFlavor
from fedreg.flavor.schemas import FlavorUpdate, PrivateFlavorCreate
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import PrivateFlavorCreateExtended
from fedreg.region.models import Region
from fedreg.service.models import ComputeService
from pytest_cases import case, parametrize_with_cases

from fed_reg.flavor.crud import private_flavor_mng
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
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    return service


@pytest.fixture
def private_flavor_model() -> PrivateFlavor:
    """Private flavor service model.

    Already connected to a compute service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=random_lower_string(), name=random_lower_string()
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
def project_model(private_flavor_model: PrivateFlavor) -> Project:
    """Project model.

    Connected to same provider of the existing private flavor.
    """
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return project


class CaseFlavor:
    @case(tags="create")
    def case_private_flavor_create(self) -> PrivateFlavorCreate:
        return PrivateFlavorCreate(name=random_lower_string(), uuid=uuid4())

    @case(tags="update")
    def case_flavor_update(self) -> FlavorUpdate:
        return FlavorUpdate(name=random_lower_string(), uuid=uuid4())

    @case(tags="extended")
    def case_private_flavor_create_extended(
        self, service_model: ComputeService
    ) -> PrivateFlavorCreateExtended:
        region = service_model.region.single()
        provider = region.provider.single()
        project = provider.projects.single()
        return PrivateFlavorCreateExtended(
            name=random_lower_string(), uuid=uuid4(), projects=[project.uuid]
        )


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
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


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_create_same_uuid_diff_provider(
    item: PrivateFlavorCreateExtended,
    service_model: ComputeService,
    private_flavor_model: PrivateFlavor,
) -> None:
    """A flavor with the given uuid already exists but on a different provider."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.uuid = private_flavor_model.uuid
    db_obj = private_flavor_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    assert db_obj.services.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_create_already_exists(
    item: PrivateFlavorCreate,
    private_flavor_model: PrivateFlavor,
) -> None:
    """A flavor with the given uuid already exists"""
    item.uuid = private_flavor_model.uuid
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"A private flavor with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        private_flavor_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_create_with_invalid_projects(
    item: PrivateFlavorCreateExtended,
    private_flavor_model: PrivateFlavor,
) -> None:
    """None of the flavor projects belong to the target provider."""
    item.projects = [uuid4()]
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"None of the input projects {[i for i in item.projects]} in the "
        f"provider projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        private_flavor_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_create_with_no_provider_projects(
    item: PrivateFlavorCreateExtended,
    private_flavor_model: PrivateFlavor,
) -> None:
    """Empty list passed to the provider_projects param."""
    service = private_flavor_model.services.single()
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.create(obj_in=item, service=service, provider_projects=[])


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_update(
    item: PrivateFlavorCreateExtended,
    private_flavor_model: PrivateFlavor,
    project_model: Project,
) -> None:
    """Completely update the flavor attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    item.projects = [project_model.uuid]
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=private_flavor_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_update_no_changes(
    item: PrivateFlavorCreateExtended, private_flavor_model: PrivateFlavor
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.uuid = private_flavor_model.uuid
    item.name = private_flavor_model.name
    item.projects = [i.uuid for i in projects]
    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=private_flavor_model, provider_projects=projects
    )
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_update_empy_provider_projects_list(
    item: PrivateFlavorCreateExtended, private_flavor_model: PrivateFlavor
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.update(
            obj_in=item, db_obj=private_flavor_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_update_same_projects(
    item: PrivateFlavorCreateExtended, private_flavor_model: PrivateFlavor
) -> None:
    """Completely update the flavor attributes. Also override not set ones.

    Keep the same projects but change content..
    """
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.projects = [i.uuid for i in projects]
    db_obj = private_flavor_mng.update(
        obj_in=item, db_obj=private_flavor_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, PrivateFlavor)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseFlavor, has_tag="extended")
def test_update_invalid_project(
    item: PrivateFlavorCreateExtended, private_flavor_model: PrivateFlavor
) -> None:
    """None of the new flavor projects belong to the target provider."""
    service = private_flavor_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"Input project {item.projects[0]} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_flavor_mng.update(
            obj_in=item, db_obj=private_flavor_model, provider_projects=projects
        )
