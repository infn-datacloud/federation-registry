"""File to set tests configuration parameters and common fixtures."""

import pytest

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.location.models import Location
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    Quota,
)
from fed_reg.region.models import Region
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
    Service,
)
from fed_reg.sla.models import SLA
from fed_reg.user_group.models import UserGroup
from tests.models.utils import (
    flavor_model_dict,
    identity_provider_model_dict,
    image_model_dict,
    location_model_dict,
    network_model_dict,
    project_model_dict,
    provider_model_dict,
    quota_model_dict,
    region_model_dict,
    service_model_dict,
    sla_model_dict,
    user_group_model_dict,
)


@pytest.fixture
def flavor_model() -> Flavor:
    d = flavor_model_dict()
    return Flavor(**d).save()


@pytest.fixture
def private_flavor_model() -> PrivateFlavor:
    d = flavor_model_dict()
    return PrivateFlavor(**d).save()


@pytest.fixture
def shared_flavor_model() -> SharedFlavor:
    d = flavor_model_dict()
    return SharedFlavor(**d).save()


@pytest.fixture
def identity_provider_model() -> IdentityProvider:
    d = identity_provider_model_dict()
    return IdentityProvider(**d).save()


@pytest.fixture
def image_model() -> Image:
    d = image_model_dict()
    return Image(**d).save()


@pytest.fixture
def private_image_model() -> PrivateImage:
    d = image_model_dict()
    return PrivateImage(**d).save()


@pytest.fixture
def shared_image_model() -> SharedImage:
    d = image_model_dict()
    return SharedImage(**d).save()


@pytest.fixture
def location_model() -> Location:
    d = location_model_dict()
    return Location(**d).save()


@pytest.fixture
def network_model() -> Network:
    d = network_model_dict()
    return Network(**d).save()


@pytest.fixture
def private_network_model() -> PrivateNetwork:
    d = network_model_dict()
    return PrivateNetwork(**d).save()


@pytest.fixture
def shared_network_model() -> SharedNetwork:
    d = network_model_dict()
    return SharedNetwork(**d).save()


@pytest.fixture
def project_model() -> Project:
    d = project_model_dict()
    return Project(**d).save()


@pytest.fixture
def provider_model() -> Provider:
    d = provider_model_dict()
    return Provider(**d).save()


@pytest.fixture
def quota_model() -> Quota:
    d = quota_model_dict()
    return Quota(**d).save()


@pytest.fixture
def block_storage_quota_model() -> BlockStorageQuota:
    d = quota_model_dict()
    return BlockStorageQuota(**d).save()


@pytest.fixture
def compute_quota_model() -> ComputeQuota:
    d = quota_model_dict()
    return ComputeQuota(**d).save()


@pytest.fixture
def network_quota_model() -> NetworkQuota:
    d = quota_model_dict()
    return NetworkQuota(**d).save()


@pytest.fixture
def object_store_quota_model() -> ObjectStoreQuota:
    d = quota_model_dict()
    return ObjectStoreQuota(**d).save()


@pytest.fixture
def region_model() -> Region:
    d = region_model_dict()
    return Region(**d).save()


@pytest.fixture
def service_model() -> Service:
    d = service_model_dict()
    return Service(**d).save()


@pytest.fixture
def block_storage_service_model() -> BlockStorageService:
    d = service_model_dict()
    return BlockStorageService(**d).save()


@pytest.fixture
def compute_service_model() -> ComputeService:
    d = service_model_dict()
    return ComputeService(**d).save()


@pytest.fixture
def identity_service_model() -> IdentityService:
    d = service_model_dict()
    return IdentityService(**d).save()


@pytest.fixture
def network_service_model() -> NetworkService:
    d = service_model_dict()
    return NetworkService(**d).save()


@pytest.fixture
def object_store_service_model() -> ObjectStoreService:
    d = service_model_dict()
    return ObjectStoreService(**d).save()


@pytest.fixture
def sla_model() -> SLA:
    d = sla_model_dict()
    return SLA(**d).save()


@pytest.fixture
def user_group_model() -> UserGroup:
    d = user_group_model_dict()
    return UserGroup(**d).save()
