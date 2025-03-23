import re
from uuid import uuid4

import pytest
from fedreg.image.models import PrivateImage
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import PrivateImageCreateExtended
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import ComputeService
from pytest_cases import parametrize_with_cases

from fed_reg.image.crud import private_image_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_project_model() -> Project:
    """Stand alone project model.

    Connected to a different provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.projects.connect(project)
    return project


@pytest.fixture
def stand_alone_image_model() -> PrivateImage:
    """Private image model belonging to a different provider.

    Already connected to a compute service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    image = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    service.images.connect(image)
    image.projects.connect(project)
    return image


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
def image_model(service_model: ComputeService) -> PrivateImage:
    """Private image model. Already connected to compute service."""
    image = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    image.projects.connect(project)

    service_model.images.connect(image)
    region = service_model.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return image


class CaseImage:
    def case_private_image_create_extended(
        self, service_model: ComputeService
    ) -> PrivateImageCreateExtended:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = service_model.region.single()
        provider = region.provider.single()
        provider.projects.connect(project)
        return PrivateImageCreateExtended(
            name=random_lower_string(), uuid=uuid4(), projects=[project.uuid]
        )


@parametrize_with_cases("item", cases=CaseImage)
def test_create(
    item: PrivateImageCreateExtended, service_model: ComputeService
) -> None:
    """Create a new istance"""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = private_image_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateImage)
    assert db_obj.services.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseImage)
def test_create_same_uuid_diff_provider(
    item: PrivateImageCreateExtended,
    service_model: ComputeService,
    stand_alone_image_model: PrivateImage,
) -> None:
    """A image with the given uuid already exists but on a different provider."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = stand_alone_image_model.uuid

    db_obj = private_image_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateImage)
    assert db_obj.services.is_connected(service_model)
    assert db_obj.projects.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseImage)
def test_create_already_exists(
    item: PrivateImageCreateExtended,
    image_model: PrivateImage,
) -> None:
    """A image with the given uuid already exists"""
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = image_model.uuid

    msg = (
        f"A private image with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        private_image_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseImage)
def test_create_with_invalid_projects(
    item: PrivateImageCreateExtended,
    image_model: PrivateImage,
) -> None:
    """None of the image projects belong to the target provider."""
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.projects = [uuid4()]

    msg = (
        f"None of the input projects {[i for i in item.projects]} in the "
        f"provider projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        private_image_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseImage)
def test_create_with_no_provider_projects(
    item: PrivateImageCreateExtended, service_model: ComputeService
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_image_mng.create(
            obj_in=item, service=service_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseImage)
def test_update(
    item: PrivateImageCreateExtended,
    image_model: PrivateImage,
) -> None:
    """Completely update the image attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = private_image_mng.update(
        obj_in=item, db_obj=image_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateImage)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseImage)
def test_update_no_changes(
    item: PrivateImageCreateExtended, image_model: PrivateImage
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = image_model.uuid
    item.name = image_model.name
    item.projects = [i.uuid for i in image_model.projects]

    db_obj = private_image_mng.update(
        obj_in=item, db_obj=image_model, provider_projects=projects
    )

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseImage)
def test_update_only_content(
    item: PrivateImageCreateExtended, image_model: PrivateImage
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.projects = [i.uuid for i in image_model.projects]

    db_obj = private_image_mng.update(
        obj_in=item, db_obj=image_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateImage)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseImage)
def test_update_only_projects(
    item: PrivateImageCreateExtended, image_model: PrivateImage
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.uuid = image_model.uuid
    item.name = image_model.name

    db_obj = private_image_mng.update(
        obj_in=item, db_obj=image_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, PrivateImage)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.projects) == len(item.projects)
    assert set([x.uuid for x in db_obj.projects]) == set(item.projects)


@parametrize_with_cases("item", cases=CaseImage)
def test_update_empy_provider_projects_list(
    item: PrivateImageCreateExtended, image_model: PrivateImage
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_image_mng.update(obj_in=item, db_obj=image_model, provider_projects=[])


@parametrize_with_cases("item", cases=CaseImage)
def test_update_invalid_project(
    item: PrivateImageCreateExtended,
    image_model: PrivateImage,
    stand_alone_project_model: Project,
) -> None:
    """None of the new image projects belong to the target provider."""
    msg = (
        f"Input project {item.projects[0]} not in the provider "
        f"projects: {[stand_alone_project_model.uuid]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        private_image_mng.update(
            obj_in=item,
            db_obj=image_model,
            provider_projects=[stand_alone_project_model],
        )
