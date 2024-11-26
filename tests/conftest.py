"""File to set tests configuration parameters and common fixtures."""
import os
from typing import Any, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from flaat.user_infos import UserInfos
from neomodel import db

from fed_reg.config import Settings
from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.location.models import Location
from fed_reg.location.schemas import LocationCreate
from fed_reg.main import app, settings
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.project.schemas import ProjectCreate
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    ComputeQuotaCreateExtended,
    IdentityProviderCreateExtended,
    NetworkQuotaCreateExtended,
    ObjectStoreQuotaCreateExtended,
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
    # auth_method_dict,
    # block_storage_service_schema_dict,
    # compute_service_schema_dict,
    flavor_schema_dict,
    identity_provider_schema_dict,
    # identity_service_schema_dict,
    image_schema_dict,
    location_schema_dict,
    network_schema_dict,
    # network_service_schema_dict,
    # object_store_service_schema_dict,
    project_schema_dict,
    provider_schema_dict,
    region_schema_dict,
    sla_schema_dict,
    user_group_schema_dict,
)
from tests.utils import (
    MOCK_READ_EMAIL,
    MOCK_WRITE_EMAIL,
    random_lower_string,
    random_start_end_dates,
)


def pytest_addoption(parser):
    """
    Adds the command line option --resetdb.

    :param parser: The parser object. Please see <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_addoption>`_
    :type Parser object: For more information please see <https://docs.pytest.org/en/latest/reference.html#_pytest.config.Parser>`_
    """
    parser.addoption(
        "--resetdb",
        action="store_true",
        help="Ensures that the database is clear prior to running tests for neomodel",
        default=False,
    )


@pytest.fixture(scope="session", autouse=True)
def setup_neo4j_session(request):
    """
    Provides initial connection to the database and sets up the rest of the test suite

    :param request: The request object. Please see <https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_sessionstart>`_
    :type Request object: For more information please see <https://docs.pytest.org/en/latest/reference.html#request>`_
    """
    settings.NEO4J_DB_URL = os.environ.get(
        "NEO4J_TEST_URL", "bolt://neo4j:password@localhost:7687"
    )

    # Clear the database if required
    database_is_populated, _ = db.cypher_query(
        "MATCH (a) return count(a)>0 as database_is_populated"
    )
    if database_is_populated[0][0]:
        if not request.config.getoption("resetdb"):
            raise SystemError(
                "Please note: The database seems to be populated.\n"
                + "\tEither delete all nodesand edges manually, or set the "
                + "--resetdb parameter when calling pytest\n\n"
                + "\tpytest --resetdb."
            )

        db.clear_neo4j_database(clear_constraints=True, clear_indexes=True)
        db.install_all_labels()

    db.cypher_query(
        "CREATE OR REPLACE USER test SET PASSWORD 'foobarbaz' CHANGE NOT REQUIRED"
    )
    if db.database_edition == "enterprise":
        db.cypher_query("GRANT ROLE publisher TO test")
        db.cypher_query("GRANT IMPERSONATE (test) ON DBMS TO admin")


@pytest.fixture(autouse=True)
def clear_os_environment(monkeypatch) -> None:
    """Clear the OS environment."""
    for k in Settings.__fields__.keys():
        monkeypatch.delenv(k, None)
    if "test_settings_default" not in os.environ.get("PYTEST_CURRENT_TEST", None):
        settings.NEO4J_DB_URL = os.environ.get(
            "NEO4J_TEST_URL", "bolt://neo4j:password@localhost:7687"
        )


@pytest.fixture(autouse=True)
def cleanup() -> Generator[None, Any, None]:
    """Clear DB after every test

    Yields:
        Generator[None, Any, None]: Nothing
    """
    yield
    db.clear_neo4j_database()


# @pytest.fixture(scope="session", autouse=False)
# def close_db_conn() -> Generator[None, Any, None]:
#     """Close connection with the DB at the end of the test.

#     Yields:
#         Generator[None, Any, None]: Nothing
#     """
#     yield
#     db.close_connection()


