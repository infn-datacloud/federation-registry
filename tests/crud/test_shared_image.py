from uuid import uuid4

import pytest
from fedreg.image.models import SharedImage
from fedreg.image.schemas import SharedImageCreate
from fedreg.provider.models import Provider
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import ComputeService
from pytest_cases import parametrize_with_cases

from fed_reg.image.crud import shared_image_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_image_model() -> SharedImage:
    """Shared image model belonging to a different provider.

    Already connected to a compute service, a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    image = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.regions.connect(region)
    region.services.connect(service)
    service.images.connect(image)
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
def image_model(service_model: ComputeService) -> SharedImage:
    """Shared image model.

    Already connected to a compute service, a region and a provider.
    """
    image = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
    service_model.images.connect(image)
    return image


class CaseImage:
    def case_shared_image_create(self) -> SharedImageCreate:
        return SharedImageCreate(name=random_lower_string(), uuid=uuid4())


@parametrize_with_cases("item", cases=CaseImage)
def test_create(item: SharedImageCreate, service_model: ComputeService) -> None:
    """Create a new istance"""
    db_obj = shared_image_mng.create(obj_in=item, service=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedImage)
    assert db_obj.services.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseImage)
def test_create_same_uuid_diff_provider(
    item: SharedImageCreate,
    service_model: ComputeService,
    stand_alone_image_model: SharedImage,
) -> None:
    """A image with the given uuid already exists but on a different provider."""
    item.uuid = stand_alone_image_model.uuid

    db_obj = shared_image_mng.create(obj_in=item, service=service_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedImage)
    assert db_obj.services.is_connected(service_model)


@parametrize_with_cases("item", cases=CaseImage)
def test_create_already_exists(
    item: SharedImageCreate,
    image_model: SharedImage,
) -> None:
    """A image with the given uuid already exists"""
    service = image_model.services.single()
    region = service.region.single()
    provider = region.provider.single()

    item.uuid = image_model.uuid

    msg = (
        f"A shared image with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(ValueError, match=msg):
        shared_image_mng.create(obj_in=item, service=service)


@parametrize_with_cases("item", cases=CaseImage)
def test_update(item: SharedImageCreate, image_model: SharedImage) -> None:
    """Completely update the image attributes. Also override not set ones."""
    db_obj = shared_image_mng.update(obj_in=item, db_obj=image_model)

    assert db_obj is not None
    assert isinstance(db_obj, SharedImage)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseImage)
def test_update_no_changes(item: SharedImageCreate, image_model: SharedImage) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = image_model.uuid
    item.name = image_model.name

    db_obj = shared_image_mng.update(obj_in=item, db_obj=image_model)

    assert db_obj is None
