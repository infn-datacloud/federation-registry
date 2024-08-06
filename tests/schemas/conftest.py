"""File to set tests configuration parameters and common fixtures."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from flaat.user_infos import UserInfos

from fed_reg.location.schemas import LocationCreate
from fed_reg.main import app
from fed_reg.project.schemas import ProjectCreate
from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    BlockStorageServiceCreateExtended,
    ComputeQuotaCreateExtended,
    ComputeServiceCreateExtended,
    IdentityProviderCreateExtended,
    NetworkQuotaCreateExtended,
    NetworkServiceCreateExtended,
    ObjectStoreQuotaCreateExtended,
    ObjectStoreServiceCreateExtended,
    PrivateFlavorCreateExtended,
    PrivateImageCreateExtended,
    PrivateNetworkCreateExtended,
    ProviderCreateExtended,
    RegionCreateExtended,
    SharedFlavorCreateExtended,
    SharedImageCreateExtended,
    SharedNetworkCreateExtended,
    SLACreateExtended,
    UserGroupCreateExtended,
)
from fed_reg.service.schemas import IdentityServiceCreate
from tests.create_dict import (
    auth_method_dict,
    block_storage_service_schema_dict,
    compute_service_schema_dict,
    flavor_schema_dict,
    identity_provider_schema_dict,
    identity_service_schema_dict,
    image_schema_dict,
    location_schema_dict,
    network_schema_dict,
    network_service_schema_dict,
    object_store_service_schema_dict,
    project_schema_dict,
    provider_schema_dict,
    region_schema_dict,
    sla_schema_dict,
    user_group_schema_dict,
)
from tests.utils import MOCK_READ_EMAIL, MOCK_WRITE_EMAIL


@pytest.fixture
def location_create_schema() -> LocationCreate:
    return LocationCreate(**location_schema_dict())


@pytest.fixture
def project_create_schema() -> ProjectCreate:
    return ProjectCreate(**project_schema_dict())


@pytest.fixture
def identity_service_create_schema() -> IdentityServiceCreate:
    return IdentityServiceCreate(**identity_service_schema_dict())


@pytest.fixture
def private_flavor_create_ext_schema() -> PrivateFlavorCreateExtended:
    return PrivateFlavorCreateExtended(**flavor_schema_dict(), projects=[uuid4()])


@pytest.fixture
def shared_flavor_create_ext_schema() -> SharedFlavorCreateExtended:
    return SharedFlavorCreateExtended(**flavor_schema_dict())


@pytest.fixture
def identity_provider_create_ext_schema(
    user_group_create_ext_schema: UserGroupCreateExtended,
) -> IdentityProviderCreateExtended:
    return IdentityProviderCreateExtended(
        **identity_provider_schema_dict(),
        relationship=auth_method_dict(),
        user_groups=[user_group_create_ext_schema],
    )


@pytest.fixture
def private_image_create_ext_schema() -> PrivateImageCreateExtended:
    return PrivateImageCreateExtended(**image_schema_dict(), projects=[uuid4()])


@pytest.fixture
def shared_image_create_ext_schema() -> SharedImageCreateExtended:
    return SharedImageCreateExtended(**image_schema_dict())


@pytest.fixture
def private_network_create_ext_schema() -> PrivateNetworkCreateExtended:
    return PrivateNetworkCreateExtended(**network_schema_dict())


@pytest.fixture
def shared_network_create_ext_schema() -> SharedNetworkCreateExtended:
    return SharedNetworkCreateExtended(**network_schema_dict())


@pytest.fixture
def provider_create_ext_schema() -> ProviderCreateExtended:
    return ProviderCreateExtended(**provider_schema_dict())


@pytest.fixture
def block_storage_quota_create_ext_schema() -> BlockStorageQuotaCreateExtended:
    return BlockStorageQuotaCreateExtended(project=uuid4())


@pytest.fixture
def compute_quota_create_ext_schema() -> ComputeQuotaCreateExtended:
    return ComputeQuotaCreateExtended(project=uuid4())


@pytest.fixture
def network_quota_create_ext_schema() -> NetworkQuotaCreateExtended:
    return NetworkQuotaCreateExtended(project=uuid4())


@pytest.fixture
def object_store_quota_create_ext_schema() -> ObjectStoreQuotaCreateExtended:
    return ObjectStoreQuotaCreateExtended(project=uuid4())


@pytest.fixture
def region_create_ext_schema() -> RegionCreateExtended:
    return RegionCreateExtended(**region_schema_dict())


@pytest.fixture
def block_storage_service_create_ext_schema() -> BlockStorageServiceCreateExtended:
    return BlockStorageServiceCreateExtended(**block_storage_service_schema_dict())


@pytest.fixture
def compute_service_create_ext_schema() -> ComputeServiceCreateExtended:
    return ComputeServiceCreateExtended(**compute_service_schema_dict())


@pytest.fixture
def network_service_create_ext_schema() -> NetworkServiceCreateExtended:
    return NetworkServiceCreateExtended(**network_service_schema_dict())


@pytest.fixture
def object_store_service_create_ext_schema() -> ObjectStoreServiceCreateExtended:
    return ObjectStoreServiceCreateExtended(**object_store_service_schema_dict())


@pytest.fixture
def sla_create_ext_schema() -> SLACreateExtended:
    return SLACreateExtended(**sla_schema_dict(), project=uuid4())


@pytest.fixture
def user_group_create_ext_schema(
    sla_create_ext_schema: SLACreateExtended,
) -> UserGroupCreateExtended:
    return UserGroupCreateExtended(
        **user_group_schema_dict(), sla=sla_create_ext_schema
    )


@pytest.fixture
def client_no_authn():
    return TestClient(app)


@pytest.fixture
def client_with_token():
    return TestClient(app, headers={"Authorization": "Bearer fake"})


@pytest.fixture
def user_infos_with_write_email() -> UserInfos:
    """Fake user with email. It has write access rights."""
    return UserInfos(
        access_token_info=None,
        user_info={"email": MOCK_WRITE_EMAIL},
        introspection_info=None,
    )


@pytest.fixture
def user_infos_with_read_email() -> UserInfos:
    """Fake user with email. It has only read access rights."""
    return UserInfos(
        access_token_info=None,
        user_info={"email": MOCK_READ_EMAIL},
        introspection_info=None,
    )


@pytest.fixture
def user_infos_without_email() -> UserInfos:
    """Fake user without email."""
    return UserInfos(access_token_info=None, user_info={}, introspection_info=None)
