from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import IdentityService
from fedreg.service.schemas import IdentityServiceCreate
from pytest_cases import parametrize_with_cases

from fed_reg.service.crud import identity_service_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def region_model() -> Region:
    """Region model. Already connected to a provider."""
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    provider.regions.connect(region)
    return region


@pytest.fixture
def another_region_model(region_model: Region) -> Region:
    """Second region model connected to the first's region provider."""
    region = Region(name=random_lower_string()).save()
    provider = region_model.provider.single()
    provider.regions.connect(region)
    return region


@pytest.fixture
def service_model(region_model: Region) -> IdentityService:
    """Identity service model.

    Already connected to a region and a provider. It already has one quota.
    """
    provider = region_model.provider.single()
    service = IdentityService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
    ).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region_model)
    provider.projects.connect(project)
    region_model.services.connect(service)
    return service


class CaseService:
    def case_identity_service(self) -> IdentityServiceCreate:
        return IdentityServiceCreate(
            endpoint=random_url(), name=random_service_name(ServiceType.IDENTITY)
        )


@parametrize_with_cases("item", cases=CaseService)
def test_create(item: IdentityServiceCreate, region_model: Region) -> None:
    """Create a new istance"""
    db_obj = identity_service_mng.create(obj_in=item, region=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, IdentityService)
    assert db_obj.region.is_connected(region_model)


@parametrize_with_cases("item", cases=CaseService)
def test_create_same_endpoint_same_provider_diff_region(
    item: IdentityServiceCreate,
    service_model: IdentityService,
    another_region_model: Region,
) -> None:
    """Identity services with the same endpoint can exist within a provider."""
    item.endpoint = service_model.endpoint

    db_obj = identity_service_mng.create(obj_in=item, region=another_region_model)

    assert db_obj is not None
    assert isinstance(db_obj, IdentityService)
    assert db_obj.region.is_connected(another_region_model)


@parametrize_with_cases("item", cases=CaseService)
def test_create_already_exists(
    item: IdentityServiceCreate, service_model: IdentityService
) -> None:
    """A identity service with the given endpoint already exists in this region."""
    region = service_model.region.single()

    item.endpoint = service_model.endpoint

    msg = (
        f"An identity service with endpoint {item.endpoint} "
        f"belonging to region {region.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        identity_service_mng.create(obj_in=item, region=region)


@parametrize_with_cases("item", cases=CaseService)
def test_update(item: IdentityServiceCreate, service_model: IdentityService) -> None:
    """Completely update the service attributes. Also override not set ones.

    Replace existing quotas with new ones. Remove no more used and add new ones.
    """
    db_obj = identity_service_mng.update(obj_in=item, db_obj=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, IdentityService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseService)
def test_update_no_changes(
    item: IdentityServiceCreate, service_model: IdentityService
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.endpoint = service_model.endpoint
    item.name = service_model.name

    db_obj = identity_service_mng.update(obj_in=item, db_obj=service_model)

    assert db_obj is None
