from datetime import date
from random import randint
from typing import Literal

from pytest_cases import parametrize

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
)
from fed_reg.region.models import Region
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    NetworkService,
    ObjectStoreService,
)
from fed_reg.sla.models import SLA
from fed_reg.user_group.models import UserGroup
from tests.create_dict import (
    block_storage_quota_model_dict,
    block_storage_service_model_dict,
    compute_quota_model_dict,
    compute_service_model_dict,
    flavor_model_dict,
    identity_provider_model_dict,
    image_model_dict,
    location_model_dict,
    network_model_dict,
    network_quota_model_dict,
    network_service_model_dict,
    object_store_quota_model_dict,
    object_store_service_model_dict,
    project_model_dict,
    provider_model_dict,
    region_model_dict,
    sla_model_dict,
    user_group_model_dict,
)
from tests.utils import random_date, random_float, random_lower_string


class CaseFlavor:
    @parametrize(
        attr=["description", "name", "uuid", "gpu_model", "gpu_vendor", "local_storage"]
    )
    def case_flavor_str(self, attr: str) -> tuple[dict, type[Flavor], str, str]:
        return flavor_model_dict(), Flavor, attr, random_lower_string()

    @parametrize(attr=["disk", "ram", "vcpus", "swap", "ephemeral", "gpus"])
    def case_flavor_int(self, attr: str) -> tuple[dict, type[Flavor], str, int]:
        return flavor_model_dict(), Flavor, attr, randint(0, 100)

    @parametrize(attr=["infiniband"])
    def case_flavor_bool(
        self, attr: str
    ) -> tuple[dict, type[Flavor], str, Literal[True]]:
        return flavor_model_dict(), Flavor, attr, True

    @parametrize(attr=["is_public"])
    def case_public_flavor_bool(
        self, attr: str
    ) -> tuple[dict, type[SharedFlavor], str, Literal[False]]:
        return flavor_model_dict(), SharedFlavor, attr, False

    @parametrize(attr=["is_public"])
    def case_private_flavor_bool(
        self, attr: str
    ) -> tuple[dict, type[PrivateFlavor], str, Literal[True]]:
        return flavor_model_dict(), PrivateFlavor, attr, True


class CaseIdentityProvider:
    @parametrize(attr=["description", "endpoint", "group_claim"])
    def case_identity_provider_str(
        self, attr: str
    ) -> tuple[dict, type[IdentityProvider], str, str]:
        return (
            identity_provider_model_dict(),
            IdentityProvider,
            attr,
            random_lower_string(),
        )


class CaseImage:
    @parametrize(
        attr=[
            "description",
            "name",
            "uuid",
            "os_type",
            "os_distro",
            "os_version",
            "architecture",
            "kernel_id",
        ]
    )
    def case_image_str(self, attr: str) -> tuple[dict, type[Image], str, str]:
        return image_model_dict(), Image, attr, random_lower_string()

    @parametrize(attr=["cuda_support", "gpu_driver"])
    def case_image_bool(
        self, attr: str
    ) -> tuple[dict, type[Image], str, Literal[True]]:
        return image_model_dict(), Image, attr, True

    @parametrize(attr=["tags"])
    @parametrize(fill=[True, False])
    def case_image_list_str(
        self, attr: str, fill: bool
    ) -> tuple[dict, type[Image], str, list[str]]:
        values = [] if not fill else [random_lower_string()]
        return image_model_dict(), Image, attr, values

    @parametrize(attr=["is_public"])
    def case_public_image_bool(
        self, attr: str
    ) -> tuple[dict, type[SharedImage], str, Literal[False]]:
        return image_model_dict(), SharedImage, attr, False

    @parametrize(attr=["is_public"])
    def case_private_image_bool(
        self, attr: str
    ) -> tuple[dict, type[PrivateImage], str, Literal[True]]:
        return image_model_dict(), PrivateImage, attr, True


class CaseLocation:
    @parametrize(attr=["description", "site", "country"])
    def case_location_str(self, attr: str) -> tuple[dict, type[Location], str, str]:
        return location_model_dict(), Location, attr, random_lower_string()

    @parametrize(attr=["latitude", "longitude"])
    def case_location_float(self, attr: str) -> tuple[dict, type[Location], str, float]:
        return location_model_dict(), Location, attr, random_float(0, 100)


class CaseNetwork:
    @parametrize(attr=["description", "name", "uuid", "proxy_host", "proxy_user"])
    def case_network_str(self, attr: str) -> tuple[dict, type[Network], str, str]:
        return network_model_dict(), Network, attr, random_lower_string()

    @parametrize(attr=["mtu"])
    def case_network_int(self, attr: str) -> tuple[dict, type[Network], str, int]:
        return network_model_dict(), Network, attr, randint(0, 100)

    @parametrize(attr=["is_router_external", "is_default"])
    def case_network_bool(
        self, attr: str
    ) -> tuple[dict, type[Network], str, Literal[True]]:
        return network_model_dict(), Network, attr, True

    @parametrize(attr=["is_shared"])
    def case_shared_network_bool(
        self, attr: str
    ) -> tuple[dict, type[SharedNetwork], str, Literal[False]]:
        return network_model_dict(), SharedNetwork, attr, False

    @parametrize(attr=["is_shared"])
    def case_private_network_bool(
        self, attr: str
    ) -> tuple[dict, type[PrivateNetwork], str, Literal[True]]:
        return network_model_dict(), PrivateNetwork, attr, True

    @parametrize(attr=["tags"])
    @parametrize(fill=[True, False])
    def case_network_list_str(
        self, attr: str, fill: bool
    ) -> tuple[dict, type[Network], str, list[str]]:
        values = [] if not fill else [random_lower_string()]
        return network_model_dict(), Network, attr, values


