import os
from typing import Any
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from flaat.user_infos import UserInfos
from pytest_cases import parametrize, parametrize_with_cases

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
from tests.models.utils import auth_method_model_dict


@parametrize(single=[True, False])
@parametrize(with_conn=[True, False])
@parametrize(is_public=[True, False])
class CaseItemEndpointSchemaDir:
    def _determine_schema(self, *, with_conn: bool, is_public: bool) -> str:
        if with_conn:
            return "public_extended" if is_public else "private_extended"
        else:
            return "public" if is_public else "private"

    def case_flavor(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        compute_service_model: ComputeService,
        flavor_model: Flavor,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, Flavor, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(compute_service_model)
            compute_service_model.flavors.connect(flavor_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return client, with_conn, single, schema, flavor_model, "flavors", "flavor"

    def case_identity_provider(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        identity_provider_model: IdentityProvider,
        provider_model: Provider,
    ) -> tuple[TestClient, bool, bool, str, IdentityProvider, str, str]:
        if with_conn:
            provider_model.identity_providers.connect(
                identity_provider_model, auth_method_model_dict()
            )
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            identity_provider_model,
            "identity_providers",
            "identity_provider",
        )

    def case_image(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        compute_service_model: ComputeService,
        image_model: Image,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, Image, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(compute_service_model)
            compute_service_model.images.connect(image_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return client, with_conn, single, schema, image_model, "images", "image"

    def case_location(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        location_model: Location,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, Location, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.location.connect(location_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            location_model,
            "locations",
            "location",
        )

    def case_network(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        network_model: Network,
        network_service_model: NetworkService,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, Network, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(network_service_model)
            network_service_model.networks.connect(network_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return client, with_conn, single, schema, network_model, "networks", "network"

    def case_project(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        project_model: Project,
        provider_model: Provider,
    ) -> tuple[TestClient, bool, bool, str, Project, str, str]:
        if with_conn:
            provider_model.projects.connect(project_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return client, with_conn, single, schema, project_model, "projects", "project"

    def case_provider(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        provider_model: Provider,
    ) -> tuple[TestClient, bool, bool, str, Provider, str, str]:
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            provider_model,
            "providers",
            "provider",
        )

    def case_block_storage_quota(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        block_storage_quota_model: BlockStorageQuota,
        block_storage_service_model: BlockStorageService,
        project_model: Project,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, BlockStorageQuota, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(block_storage_service_model)
            block_storage_service_model.quotas.connect(block_storage_quota_model)
            provider_model.projects.connect(project_model)
            project_model.quotas.connect(block_storage_quota_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            block_storage_quota_model,
            "block_storage_quotas",
            "quota",
        )

    def case_compute_quota(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        compute_quota_model: ComputeQuota,
        compute_service_model: BlockStorageService,
        project_model: Project,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, ComputeQuota, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(compute_service_model)
            compute_service_model.quotas.connect(compute_quota_model)
            provider_model.projects.connect(project_model)
            project_model.quotas.connect(compute_quota_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            compute_quota_model,
            "compute_quotas",
            "quota",
        )

    def case_network_quota(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        network_quota_model: NetworkQuota,
        network_service_model: BlockStorageService,
        project_model: Project,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, NetworkQuota, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(network_service_model)
            network_service_model.quotas.connect(network_quota_model)
            provider_model.projects.connect(project_model)
            project_model.quotas.connect(network_quota_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            network_quota_model,
            "network_quotas",
            "quota",
        )

    def case_object_store_quota(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        object_store_quota_model: ObjectStoreQuota,
        object_store_service_model: ObjectStoreService,
        project_model: Project,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, BlockStorageQuota, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(object_store_service_model)
            object_store_service_model.quotas.connect(object_store_quota_model)
            provider_model.projects.connect(project_model)
            project_model.quotas.connect(object_store_quota_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            object_store_quota_model,
            "object_store_quotas",
            "quota",
        )

    def case_region(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, Region, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return client, with_conn, single, schema, region_model, "regions", "region"

    def case_block_storage_service(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        block_storage_service_model: BlockStorageService,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, BlockStorageService, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(block_storage_service_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            block_storage_service_model,
            "block_storage_services",
            "service",
        )

    def case_compute_service(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        compute_service_model: ComputeService,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, ComputeService, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(compute_service_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            compute_service_model,
            "compute_services",
            "service",
        )

    def case_identity_service(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        identity_service_model: IdentityService,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, IdentityService, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(identity_service_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            identity_service_model,
            "identity_services",
            "service",
        )

    def case_network_service(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        network_service_model: NetworkService,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, NetworkService, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(network_service_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            network_service_model,
            "network_services",
            "service",
        )

    def case_object_store_service(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        object_store_service_model: ObjectStoreService,
        provider_model: Provider,
        region_model: Region,
    ) -> tuple[TestClient, bool, bool, str, ObjectStoreService, str, str]:
        if with_conn:
            provider_model.regions.connect(region_model)
            region_model.services.connect(object_store_service_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            object_store_service_model,
            "object_store_services",
            "service",
        )

    def case_sla(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        identity_provider_model: IdentityProvider,
        project_model: Project,
        provider_model: Provider,
        sla_model: SLA,
        user_group_model: UserGroup,
    ) -> tuple[TestClient, bool, bool, str, SLA, str, str]:
        if with_conn:
            provider_model.identity_providers.connect(
                identity_provider_model, auth_method_model_dict()
            )
            identity_provider_model.user_groups.connect(user_group_model)
            user_group_model.slas.connect(sla_model)
            provider_model.projects.connect(project_model)
            project_model.sla.connect(sla_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return client, with_conn, single, schema, sla_model, "slas", "sla"

    def case_user_group(
        self,
        with_conn: bool,
        single: bool,
        is_public: bool,
        client_no_authn: TestClient,
        client_with_token: TestClient,
        identity_provider_model: IdentityProvider,
        provider_model: Provider,
        user_group_model: UserGroup,
    ) -> tuple[TestClient, bool, bool, str, UserGroup, str, str]:
        if with_conn:
            provider_model.identity_providers.connect(
                identity_provider_model, auth_method_model_dict()
            )
            identity_provider_model.user_groups.connect(user_group_model)
        client = client_no_authn if is_public else client_with_token
        schema = self._determine_schema(with_conn=with_conn, is_public=is_public)
        return (
            client,
            with_conn,
            single,
            schema,
            user_group_model,
            "user_groups",
            "user_group",
        )


@parametrize_with_cases(
    "client, with_conn, single, schema, item, endpoint, dir",
    cases=CaseItemEndpointSchemaDir,
)
def test_get_returned_schema(
    user_infos_with_read_email: UserInfos,
    client: TestClient,
    with_conn: bool,
    single: bool,
    item: Any,
    endpoint: str,
    schema: str,
    dir: str,
):
    settings = get_settings()
    if single:
        url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    else:
        url = os.path.join(settings.API_V1_STR, endpoint)

    if schema.startswith("private"):
        with patch(
            f"fed_reg.{dir}.api.v1.endpoints.flaat.get_user_infos_from_request",
            return_value=user_infos_with_read_email,
        ):
            resp = client.get(url, params={"with_conn": with_conn})
    else:
        resp = client.get(url, params={"with_conn": with_conn})
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    if single:
        assert data is not None
    else:
        assert len(data) > 0
        data = data[0]

    assert data["schema_type"] == schema
