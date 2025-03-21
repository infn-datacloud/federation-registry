import re
from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import ObjectStoreQuotaCreateExtended
from fedreg.quota.models import ObjectStoreQuota
from fedreg.quota.schemas import ObjectStoreQuotaCreate, ObjectStoreQuotaUpdate
from fedreg.region.models import Region
from fedreg.service.models import ObjectStoreService
from pytest_cases import case, parametrize_with_cases

from fed_reg.quota.crud import object_store_quota_mng
from tests.utils import random_lower_string


@pytest.fixture
def service_model() -> ObjectStoreService:
    """ObjectStore service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = ObjectStoreService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    return service


@pytest.fixture
def object_store_quota_model() -> ObjectStoreQuota:
    """ObjectStore quota model.

    Already connected to a block storage service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = ObjectStoreService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    quota = ObjectStoreQuota().save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    service.quotas.connect(quota)
    quota.project.connect(project)
    return quota


@pytest.fixture
def project_model(object_store_quota_model: ObjectStoreQuota) -> Project:
    """Project model.

    Connected to same provider of the existing private quota.
    """
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    service = object_store_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return project


class CaseQuota:
    @case(tags="create")
    def case_object_store_quota_create(self) -> ObjectStoreQuotaCreate:
        return ObjectStoreQuotaCreate(name=random_lower_string(), uuid=uuid4())

    @case(tags="update")
    def case_object_store_update(self) -> ObjectStoreQuotaUpdate:
        return ObjectStoreQuotaUpdate(name=random_lower_string(), uuid=uuid4())

    @case(tags="extended")
    def case_object_store_quota_create_extended(
        self, service_model: ObjectStoreService
    ) -> ObjectStoreQuotaCreateExtended:
        region = service_model.region.single()
        provider = region.provider.single()
        project = provider.projects.single()
        return ObjectStoreQuotaCreateExtended(
            name=random_lower_string(), uuid=uuid4(), project=project.uuid
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_create(
    item: ObjectStoreQuotaCreateExtended, service_model: ObjectStoreService
) -> None:
    """Create a new istance"""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = object_store_quota_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ObjectStoreQuota)
    assert db_obj.service.is_connected(service_model)
    assert db_obj.project.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_create_with_invalid_project(
    item: ObjectStoreQuotaCreateExtended,
    object_store_quota_model: ObjectStoreQuota,
) -> None:
    """None of the quota projects belong to the target provider."""
    item.project = uuid4()
    service = object_store_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        object_store_quota_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_create_with_no_provider_projects(
    item: ObjectStoreQuotaCreateExtended,
    object_store_quota_model: ObjectStoreQuota,
) -> None:
    """Empty list passed to the provider_projects param."""
    service = object_store_quota_model.service.single()
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        object_store_quota_mng.create(
            obj_in=item, service=service, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update(
    item: ObjectStoreQuotaCreateExtended,
    object_store_quota_model: ObjectStoreQuota,
    project_model: Project,
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    item.project = project_model.uuid
    service = object_store_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = object_store_quota_mng.update(
        obj_in=item, db_obj=object_store_quota_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ObjectStoreQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_no_changes(
    item: ObjectStoreQuotaCreateExtended, object_store_quota_model: ObjectStoreQuota
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = object_store_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.project = projects[0].uuid
    db_obj = object_store_quota_mng.update(
        obj_in=item, db_obj=object_store_quota_model, provider_projects=projects
    )
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_empy_provider_projects_list(
    item: ObjectStoreQuotaCreateExtended, object_store_quota_model: ObjectStoreQuota
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        object_store_quota_mng.update(
            obj_in=item, db_obj=object_store_quota_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_same_projects(
    item: ObjectStoreQuotaCreateExtended, object_store_quota_model: ObjectStoreQuota
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = object_store_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.description = random_lower_string()
    item.project = projects[0].uuid
    db_obj = object_store_quota_mng.update(
        obj_in=item, db_obj=object_store_quota_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ObjectStoreQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_invalid_project(
    item: ObjectStoreQuotaCreateExtended, object_store_quota_model: ObjectStoreQuota
) -> None:
    """None of the new quota projects belong to the target provider."""
    service = object_store_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        object_store_quota_mng.update(
            obj_in=item, db_obj=object_store_quota_model, provider_projects=projects
        )
