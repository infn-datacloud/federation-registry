import re
from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import ComputeQuotaCreateExtended
from fedreg.quota.models import ComputeQuota
from fedreg.quota.schemas import ComputeQuotaCreate, ComputeQuotaUpdate
from fedreg.region.models import Region
from fedreg.service.models import ComputeService
from pytest_cases import case, parametrize_with_cases

from fed_reg.quota.crud import compute_quota_mng
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
def compute_quota_model() -> ComputeQuota:
    """Compute quota model.

    Already connected to a block storage service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()
    quota = ComputeQuota().save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    provider.projects.connect(project)
    region.services.connect(service)
    service.quotas.connect(quota)
    quota.project.connect(project)
    return quota


@pytest.fixture
def project_model(compute_quota_model: ComputeQuota) -> Project:
    """Project model.

    Connected to same provider of the existing private quota.
    """
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    service = compute_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return project


class CaseQuota:
    @case(tags="create")
    def case_compute_quota_create(self) -> ComputeQuotaCreate:
        return ComputeQuotaCreate(name=random_lower_string(), uuid=uuid4())

    @case(tags="update")
    def case_compute_update(self) -> ComputeQuotaUpdate:
        return ComputeQuotaUpdate(name=random_lower_string(), uuid=uuid4())

    @case(tags="extended")
    def case_compute_quota_create_extended(
        self, service_model: ComputeService
    ) -> ComputeQuotaCreateExtended:
        region = service_model.region.single()
        provider = region.provider.single()
        project = provider.projects.single()
        return ComputeQuotaCreateExtended(
            name=random_lower_string(), uuid=uuid4(), project=project.uuid
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_create(
    item: ComputeQuotaCreateExtended, service_model: ComputeService
) -> None:
    """Create a new istance"""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = compute_quota_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ComputeQuota)
    assert db_obj.service.is_connected(service_model)
    assert db_obj.project.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_create_with_invalid_project(
    item: ComputeQuotaCreateExtended,
    compute_quota_model: ComputeQuota,
) -> None:
    """None of the quota projects belong to the target provider."""
    item.project = uuid4()
    service = compute_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(ValueError, match=re.escape(msg)):
        compute_quota_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_create_with_no_provider_projects(
    item: ComputeQuotaCreateExtended,
    compute_quota_model: ComputeQuota,
) -> None:
    """Empty list passed to the provider_projects param."""
    service = compute_quota_model.service.single()
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        compute_quota_mng.create(
            obj_in=item, service=service, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update(
    item: ComputeQuotaCreateExtended,
    compute_quota_model: ComputeQuota,
    project_model: Project,
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    item.project = project_model.uuid
    service = compute_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = compute_quota_mng.update(
        obj_in=item, db_obj=compute_quota_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ComputeQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_no_changes(
    item: ComputeQuotaCreateExtended, compute_quota_model: ComputeQuota
) -> None:
    """The new item is equal to the existing one. No changes."""
    service = compute_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.project = projects[0].uuid
    db_obj = compute_quota_mng.update(
        obj_in=item, db_obj=compute_quota_model, provider_projects=projects
    )
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_empy_provider_projects_list(
    item: ComputeQuotaCreateExtended, compute_quota_model: ComputeQuota
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        compute_quota_mng.update(
            obj_in=item, db_obj=compute_quota_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_same_projects(
    item: ComputeQuotaCreateExtended, compute_quota_model: ComputeQuota
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = compute_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.description = random_lower_string()
    item.project = projects[0].uuid
    db_obj = compute_quota_mng.update(
        obj_in=item, db_obj=compute_quota_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ComputeQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseQuota, has_tag="extended")
def test_update_invalid_project(
    item: ComputeQuotaCreateExtended, compute_quota_model: ComputeQuota
) -> None:
    """None of the new quota projects belong to the target provider."""
    service = compute_quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        compute_quota_mng.update(
            obj_in=item, db_obj=compute_quota_model, provider_projects=projects
        )
