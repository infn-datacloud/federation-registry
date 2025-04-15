import os
from typing import Any, Literal
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

from fed_reg.main import settings
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
    def case_private_flavor(self) -> tuple[str, PrivateFlavor, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = Region(name=random_lower_string()).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        project.private_flavors.connect(item1)
        project.private_flavors.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.flavors.connect(item1)
        service.flavors.connect(item2)
        return "flavors", item1

    def case_shared_flavor(self) -> tuple[str, SharedFlavor, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.regions.connect(region)
        region.services.connect(service)
        service.flavors.connect(item1)
        service.flavors.connect(item2)
        return "flavors", item1

    def case_identity_provider(self) -> tuple[str, IdentityProvider, dict[str, Any]]:
        item1 = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        _ = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        return "identity_providers", item1

    def case_private_image(self) -> tuple[str, PrivateImage, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = Region(name=random_lower_string()).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        project.private_images.connect(item1)
        project.private_images.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.images.connect(item1)
        service.images.connect(item2)
        return "images", item1

    def case_shared_image(self) -> tuple[str, SharedImage, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.regions.connect(region)
        region.services.connect(service)
        service.images.connect(item1)
        service.images.connect(item2)
        return "images", item1

    def case_location(self) -> tuple[str, Location, dict[str, Any]]:
        item1 = Location(site=random_lower_string(), country=random_country()).save()
        item2 = Location(site=random_lower_string(), country=random_country()).save()
        return "locations", item1, {"site": item2.site}

    def case_private_network(self) -> tuple[str, PrivateNetwork, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        region = Region(name=random_lower_string()).save()
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = PrivateNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        project.private_networks.connect(item1)
        project.private_networks.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.networks.connect(item1)
        service.networks.connect(item2)
        return "networks", item1

    def case_shared_network(self) -> tuple[str, SharedNetwork, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = SharedNetwork(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.regions.connect(region)
        region.services.connect(service)
        service.networks.connect(item1)
        service.networks.connect(item2)
        return "networks", item1

    def case_project(self) -> tuple[str, Project, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        item1 = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        item2 = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(item1)
        provider.projects.connect(item2)
        return "projects", item1

    @case(tags="provider")
    def case_provider(self) -> tuple[str, str, Provider, dict[str, Any]]:
        item1 = Provider(name=random_lower_string(), type=random_provider_type()).save()
        _ = Provider(name=random_lower_string(), type=random_provider_type()).save()
        return "providers", item1

    def case_block_storage_quota(
        self,
    ) -> tuple[str, BlockStorageQuota, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        item1 = BlockStorageQuota().save()
        item2 = BlockStorageQuota(per_user=True).save()
        provider.projects.connect(project)
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "block_storage_quotas", item1

    def case_compute_quota(self) -> tuple[str, ComputeQuota, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item1 = ComputeQuota().save()
        item2 = ComputeQuota(per_user=True).save()
        provider.projects.connect(project)
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "compute_quotas", item1

    def case_network_quota(self) -> tuple[str, NetworkQuota, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item1 = NetworkQuota().save()
        item2 = NetworkQuota(per_user=True).save()
        provider.projects.connect(project)
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "network_quotas", item1

    def case_object_store_quota(
        self,
    ) -> tuple[str, ObjectStoreQuota, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        service = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        item1 = ObjectStoreQuota().save()
        item2 = ObjectStoreQuota(per_user=True).save()
        provider.projects.connect(project)
        project.quotas.connect(item1)
        project.quotas.connect(item2)
        provider.regions.connect(region)
        region.services.connect(service)
        service.quotas.connect(item1)
        service.quotas.connect(item2)
        return "object_store_quotas", item1

    def case_region(self) -> tuple[str, Region, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        item1 = Region(name=random_lower_string()).save()
        item2 = Region(name=random_lower_string()).save()
        provider.regions.connect(item1)
        provider.regions.connect(item2)
        return "regions", item1

    def case_block_storage_service(
        self,
    ) -> tuple[str, BlockStorageService, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        item1 = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        item2 = BlockStorageService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
        ).save()
        provider.regions.connect(region)
        region.services.connect(item1)
        region.services.connect(item2)
        return "block_storage_services", item1

    def case_compute_service(self) -> tuple[str, ComputeService, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        item1 = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        item2 = ComputeService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
        ).save()
        provider.regions.connect(region)
        region.services.connect(item1)
        region.services.connect(item2)
        return "compute_services", item1

    def case_identity_service(self) -> tuple[str, IdentityService, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        item1 = IdentityService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
        ).save()
        item2 = IdentityService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
        ).save()
        provider.regions.connect(region)
        region.services.connect(item1)
        region.services.connect(item2)
        return "identity_services", item1

    def case_network_service(self) -> tuple[str, NetworkService, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        item1 = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        item2 = NetworkService(
            endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
        ).save()
        provider.regions.connect(region)
        region.services.connect(item1)
        region.services.connect(item2)
        return "network_services", item1

    def case_object_store_service(
        self,
    ) -> tuple[str, ObjectStoreService, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        region = Region(name=random_lower_string()).save()
        item1 = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        item2 = ObjectStoreService(
            endpoint=str(random_url()),
            name=random_service_name(ServiceType.OBJECT_STORE),
        ).save()
        provider.regions.connect(region)
        region.services.connect(item1)
        region.services.connect(item2)
        return "object_store_services", item1

    def case_sla(self) -> tuple[str, SLA, dict[str, Any]]:
        provider = Provider(
            name=random_lower_string(), type=random_provider_type()
        ).save()
        project1 = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        project2 = Project(name=random_lower_string(), uuid=str(uuid4())).save()

        idp = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        user_group1 = UserGroup(name=random_lower_string()).save()
        user_group2 = UserGroup(name=random_lower_string()).save()

        start_date, end_date = random_start_end_dates()
        item1 = SLA(
            doc_uuid=str(uuid4()), start_date=start_date, end_date=end_date
        ).save()
        item2 = SLA(
            doc_uuid=str(uuid4()), start_date=start_date, end_date=end_date
        ).save()
        provider.identity_providers.connect(
            idp, {"idp_name": random_lower_string(), "protocol": random_lower_string()}
        )
        provider.projects.connect(project1)
        provider.projects.connect(project2)
        idp.user_groups.connect(user_group1)
        idp.user_groups.connect(user_group2)
        user_group1.slas.connect(item1)
        user_group2.slas.connect(item2)
        project1.sla.connect(item1)
        project2.sla.connect(item2)
        return "slas", item1

    def case_user_group(self) -> tuple[str, UserGroup, dict[str, Any]]:
        idp = IdentityProvider(
            endpoint=random_url(), group_claim=random_lower_string()
        ).save()
        item1 = UserGroup(name=random_lower_string()).save()
        item2 = UserGroup(name=random_lower_string()).save()
        idp.user_groups.connect(item1)
        idp.user_groups.connect(item2)
        return "user_groups", item1


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


class CaseWithConn:
    def case_with_conn(self) -> Literal[True]:
        return True

    def case_without_conn(self) -> Literal[False]:
        return False


class CaseShrunk:
    def case_shrunk(self) -> Literal[True]:
        return True

    def case_standard(self) -> Literal[False]:
        return False


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="valid")
@parametrize_with_cases("endpoint, item", cases=CaseItem)
@parametrize_with_cases("with_conn", cases=CaseWithConn)
@parametrize_with_cases("shrunk", cases=CaseShrunk)
def test_get_multi(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Any,
    with_conn: bool,
    shrunk: bool,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_with_token.get(url, params={"short": shrunk, "with_conn": with_conn})
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) == 2
    data = data[0]

    if with_conn and shrunk:
        assert data["schema_type"] == "public_extended"
    elif not with_conn and shrunk:
        assert data["schema_type"] == "public"
    elif with_conn and not shrunk:
        assert data["schema_type"] == "private_extended"
    else:
        assert data["schema_type"] == "private"


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("user_infos", cases=CaseUserInfos, has_tag="valid")
@parametrize_with_cases("endpoint, item", cases=CaseItem)
@parametrize_with_cases("with_conn", cases=CaseWithConn)
@parametrize_with_cases("shrunk", cases=CaseShrunk)
def test_get_single(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
    item: Any,
    with_conn: bool,
    shrunk: bool,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, item.uid)
    resp = client_with_token.get(url, params={"short": shrunk, "with_conn": with_conn})
    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    assert data is not None

    if with_conn and shrunk:
        assert data["schema_type"] == "public_extended"
    elif not with_conn and shrunk:
        assert data["schema_type"] == "public"
    elif with_conn and not shrunk:
        assert data["schema_type"] == "private_extended"
    else:
        assert data["schema_type"] == "private"
