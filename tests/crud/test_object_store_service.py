from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import ObjectStoreServiceCreateExtended
from fedreg.quota.models import ObjectStoreQuota
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import ObjectStoreService
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.service.crud import object_store_service_mng
from tests.utils import random_lower_string, random_service_name, random_url


@pytest.fixture
def region_model() -> Region:
    """ObjectStore service model.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_lower_string()).save()
    region = Region(name=random_lower_string()).save()
    provider.regions.connect(region)
    return region


@pytest.fixture
def object_store_service_model(region_model: Region) -> ObjectStoreService:
    """ObjectStore service model.

    Already connected to a object store service, a region and a provider.
    """
    provider = region_model.provider.single()
    service = ObjectStoreService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.OBJECT_STORE)
    ).save()
    quota = ObjectStoreQuota().save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region_model)
    provider.projects.connect(project)
    region_model.services.connect(service)
    service.quotas.connect(quota)
    quota.project.connect(project)
    return service


class CaseService:
    @case(tags="base")
    def case_object_store_service(self) -> ObjectStoreServiceCreateExtended:
        return ObjectStoreServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.OBJECT_STORE),
        )

    @case(tags="quotas")
    @parametrize(tot_quotas=(1, 2))
    def case_object_store_service_with_quotas(
        self, tot_quotas: int, region_model: Region
    ) -> ObjectStoreServiceCreateExtended:
        provider = region_model.provider.single()
        quotas = []
        for _ in range(tot_quotas):
            project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
            provider.projects.connect(project)
            quotas.append({"project": project.uuid})
        return ObjectStoreServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.OBJECT_STORE),
            quotas=quotas,
        )


@parametrize_with_cases("item", cases=CaseService)
def test_create(item: ObjectStoreServiceCreateExtended, region_model: Region) -> None:
    """Create a new istance"""
    provider = region_model.provider.single()
    projects = provider.projects.all()
    db_obj = object_store_service_mng.create(
        obj_in=item, region=region_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ObjectStoreService)
    assert db_obj.region.is_connected(region_model)
    assert len(db_obj.quotas) == len(item.quotas)


@parametrize_with_cases("item", cases=CaseService)
def test_create_already_exists(
    item: ObjectStoreServiceCreateExtended,
    object_store_service_model: ObjectStoreService,
) -> None:
    """A flavor with the given uuid already exists"""
    item.endpoint = object_store_service_model.endpoint
    region = object_store_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    msg = (
        f"An object store service with endpoint {item.endpoint} "
        f"belonging to provider {provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        object_store_service_mng.create(
            obj_in=item, region=region, provider_projects=projects
        )


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_with_no_provider_projects(
    item: ObjectStoreServiceCreateExtended, region_model: Region
) -> None:
    """No provider_projects param.

    ValueError is raised only when the list of quotas is not empty.
    In fact it is the quota's create operation that raises that error.
    """
    db_obj = object_store_service_mng.create(obj_in=item, region=region_model)
    assert db_obj is not None


@parametrize_with_cases("item", cases=CaseService)
def test_update(
    item: ObjectStoreServiceCreateExtended,
    object_store_service_model: ObjectStoreService,
) -> None:
    """Completely update the service attributes. Also override not set ones.

    Replace existing quotas with new ones. Remove no more used and add new ones.
    """
    region = object_store_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    db_obj = object_store_service_mng.update(
        obj_in=item, db_obj=object_store_service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ObjectStoreService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_no_changes(
    item: ObjectStoreServiceCreateExtended,
    object_store_service_model: ObjectStoreService,
) -> None:
    """The new item is equal to the existing one. No changes."""
    region = object_store_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.endpoint = object_store_service_model.endpoint
    item.name = object_store_service_model.name
    item.quotas = [{"project": projects[0].uuid}]
    db_obj = object_store_service_mng.update(
        obj_in=item, db_obj=object_store_service_model, provider_projects=projects
    )
    assert db_obj is None


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_same_quotas(
    item: ObjectStoreServiceCreateExtended,
    object_store_service_model: ObjectStoreService,
) -> None:
    """Completely update the service attributes. Also override not set ones.

    Keep the same quota but change content.
    """
    region = object_store_service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()
    item.quotas = [{"project": projects[0].uuid}]
    db_obj = object_store_service_mng.update(
        obj_in=item, db_obj=object_store_service_model, provider_projects=projects
    )
    assert db_obj is not None
    assert isinstance(db_obj, ObjectStoreService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
