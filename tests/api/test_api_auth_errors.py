import os
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.identity_provider.models import IdentityProvider
from fedreg.image.models import PrivateImage, SharedImage
from fedreg.location.models import Location
from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fedreg.region.models import Region
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
    ServiceType,
)
from fedreg.sla.models import SLA
from fedreg.user_group.models import UserGroup
from flaat.user_infos import UserInfos
from pytest_cases import case, parametrize_with_cases

from fed_reg.config import get_settings
from tests.api.conftest import MOCK_ADMIN_EMAL
from tests.utils import (
    random_country,
    random_email,
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_start_end_dates,
    random_url,
)


class CaseItem:
    def case_private_flavor(self) -> tuple[str, PrivateFlavor]:
        item = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        return "flavors", item

    def case_shared_flavor(self) -> tuple[str, SharedFlavor]:
        item = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        return "flavors", item

    def case_identity_provider(self) -> tuple[str, IdentityProvider]:
        item = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        return "identity_providers", item

    def case_private_image(self) -> tuple[str, PrivateImage]:
        item = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
        return "images", item

    def case_shared_image(self) -> tuple[str, SharedImage]:
        item = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
        return "images", item

    def case_location(self) -> tuple[str, Location]:
        item = Location(site=random_lower_string(), country=random_country()).save()
        return "locations", item

    def case_private_network(self) -> tuple[str, PrivateNetwork]:
        item = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        return "networks", item

    def case_shared_network(self) -> tuple[str, SharedNetwork]:
        item = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        return "networks", item

    def case_project(self) -> tuple[str, Project]:
        item = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        return "projects", item

    @case(tags="provider")
    def case_provider(self) -> tuple[str, Provider]:
        item = Provider(name=random_lower_string(), type=random_provider_type()).save()
        return "providers", item

    def case_block_storage_quota(self) -> tuple[str, BlockStorageQuota]:
        item = BlockStorageQuota().save()
        return "block_storage_quotas", item

    def case_compute_quota(self) -> tuple[str, ComputeQuota]:
        item = ComputeQuota().save()
        return "compute_quotas", item

    def case_network_quota(self) -> tuple[str, NetworkQuota]:
        item = NetworkQuota().save()
        return "network_quotas", item

    def case_object_store_quota(self) -> tuple[str, ObjectStoreQuota]:
        item = ObjectStoreQuota().save()
        return "object_store_quotas", item

    def case_region(self) -> tuple[str, Region]:
        item = Region(name=random_lower_string()).save()
        return "regions", item

    def case_block_storage_service(self) -> tuple[str, BlockStorageService]:
        item = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        return "block_storage_services", item

    def case_compute_service(self) -> tuple[str, ComputeService]:
        item = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        return "compute_services", item

    def case_identity_service(self) -> tuple[str, IdentityService]:
        item = IdentityService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
        ).save()
        return "identity_services", item

    def case_network_service(self) -> tuple[str, NetworkService]:
        item = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        return "network_services", item

    def case_object_store_service(self) -> tuple[str, ObjectStoreService]:
        item = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        return "object_store_services", item

    def case_sla(self) -> tuple[str, SLA]:
        start_date, end_date = random_start_end_dates()
        item = SLA(
            doc_uuid=str(uuid4()), start_date=start_date, end_date=end_date
        ).save()
        return "slas", item

    def case_user_group(self) -> tuple[str, UserGroup]:
        item = UserGroup(name=random_lower_string()).save()
        return "user_groups", item


class CaseUserInfos:
    @case(tags="valid")
    def case_user_infos(self, user_infos: UserInfos) -> UserInfos:
        return user_infos

    @case(tags="invalid")
    def case_no_admin_email(self) -> UserInfos:
        return UserInfos(
            access_token_info=None,
            user_info={
                "email": random_email(),
                "iss": random_url(),
                "sub": random_lower_string(),
            },
            introspection_info=None,
        )

    @case(tags="invalid")
    def case_no_issuer(self) -> UserInfos:
        return UserInfos(
            access_token_info=None,
            user_info={"email": MOCK_ADMIN_EMAL, "sub": random_lower_string()},
            introspection_info=None,
        )

    @case(tags="invalid")
    def case_no_subject(self) -> UserInfos:
        return UserInfos(
            access_token_info=None,
            user_info={"email": MOCK_ADMIN_EMAL, "iss": random_url()},
            introspection_info=None,
        )


