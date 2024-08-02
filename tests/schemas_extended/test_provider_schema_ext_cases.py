from typing import Literal
from uuid import uuid4

from pytest_cases import case, parametrize

from fed_reg.project.schemas import ProjectCreate
from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    BlockStorageServiceCreateExtended,
    ComputeQuotaCreateExtended,
    ComputeServiceCreateExtended,
    IdentityProviderCreateExtended,
    NetworkCreateExtended,
    NetworkQuotaCreateExtended,
    NetworkServiceCreateExtended,
    ObjectStoreQuotaCreateExtended,
    ObjectStoreServiceCreateExtended,
    PrivateFlavorCreateExtended,
    PrivateImageCreateExtended,
    RegionCreateExtended,
    SLACreateExtended,
)
from tests.create_dict import (
    flavor_schema_dict,
    image_schema_dict,
    network_schema_dict,
    project_schema_dict,
    region_schema_dict,
    sla_schema_dict,
)
from tests.utils import random_lower_string, random_url


class CaseAttr:
    @case(tags=["valid"])
    @parametrize(len=(0, 1, 2))
    def case_projects(
        self, len: int
    ) -> tuple[Literal["projects"], list[ProjectCreate]]:
        return "projects", [ProjectCreate(**project_schema_dict()) for _ in range(len)]

    @case(tags=["valid"])
    @parametrize(len=(0, 1, 2))
    def case_regions(
        self, len: int
    ) -> tuple[Literal["regions"], list[RegionCreateExtended]]:
        return "regions", [
            RegionCreateExtended(**region_schema_dict()) for _ in range(len)
        ]

    @case(tags=["valid"])
    @parametrize(len=(0, 1, 2))
    def case_identity_providers(
        self,
        identity_provider_create_ext_schema: IdentityProviderCreateExtended,
        len: int,
    ) -> tuple[Literal["identity_providers"], list[IdentityProviderCreateExtended]]:
        if len == 1:
            return "identity_providers", [identity_provider_create_ext_schema]
        elif len == 2:
            idp2 = identity_provider_create_ext_schema.copy()
            user_group = idp2.user_groups[0].copy()
            user_group.sla = SLACreateExtended(**sla_schema_dict(), project=uuid4())
            idp2.user_groups = [user_group]
            idp2.endpoint = random_url()
            return "identity_providers", [identity_provider_create_ext_schema, idp2]
        else:
            return "identity_providers", []

    @case(tags=["invalid"])
    @parametrize(attr=("name", "uuid"))
    def case_dup_projects(
        self, attr: str
    ) -> tuple[Literal["projects"], list[ProjectCreate], str]:
        project = ProjectCreate(**project_schema_dict())
        project2 = project.copy()
        if attr == "name":
            project2.uuid = uuid4()
        else:
            project2.name = random_lower_string()
        return (
            "projects",
            [project, project2],
            f"There are multiple items with identical {attr}",
        )

    @case(tags=["invalid"])
    def case_dup_regions(
        self,
    ) -> tuple[Literal["regions"], list[RegionCreateExtended], str]:
        region = RegionCreateExtended(**region_schema_dict())
        return (
            "regions",
            [region, region],
            "There are multiple items with identical name",
        )

    @case(tags=["invalid"])
    def case_dup_idps(
        self, identity_provider_create_ext_schema: IdentityProviderCreateExtended
    ) -> tuple[
        Literal["identity_providers"], list[IdentityProviderCreateExtended], str
    ]:
        return (
            "identity_providers",
            [identity_provider_create_ext_schema, identity_provider_create_ext_schema],
            "There are multiple items with identical endpoint",
        )

    @case(tags=["idps"])
    def case_dup_sla_in_multi_idps(
        self, identity_provider_create_ext_schema: IdentityProviderCreateExtended
    ) -> tuple[Literal["identity_providers"], list[ProjectCreate]]:
        idp2 = identity_provider_create_ext_schema.copy()
        idp2.endpoint = random_url()
        return (
            [identity_provider_create_ext_schema, idp2],
            "already used by another user group",
        )

    @case(tags=["idps"])
    def case_dup_project_in_multi_idps(
        self, identity_provider_create_ext_schema: IdentityProviderCreateExtended
    ) -> tuple[Literal["identity_providers"], list[ProjectCreate]]:
        idp2 = identity_provider_create_ext_schema.copy()
        user_group = idp2.user_groups[0].copy()
        sla = user_group.sla.copy()
        sla.doc_uuid = uuid4()
        user_group.sla = sla
        idp2.user_groups = [user_group]
        idp2.endpoint = random_url()
        return (
            [identity_provider_create_ext_schema, idp2],
            "already used by another SLA",
        )

    @case(tags=["missing"])
    def case_missing_idp_projects(
        self,
        identity_provider_create_ext_schema: IdentityProviderCreateExtended,
    ) -> tuple[
        str,
        list[IdentityProviderCreateExtended] | list[RegionCreateExtended],
        Literal["not in this provider"],
    ]:
        return (
            "identity_providers",
            [identity_provider_create_ext_schema],
            "not in this provider",
        )

    @case(tags=["missing"])
    def case_missing_block_storage_projects(
        self,
        region_create_ext_schema: RegionCreateExtended,
        block_storage_service_create_ext_schema: BlockStorageServiceCreateExtended,
        block_storage_quota_create_ext_schema: BlockStorageQuotaCreateExtended,
    ) -> tuple[
        str,
        list[IdentityProviderCreateExtended] | list[RegionCreateExtended],
        Literal["not in this provider"],
    ]:
        block_storage_service_create_ext_schema.quotas = [
            block_storage_quota_create_ext_schema
        ]
        region_create_ext_schema.block_storage_services = [
            block_storage_service_create_ext_schema
        ]
        return ("regions", [region_create_ext_schema], "not in this provider")

    @case(tags=["missing"])
    @parametrize(resource=("quotas", "flavors", "images"))
    def case_missing_compute_projects(
        self,
        region_create_ext_schema: RegionCreateExtended,
        compute_service_create_ext_schema: ComputeServiceCreateExtended,
        compute_quota_create_ext_schema: ComputeQuotaCreateExtended,
        resource: str,
    ) -> tuple[
        str,
        list[IdentityProviderCreateExtended] | list[RegionCreateExtended],
        Literal["not in this provider"],
    ]:
        if resource == "quotas":
            compute_service_create_ext_schema.quotas = [compute_quota_create_ext_schema]
        elif resource == "flavors":
            item = PrivateFlavorCreateExtended(
                **flavor_schema_dict(), is_public=False, projects=[uuid4()]
            )
            compute_service_create_ext_schema.flavors = [item]
        elif resource == "images":
            item = PrivateImageCreateExtended(
                **image_schema_dict(), is_public=False, projects=[uuid4()]
            )
            compute_service_create_ext_schema.images = [item]
        region_create_ext_schema.compute_services = [compute_service_create_ext_schema]
        return ("regions", [region_create_ext_schema], "not in this provider")

    @case(tags=["missing"])
    @parametrize(resource=("quotas", "networks"))
    def case_missing_network_projects(
        self,
        region_create_ext_schema: RegionCreateExtended,
        network_service_create_ext_schema: NetworkServiceCreateExtended,
        network_quota_create_ext_schema: NetworkQuotaCreateExtended,
        resource: str,
    ) -> tuple[
        str,
        list[IdentityProviderCreateExtended] | list[RegionCreateExtended],
        Literal["not in this provider"],
    ]:
        if resource == "quotas":
            network_service_create_ext_schema.quotas = [network_quota_create_ext_schema]
        elif resource == "networks":
            item = NetworkCreateExtended(
                **network_schema_dict(), is_shared=False, project=uuid4()
            )
            network_service_create_ext_schema.networks = [item]
        region_create_ext_schema.network_services = [network_service_create_ext_schema]
        return ("regions", [region_create_ext_schema], "not in this provider")

    @case(tags=["missing"])
    def case_missing_object_store_projects(
        self,
        region_create_ext_schema: RegionCreateExtended,
        object_store_service_create_ext_schema: ObjectStoreServiceCreateExtended,
        object_store_quota_create_ext_schema: ObjectStoreQuotaCreateExtended,
    ) -> tuple[
        str,
        list[IdentityProviderCreateExtended] | list[RegionCreateExtended],
        Literal["not in this provider"],
    ]:
        object_store_service_create_ext_schema.quotas = [
            object_store_quota_create_ext_schema
        ]
        region_create_ext_schema.object_store_services = [
            object_store_service_create_ext_schema
        ]
        return ("regions", [region_create_ext_schema], "not in this provider")