class CaseProject:
    @parametrize(attr=["description", "name", "uuid"])
    def case_project_str(self, attr: str) -> tuple[dict, type[Project], str, str]:
        return project_model_dict(), Project, attr, random_lower_string()


class CaseProvider:
    @parametrize(attr=["description", "name", "type", "status"])
    def case_provider_str(self, attr: str) -> tuple[dict, type[Provider], str, str]:
        return provider_model_dict(), Provider, attr, random_lower_string()

    @parametrize(attr=["is_public"])
    def case_provider_bool(
        self, attr: str
    ) -> tuple[dict, type[Provider], str, Literal[True]]:
        return provider_model_dict(), Provider, attr, True

    @parametrize(attr=["tags"])
    @parametrize(fill=[True, False])
    def case_provider_list_str(
        self, attr: str, fill: bool
    ) -> tuple[dict, type[Provider], str, list[str]]:
        values = [] if not fill else [random_lower_string()]
        return provider_model_dict(), Provider, attr, values


class CaseBlockStorageQuota:
    @parametrize(attr=["description", "type"])
    def case_block_storage_quota_str(
        self, attr: str
    ) -> tuple[dict, type[BlockStorageQuota], str, str]:
        return (
            block_storage_quota_model_dict(),
            BlockStorageQuota,
            attr,
            random_lower_string(),
        )

    @parametrize(attr=["gigabytes", "volumes", "per_volume_gigabytes"])
    def case_block_storage_quota_int(
        self, attr: str
    ) -> tuple[dict, type[BlockStorageQuota], str, int]:
        return (
            block_storage_quota_model_dict(),
            BlockStorageQuota,
            attr,
            randint(0, 100),
        )


class CaseComputeQuota:
    @parametrize(attr=["description", "type"])
    def case_compute_quota_str(
        self, attr: str
    ) -> tuple[dict, type[ComputeQuota], str, str]:
        return compute_quota_model_dict(), ComputeQuota, attr, random_lower_string()

    @parametrize(attr=["cores", "instances", "ram"])
    def case_compute_quota_int(
        self, attr: str
    ) -> tuple[dict, type[ComputeQuota], str, int]:
        return compute_quota_model_dict(), ComputeQuota, attr, randint(0, 100)


class CaseNetworkQuota:
    @parametrize(attr=["description", "type"])
    def case_network_quota_str(
        self, attr: str
    ) -> tuple[dict, type[NetworkQuota], str, str]:
        return network_quota_model_dict(), NetworkQuota, attr, random_lower_string()

    @parametrize(
        attr=[
            "public_ips",
            "networks",
            "ports",
            "security_groups",
            "security_group_rules",
        ]
    )
    def case_network_quota_int(
        self, attr: str
    ) -> tuple[dict, type[NetworkQuota], str, int]:
        return network_quota_model_dict(), NetworkQuota, attr, randint(0, 100)


class CaseObjectStoreQuota:
    @parametrize(attr=["description", "type"])
    def case_object_store_quota_str(
        self, attr: str
    ) -> tuple[dict, type[ObjectStoreQuota], str, str]:
        return (
            object_store_quota_model_dict(),
            ObjectStoreQuota,
            attr,
            random_lower_string(),
        )

    # TODO: understand attributes


class CaseRegion:
    @parametrize(attr=["description", "name"])
    def case_region_str(self, attr: str) -> tuple[dict, type[Region], str, str]:
        return region_model_dict(), Region, attr, random_lower_string()


class CaseBlockStorageService:
    @parametrize(attr=["description", "type", "name", "endpoint"])
    def case_block_storage_service_str(
        self, attr: str
    ) -> tuple[dict, type[BlockStorageService], str, str]:
        return (
            block_storage_service_model_dict(),
            BlockStorageService,
            attr,
            random_lower_string(),
        )


class CaseComputeService:
    @parametrize(attr=["description", "type", "name", "endpoint"])
    def case_compute_service_str(
        self, attr: str
    ) -> tuple[dict, type[ComputeService], str, str]:
        return compute_service_model_dict(), ComputeService, attr, random_lower_string()


class CaseNetworkService:
    @parametrize(attr=["description", "type", "name", "endpoint"])
    def case_network_service_str(
        self, attr: str
    ) -> tuple[dict, type[NetworkService], str, str]:
        return network_service_model_dict(), NetworkService, attr, random_lower_string()


class CaseObjectStoreService:
    @parametrize(attr=["description", "type", "name", "endpoint"])
    def case_object_store_service_str(
        self, attr: str
    ) -> tuple[dict, type[ObjectStoreService], str, str]:
        return (
            object_store_service_model_dict(),
            ObjectStoreService,
            attr,
            random_lower_string(),
        )


class CaseSLA:
    @parametrize(attr=["description", "doc_uuid"])
    def case_sla_str(self, attr: str) -> tuple[dict, type[SLA], str, str]:
        return sla_model_dict(), SLA, attr, random_lower_string()

    @parametrize(attr=["start_date", "end_date"])
    def case_sla_date(self, attr: str) -> tuple[dict, type[SLA], str, date]:
        return sla_model_dict(), SLA, attr, random_date()


class CaseUserGroup:
    @parametrize(attr=["description", "name"])
    def case_user_group_str(self, attr: str) -> tuple[dict, type[UserGroup], str, str]:
        return user_group_model_dict(), UserGroup, attr, random_lower_string()