# DELETE Operations


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_delete_no_token(
    client_without_token: TestClient, endpoint: str, item: Any
) -> None:
    """If not authenticated, the endpoint gives 403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_without_token.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_delete_no_token_no_resource(
    client_without_token: TestClient, endpoint: str, item: Any
) -> None:
    """If not authenticated and resources does not exists, the endpoint still gives
    403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_without_token.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_delete_invalid_token(
    client_with_token: TestClient, endpoint: str, item: Any
) -> None:
    """If authenticated but not authorized, the endpoint gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_delete_invalid_token_no_resource(
    client_with_token: TestClient, endpoint: str, item: Any
) -> None:
    """If authenticated but not authorized and resources does not exists, the endpoint
    still gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item", cases=CaseItem)
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="invalid")
def test_delete_no_authz_no_resource(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Any,
) -> None:
    settings = get_settings()
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item", cases=CaseItem)
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="valid")
def test_delete(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Any,
) -> None:
    settings = get_settings()
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


# PATCH Operations


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_patch_no_token(
    client_without_token: TestClient, endpoint: str, item: Any
) -> None:
    """If not authenticated, the endpoint gives 403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_without_token.patch(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_patch_no_token_no_resource(
    client_without_token: TestClient, endpoint: str, item: Any
) -> None:
    """If not authenticated and resources does not exists, the endpoint still gives
    403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_without_token.patch(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_patch_invalid_token(
    client_with_token: TestClient, endpoint: str, item: Any
) -> None:
    """If authenticated but not authorized, the endpoint gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.patch(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem)
def test_patch_invalid_token_no_resource(
    client_with_token: TestClient, endpoint: str, item: Any
) -> None:
    """If authenticated but not authorized and resources does not exists, the endpoint
    still gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.patch(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item", cases=CaseItem)
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="invalid")
def test_patch_no_authz_no_resource(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Any,
) -> None:
    settings = get_settings()
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.patch(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item", cases=CaseItem)
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="valid")
def test_patch_no_changes(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Any,
) -> None:
    settings = get_settings()
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.patch(url, json={})
    assert resp.status_code == status.HTTP_304_NOT_MODIFIED


# POST Operations


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_post_no_token(
    client_without_token: TestClient, endpoint: str, item: Any
) -> None:
    """If not authenticated, the endpoint gives 403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_without_token.post(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_post_no_token_no_resource(
    client_without_token: TestClient, endpoint: str, item: Provider
) -> None:
    """If not authenticated and resources does not exists, the endpoint still gives
    403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_without_token.post(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_post_invalid_token(
    client_with_token: TestClient, endpoint: str, item: Provider
) -> None:
    """If authenticated but not authorized, the endpoint gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_with_token.post(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_post_invalid_token_no_resource(
    client_with_token: TestClient, endpoint: str, item: Provider
) -> None:
    """If authenticated but not authorized and resources does not exists, the endpoint
    still gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_with_token.post(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="invalid")
def test_post_no_authz_no_resource(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Provider,
) -> None:
    settings = get_settings()
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_with_token.post(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# PUT Operations


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_put_no_token(
    client_without_token: TestClient, endpoint: str, item: Any
) -> None:
    """If not authenticated, the endpoint gives 403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_without_token.put(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_put_no_token_no_resource(
    client_without_token: TestClient, endpoint: str, item: Provider
) -> None:
    """If not authenticated and resources does not exists, the endpoint still gives
    403 `forbidden`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_without_token.put(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_put_invalid_token(
    client_with_token: TestClient, endpoint: str, item: Provider
) -> None:
    """If authenticated but not authorized, the endpoint gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.put(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
def test_put_invalid_token_no_resource(
    client_with_token: TestClient, endpoint: str, item: Provider
) -> None:
    """If authenticated but not authorized and resources does not exists, the endpoint
    still gives 401 `unauthorized`."""
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.put(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item", cases=CaseItem, has_tag="provider")
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="invalid")
def test_put_no_authz_no_resource(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Provider,
) -> None:
    settings = get_settings()
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.put(url, json={})
    assert resp.status_code == status.HTTP_403_FORBIDDEN