@pytest.fixture
def flavor_model() -> Flavor:
    return Flavor(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def private_flavor_model() -> PrivateFlavor:
    return PrivateFlavor(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def shared_flavor_model() -> SharedFlavor:
    return SharedFlavor(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def identity_provider_model() -> IdentityProvider:
    return IdentityProvider(
        endpoint=random_lower_string(), group_claim=random_lower_string()
    ).save()


@pytest.fixture
def image_model() -> Image:
    return Image(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def private_image_model() -> PrivateImage:
    return PrivateImage(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def shared_image_model() -> SharedImage:
    return SharedImage(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def location_model() -> Location:
    return Location(site=random_lower_string(), country=random_lower_string()).save()


@pytest.fixture
def network_model() -> Network:
    return Network(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def private_network_model() -> PrivateNetwork:
    return PrivateNetwork(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def shared_network_model() -> SharedNetwork:
    return SharedNetwork(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def project_model() -> Project:
    return Project(name=random_lower_string(), uuid=random_lower_string()).save()


@pytest.fixture
def provider_model() -> Provider:
    return Provider(name=random_lower_string(), type=random_lower_string()).save()


@pytest.fixture
def quota_model() -> Quota:
    return Quota().save()


@pytest.fixture
def block_storage_quota_model() -> BlockStorageQuota:
    return BlockStorageQuota().save()


@pytest.fixture
def compute_quota_model() -> ComputeQuota:
    return ComputeQuota().save()


@pytest.fixture
def network_quota_model() -> NetworkQuota:
    return NetworkQuota().save()


@pytest.fixture
def object_store_quota_model() -> ObjectStoreQuota:
    return ObjectStoreQuota().save()


@pytest.fixture
def region_model() -> Region:
    return Region(name=random_lower_string()).save()


@pytest.fixture
def service_model() -> Service:
    return Service(endpoint=random_lower_string(), name=random_lower_string()).save()


@pytest.fixture
def block_storage_service_model() -> BlockStorageService:
    return BlockStorageService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()


@pytest.fixture
def compute_service_model() -> ComputeService:
    return ComputeService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()


@pytest.fixture
def identity_service_model() -> IdentityService:
    return IdentityService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()


@pytest.fixture
def network_service_model() -> NetworkService:
    return NetworkService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()


@pytest.fixture
def object_store_service_model() -> ObjectStoreService:
    return ObjectStoreService(
        endpoint=random_lower_string(), name=random_lower_string()
    ).save()


@pytest.fixture
def sla_model() -> SLA:
    start_date, end_date = random_start_end_dates()
    return SLA(
        doc_uuid=random_lower_string(), start_date=start_date, end_date=end_date
    ).save()


@pytest.fixture
def user_group_model() -> UserGroup:
    return UserGroup(name=random_lower_string()).save()


@pytest.fixture
def location_create_schema() -> LocationCreate:
    return LocationCreate(**location_schema_dict())


@pytest.fixture
def project_create_schema() -> ProjectCreate:
    return ProjectCreate(**project_schema_dict())


# @pytest.fixture
# def identity_service_create_schema() -> IdentityServiceCreate:
#     return IdentityServiceCreate(**identity_service_schema_dict())


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
        # relationship=auth_method_dict(),
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


# @pytest.fixture
# def block_storage_service_create_ext_schema() -> BlockStorageServiceCreateExtended:
#     return BlockStorageServiceCreateExtended(**block_storage_service_schema_dict())


# @pytest.fixture
# def compute_service_create_ext_schema() -> ComputeServiceCreateExtended:
#     return ComputeServiceCreateExtended(**compute_service_schema_dict())


# @pytest.fixture
# def network_service_create_ext_schema() -> NetworkServiceCreateExtended:
#     return NetworkServiceCreateExtended(**network_service_schema_dict())


# @pytest.fixture
# def object_store_service_create_ext_schema() -> ObjectStoreServiceCreateExtended:
#     return ObjectStoreServiceCreateExtended(**object_store_service_schema_dict())


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
