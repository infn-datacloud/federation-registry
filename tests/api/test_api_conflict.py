import os
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
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
from tests.utils import (
    random_country,
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_start_end_dates,
    random_url,
)

MOCK_ADMIN_EMAL = "admin@test.it"


@pytest.fixture
def user_infos() -> UserInfos:
    return UserInfos(
        access_token_info=None,
        user_info={
            "email": MOCK_ADMIN_EMAL,
            "iss": random_url(),
            "sub": random_lower_string(),
        },
        introspection_info=None,
    )


class CaseItem:
    def case_private_flavor(self) -> tuple[str, PrivateFlavor, dict[str, Any]]:
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        service.flavors.connect(item1)
        service.flavors.connect(item2)
        return "flavors", item1, {"uuid": item2.uuid}

    def case_shared_flavor(self) -> tuple[str, SharedFlavor, dict[str, Any]]:
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        service.flavors.connect(item1)
        service.flavors.connect(item2)
        return "flavors", item1, {"uuid": item2.uuid}

    def case_identity_provider(self) -> tuple[str, IdentityProvider, dict[str, Any]]:
        item1 = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        item2 = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        return "identity_providers", item1, {"endpoint": item2.endpoint}

    def case_private_image(self) -> tuple[str, PrivateImage, dict[str, Any]]:
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
        service.images.connect(item1)
        service.images.connect(item2)
        return "images", item1, {"uuid": item2.uuid}

    def case_shared_image(self) -> tuple[str, SharedImage, dict[str, Any]]:
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
        service.images.connect(item1)
        service.images.connect(item2)
        return "images", item1, {"uuid": item2.uuid}

    def case_location(self) -> tuple[str, Location, dict[str, Any]]:
        item1 = Location(site=random_lower_string(), country=random_country()).save()
        item2 = Location(site=random_lower_string(), country=random_country()).save()
        return "locations", item1, {"site": item2.site}

    def case_private_network(self) -> tuple[str, PrivateNetwork, dict[str, Any]]:
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        service.networks.connect(item1)
        service.networks.connect(item2)
        return "networks", item1, {"uuid": item2.uuid}

    def case_shared_network(self) -> tuple[str, SharedNetwork, dict[str, Any]]:
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        service.networks.connect(item1)
        service.networks.connect(item2)
        return "networks", item1, {"uuid": item2.uuid}

    def case_project(self) -> tuple[str, Project, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        item1 = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(item1)
        provider.projects.connect(item2)
        return "projects", item1, {"uuid": item2.uuid}

    @case(tags="provider")
    def case_provider(self) -> tuple[str, str, Provider, dict[str, Any]]:
        item1 = Provider(name=random_lower_string(), type=random_provider_type()).save()
        item2 = Provider(name=random_lower_string(), type=random_provider_type()).save()
        return "providers", item1, {"name": item2.name, "type": item2.type}

    def case_block_storage_quota_per_user(
        self,
    ) -> tuple[str, BlockStorageQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        item1 = BlockStorageQuota().save()
        item2 = BlockStorageQuota(per_user=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "block_storage_quotas", item1, {"per_user": item2.per_user}

    def case_compute_quota_per_user(self) -> tuple[str, ComputeQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = ComputeQuota().save()
        item2 = ComputeQuota(per_user=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "compute_quotas", item1, {"per_user": item2.per_user}

    def case_network_quota_per_user(self) -> tuple[str, NetworkQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = NetworkQuota().save()
        item2 = NetworkQuota(per_user=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "network_quotas", item1, {"per_user": item2.per_user}

    def case_object_store_quota_per_user(
        self,
    ) -> tuple[str, ObjectStoreQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        item1 = ObjectStoreQuota().save()
        item2 = ObjectStoreQuota(per_user=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "object_store_quotas", item1, {"per_user": item2.per_user}

    def case_block_storage_quota_usage(
        self,
    ) -> tuple[str, BlockStorageQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        item1 = BlockStorageQuota().save()
        item2 = BlockStorageQuota(usage=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "block_storage_quotas", item1, {"usage": item2.usage}

    def case_compute_quota_usage(self) -> tuple[str, ComputeQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = ComputeQuota().save()
        item2 = ComputeQuota(usage=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "compute_quotas", item1, {"usage": item2.usage}

    def case_network_quota_usage(self) -> tuple[str, NetworkQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = NetworkQuota().save()
        item2 = NetworkQuota(usage=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "network_quotas", item1, {"usage": item2.usage}

    def case_object_store_quota_usage(
        self,
    ) -> tuple[str, ObjectStoreQuota, dict[str, Any]]:
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        item1 = ObjectStoreQuota().save()
        item2 = ObjectStoreQuota(usage=True).save()
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "object_store_quotas", item1, {"usage": item2.usage}

    def case_region(self) -> tuple[str, Region, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        item1 = Region(name=random_lower_string()).save()
        item2 = Region(name=random_lower_string()).save()
        provider.regions.connect(item1)
        provider.regions.connect(item2)
        return "regions", item1, {"name": item2.name}

    def case_block_storage_service(
        self,
    ) -> tuple[str, BlockStorageService, dict[str, Any]]:
        item1 = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        item2 = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        return "block_storage_services", item1, {"endpoint": item2.endpoint}

    def case_compute_service(self) -> tuple[str, ComputeService, dict[str, Any]]:
        item1 = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item2 = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        return "compute_services", item1, {"endpoint": item2.endpoint}

    def case_identity_service(self) -> tuple[str, IdentityService, dict[str, Any]]:
        item1 = IdentityService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
        ).save()
        item2 = IdentityService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
        ).save()
        return "identity_services", item1, {"endpoint": item2.endpoint}

    def case_network_service(self) -> tuple[str, NetworkService, dict[str, Any]]:
        item1 = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item2 = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        return "network_services", item1, {"endpoint": item2.endpoint}

    def case_object_store_service(
        self,
    ) -> tuple[str, ObjectStoreService, dict[str, Any]]:
        item1 = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        item2 = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        return "object_store_services", item1, {"endpoint": item2.endpoint}

    def case_sla(self) -> tuple[str, SLA, dict[str, Any]]:
        start_date, end_date = random_start_end_dates()
        item1 = SLA(
            doc_uuid=str(uuid4()), start_date=start_date, end_date=end_date
        ).save()
        item2 = SLA(
            doc_uuid=str(uuid4()), start_date=start_date, end_date=end_date
        ).save()
        return "slas", item1, {"doc_uuid": item2.doc_uuid}

    def case_user_group(self) -> tuple[str, UserGroup, dict[str, Any]]:
        idp = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        item1 = UserGroup(name=random_lower_string()).save()
        item2 = UserGroup(name=random_lower_string()).save()
        idp.user_groups.connect(item1)
        idp.user_groups.connect(item2)
        return "user_groups", item1, {"name": item2.name}


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item1, new_data", cases=CaseItem)
def test_patch_conflict(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item1: Provider,
    new_data: dict[str, Any],
) -> None:
    settings = get_settings()
    settings.ADMIN_EMAIL_LIST = [MOCK_ADMIN_EMAL]
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, item1.uid)
    resp = client_with_token.patch(url, json=new_data)
    assert resp.status_code == status.HTTP_409_CONFLICT


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item1, new_data", cases=CaseItem, has_tag="provider")
def test_put_conflict(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item1: Provider,
    new_data: dict[str, Any],
) -> None:
    settings = get_settings()
    settings.ADMIN_EMAIL_LIST = [MOCK_ADMIN_EMAL]
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, item1.uid)
    resp = client_with_token.put(url, json=new_data)
    assert resp.status_code == status.HTTP_409_CONFLICT


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint, item1, new_data", cases=CaseItem, has_tag="provider")
def test_post_conflict(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item1: Provider,
    new_data: dict[str, Any],
) -> None:
    settings = get_settings()
    settings.ADMIN_EMAIL_LIST = [MOCK_ADMIN_EMAL]
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_with_token.post(url, json=new_data)
    assert resp.status_code == status.HTTP_409_CONFLICT
