import os
from typing import Any

from fastapi import status
from fastapi.testclient import TestClient
from pytest_cases import case, parametrize_with_cases

from fed_reg.config import get_settings
from fed_reg.flavor.models import Flavor
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.image.models import Image
from fed_reg.location.models import Location
from fed_reg.network.models import Network
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fed_reg.region.models import Region
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fed_reg.sla.models import SLA
from fed_reg.user_group.models import UserGroup
from tests.models.utils import region_model_dict
from tests.schemas.utils import provider_schema_dict
from tests.utils import random_lower_string


class CaseClientStatus:
    def case_no_authn(self, client_no_authn: TestClient) -> tuple[TestClient, int]:
        return client_no_authn, status.HTTP_403_FORBIDDEN

    def case_no_authz(self, client_with_token: TestClient) -> tuple[TestClient, int]:
        return client_with_token, status.HTTP_401_UNAUTHORIZED


class CaseItemEndpoint:
    def case_flavor(
        self, compute_service_model: ComputeService, flavor_model: Flavor
    ) -> tuple[Flavor, str]:
        compute_service_model.flavors.connect(flavor_model)
        return flavor_model, "flavors"

    def case_identity_provider(
        self, identity_provider_model: IdentityProvider
    ) -> tuple[IdentityProvider, str]:
        return identity_provider_model, "identity_providers"

    def case_image(
        self, compute_service_model: ComputeService, image_model: Image
    ) -> tuple[Image, str]:
        compute_service_model.images.connect(image_model)
        return image_model, "images"

    def case_location(self, location_model: Location) -> tuple[Location, str]:
        return location_model, "locations"

    def case_network(
        self, network_model: Network, network_service_model: NetworkService
    ) -> tuple[Network, str]:
        network_service_model.networks.connect(network_model)
        return network_model, "networks"

    def case_project(
        self, project_model: Project, provider_model: Provider
    ) -> tuple[Project, str]:
        provider_model.projects.connect(project_model)
        return project_model, "projects"

    @case(tags=["provider"])
    def case_provider(self, provider_model: Provider) -> tuple[Provider, str]:
        return provider_model, "providers"

    def case_block_storage_quota(
        self, block_storage_quota_model: BlockStorageQuota
    ) -> tuple[BlockStorageQuota, str]:
        return block_storage_quota_model, "block_storage_quotas"

    def case_compute_quota(
        self, compute_quota_model: ComputeQuota
    ) -> tuple[ComputeQuota, str]:
        return compute_quota_model, "compute_quotas"

    def case_network_quota(
        self, network_quota_model: NetworkQuota
    ) -> tuple[NetworkQuota, str]:
        return network_quota_model, "network_quotas"

    def case_object_store_quota(
        self, object_store_quota_model: ObjectStoreQuota
    ) -> tuple[ObjectStoreQuota, str]:
        return object_store_quota_model, "object_store_quotas"

    def case_region(
        self, provider_model: Provider, region_model: Region
    ) -> tuple[Region, str]:
        provider_model.regions.connect(region_model)
        r2 = Region(**region_model_dict()).save()
        provider_model.regions.connect(r2)
        return region_model, "regions"

    def case_block_storage_service(
        self, block_storage_service_model: BlockStorageService
    ) -> tuple[BlockStorageService, str]:
        return block_storage_service_model, "block_storage_services"

    def case_compute_service(
        self, compute_service_model: ComputeService
    ) -> tuple[ComputeService, str]:
        return compute_service_model, "compute_services"

    def case_identity_service(
        self, identity_service_model: IdentityService
    ) -> tuple[IdentityService, str]:
        return identity_service_model, "identity_services"

    def case_network_service(
        self, network_service_model: NetworkService
    ) -> tuple[NetworkService, str]:
        return network_service_model, "network_services"

    def case_object_store_service(
        self, object_store_service_model: ObjectStoreService
    ) -> tuple[ObjectStoreService, str]:
        return object_store_service_model, "object_store_services"

    def case_sla(self, sla_model: SLA) -> tuple[SLA, str]:
        return sla_model, "slas"

    def case_user_group(
        self, identity_provider_model: IdentityProvider, user_group_model: UserGroup
    ) -> tuple[UserGroup, str]:
        identity_provider_model.user_groups.connect(user_group_model)
        return user_group_model, "user_groups"


@parametrize_with_cases("client, status_code", cases=CaseClientStatus)
@parametrize_with_cases("item, endpoint", cases=CaseItemEndpoint)
def test_patch_no_auth(client: TestClient, status_code: int, item: Any, endpoint: str):
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client.patch(url, json={"description": random_lower_string()})
    assert resp.status_code == status_code


@parametrize_with_cases("client, status_code", cases=CaseClientStatus)
@parametrize_with_cases("item, endpoint", cases=CaseItemEndpoint, has_tag="provider")
def test_post_no_auth(client: TestClient, status_code: int, item: Any, endpoint: str):
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client.post(url, json=provider_schema_dict())
    assert resp.status_code == status_code


@parametrize_with_cases("client, status_code", cases=CaseClientStatus)
@parametrize_with_cases("item, endpoint", cases=CaseItemEndpoint, has_tag="provider")
def test_put_no_auth(client: TestClient, status_code: int, item: Any, endpoint: str):
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client.put(url, json=provider_schema_dict())
    assert resp.status_code == status_code


@parametrize_with_cases("client, status_code", cases=CaseClientStatus)
@parametrize_with_cases("item, endpoint", cases=CaseItemEndpoint)
def test_delete_no_auth(client: TestClient, status_code: int, item: Any, endpoint: str):
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client.delete(url)
    assert resp.status_code == status_code


@parametrize_with_cases("item, endpoint", cases=CaseItemEndpoint)
def test_get_no_auth(client_no_authn: TestClient, item: Any, endpoint: str):
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_no_authn.get(url)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data is not None


@parametrize_with_cases("item, endpoint", cases=CaseItemEndpoint)
def test_get_multi_no_auth(client_no_authn: TestClient, item: Any, endpoint: str):
    settings = get_settings()
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_no_authn.get(url)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) > 0
