import re
from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import BlockStorageQuotaCreateExtended
from fedreg.quota.models import BlockStorageQuota
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import BlockStorageService
from pytest_cases import parametrize_with_cases

from fed_reg.quota.crud import block_storage_quota_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def service_model() -> BlockStorageService:
    """BlockStorage service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = BlockStorageService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.BLOCK_STORAGE)
    ).save()
    provider.regions.connect(region)
    region.services.connect(service)
    return service


@pytest.fixture
def quota_model(service_model: BlockStorageService) -> BlockStorageQuota:
    """BlockStorage quota model.

    Already connected to the same block storage service.
    Create a project. The quota will point to that project.
    """
    quota = BlockStorageQuota().save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    quota.project.connect(project)

    service_model.quotas.connect(quota)
    region = service_model.region.single()
    provider = region.provider.single()
    provider.projects.connect(project)
    return quota


class CaseQuota:
    def case_quota_create_extended(
        self, service_model: BlockStorageService
    ) -> BlockStorageQuotaCreateExtended:
        """Return the block storage quota.

        Create a project belonging to the service's provider.
        The quota will point to that project.
        """
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = service_model.region.single()
        provider = region.provider.single()
        provider.projects.connect(project)
        return BlockStorageQuotaCreateExtended(
            name=random_lower_string(), uuid=uuid4(), project=project.uuid
        )


@parametrize_with_cases("item", cases=CaseQuota)
def test_create(
    item: BlockStorageQuotaCreateExtended, service_model: BlockStorageService
) -> None:
    """Create a new istance"""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = block_storage_quota_mng.create(
        obj_in=item, service=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageQuota)
    assert db_obj.service.is_connected(service_model)
    assert db_obj.project.is_connected(projects[0])


@parametrize_with_cases("item", cases=CaseQuota)
def test_create_duplicate(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """Empty list passed to the provider_projects param."""
    service = quota_model.service.single()
    projects = [quota_model.project.single()]

    item.usage = quota_model.usage
    item.per_user = quota_model.per_user
    item.project = quota_model.project.single().uuid

    msg = (
        f"Target project {item.project} already has a quota with usage="
        f"{item.usage} and per_user={item.per_user} on service "
        f"{service.endpoint}"
    )
    with pytest.raises(AssertionError, match=msg):
        block_storage_quota_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseQuota)
def test_create_with_invalid_project(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """None of the quota projects belong to the target provider."""
    service = quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.project = uuid4()

    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        block_storage_quota_mng.create(
            obj_in=item, service=service, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseQuota)
def test_create_with_no_provider_projects(
    item: BlockStorageQuotaCreateExtended, service_model: BlockStorageService
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        block_storage_quota_mng.create(
            obj_in=item, service=service_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseQuota)
def test_update(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Replace existing projects with new ones. Remove no more used and add new ones.
    """
    service = quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.description = random_lower_string()

    db_obj = block_storage_quota_mng.update(
        obj_in=item, db_obj=quota_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.project.single().uuid == item.project


@parametrize_with_cases("item", cases=CaseQuota)
def test_update_no_changes(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """The new item is equal to the existing one. Also its relationships. No changes."""
    service = quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.project = quota_model.project.single().uuid

    db_obj = block_storage_quota_mng.update(
        obj_in=item, db_obj=quota_model, provider_projects=projects
    )

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseQuota)
def test_update_only_content(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.description = random_lower_string()
    item.project = quota_model.project.single().uuid

    db_obj = block_storage_quota_mng.update(
        obj_in=item, db_obj=quota_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.project.single().uuid == item.project


@parametrize_with_cases("item", cases=CaseQuota)
def test_update_only_projects(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """Completely update the quota attributes. Also override not set ones.

    Keep the same project but change content.
    """
    service = quota_model.service.single()
    region = service.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = block_storage_quota_mng.update(
        obj_in=item, db_obj=quota_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageQuota)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.project.single().uuid == item.project


@parametrize_with_cases("item", cases=CaseQuota)
def test_update_empy_provider_projects_list(
    item: BlockStorageQuotaCreateExtended, quota_model: BlockStorageQuota
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        block_storage_quota_mng.update(
            obj_in=item, db_obj=quota_model, provider_projects=[]
        )


@parametrize_with_cases("item", cases=CaseQuota)
def test_update_invalid_project(
    item: BlockStorageQuotaCreateExtended,
    quota_model: BlockStorageQuota,
    stand_alone_project_model: Project,
) -> None:
    """None of the new quota projects belong to the target provider's ones."""
    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[stand_alone_project_model.uuid]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        block_storage_quota_mng.update(
            obj_in=item,
            db_obj=quota_model,
            provider_projects=[stand_alone_project_model],
        )
