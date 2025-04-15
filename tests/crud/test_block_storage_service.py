from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import BlockStorageServiceCreateExtended
from fedreg.quota.models import BlockStorageQuota
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import BlockStorageService
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.service.crud import block_storage_service_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_service_model() -> BlockStorageService:
    """BlockStorage service model belonging to a different provider.

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
def region_model() -> Region:
    """Region model. Already connected to a provider."""
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    provider.regions.connect(region)
    return region


@pytest.fixture
def service_model(region_model: Region) -> BlockStorageService:
    """BlockStorage service model.

    Already connected to a region and a provider. It already has one quota.
    """
    provider = region_model.provider.single()
    service = BlockStorageService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.BLOCK_STORAGE)
    ).save()
    quota = BlockStorageQuota().save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region_model)
    provider.projects.connect(project)
    region_model.services.connect(service)
    service.quotas.connect(quota)
    quota.project.connect(project)
    return service


class CaseService:
    @case(tags="base")
    def case_block_storage_service(self) -> BlockStorageServiceCreateExtended:
        return BlockStorageServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        )

    @case(tags="quotas")
    @parametrize(tot_quotas=(1, 2))
    def case_block_storage_service_with_quotas(
        self, tot_quotas: int, region_model: Region
    ) -> BlockStorageServiceCreateExtended:
        provider = region_model.provider.single()
        quotas = []
        for _ in range(tot_quotas):
            project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
            provider.projects.connect(project)
            quotas.append({"project": project.uuid})
        return BlockStorageServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
            quotas=quotas,
        )


@parametrize_with_cases("item", cases=CaseService)
def test_create(item: BlockStorageServiceCreateExtended, region_model: Region) -> None:
    """Create a new istance"""
    provider = region_model.provider.single()
    projects = provider.projects.all()

    db_obj = block_storage_service_mng.create(
        obj_in=item, region=region_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageService)
    assert db_obj.region.is_connected(region_model)
    assert len(db_obj.quotas) == len(item.quotas)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_with_no_provider_projects(
    item: BlockStorageServiceCreateExtended, region_model: Region
) -> None:
    """No provider_projects param is needed when items not requesting it are defined."""
    db_obj = block_storage_service_mng.create(obj_in=item, region=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageService)
    assert db_obj.region.is_connected(region_model)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_same_uuid_diff_provider(
    item: BlockStorageServiceCreateExtended,
    region_model: Region,
    stand_alone_service_model: BlockStorageService,
) -> None:
    """A block storage service with the given endpoint exists on another provider."""
    item.endpoint = stand_alone_service_model.endpoint

    db_obj = block_storage_service_mng.create(obj_in=item, region=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageService)
    assert db_obj.region.is_connected(region_model)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_already_exists(
    item: BlockStorageServiceCreateExtended,
    service_model: BlockStorageService,
) -> None:
    """A block_storage service with the given uuid already exists"""
    region = service_model.region.single()
    provider = region.provider.single()

    item.endpoint = service_model.endpoint

    msg = (
        f"A block storage service with endpoint {item.endpoint} "
        f"belonging to provider {provider.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        block_storage_service_mng.create(obj_in=item, region=region)


@parametrize_with_cases("item", cases=CaseService)
def test_update(
    item: BlockStorageServiceCreateExtended,
    service_model: BlockStorageService,
) -> None:
    """Completely update the service attributes. Also override not set ones.

    Replace existing quotas with new ones. Remove no more used and add new ones.
    """
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = block_storage_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_no_changes(
    item: BlockStorageServiceCreateExtended,
    service_model: BlockStorageService,
) -> None:
    """The new item is equal to the existing one. No changes."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.endpoint = service_model.endpoint
    item.name = service_model.name
    quotas = []
    for quota in service_model.quotas:
        d = {"project": quota.project.single().uuid}
        quotas.append(d)
    item.quotas = quotas

    db_obj = block_storage_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_service_details(
    item: BlockStorageServiceCreateExtended,
    service_model: BlockStorageService,
) -> None:
    """Change only item content. Keep same relationships."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    quotas = []
    for quota in service_model.quotas:
        d = {"project": quota.project.single().uuid}
        quotas.append(d)
    item.quotas = quotas

    db_obj = block_storage_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_quotas(
    item: BlockStorageServiceCreateExtended,
    service_model: BlockStorageService,
) -> None:
    """Change only quotas."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.endpoint = service_model.endpoint
    item.name = service_model.name

    db_obj = block_storage_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, BlockStorageService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
