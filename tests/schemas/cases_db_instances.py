from pytest_cases import case, parametrize

from fed_reg.flavor.models import Flavor
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.image.models import Image
from fed_reg.location.models import Location
from fed_reg.network.models import Network
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.quota.models import BlockStorageQuota, ComputeQuota, NetworkQuota
from fed_reg.region.models import Region
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
)
from fed_reg.sla.models import SLA
from fed_reg.user_group.models import UserGroup
from tests.create_dict import (
    auth_method_dict,
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


class CasePublic:
    @parametrize(is_public=[True, False])
    def case_public(self, is_public: bool):
        return is_public


class CaseDBInstance:
    @case(tags=["provider"])
    @parametrize(tot=[0, 1, 2])
    def case_projects(self, provider_model: Provider, tot: int) -> Provider:
        for _ in range(tot):
            p = Project(**project_model_dict()).save()
            provider_model.projects.connect(p)
        return provider_model

    @case(tags=["provider"])
    @parametrize(tot=[0, 1, 2])
    def case_provider_regions(self, provider_model: Provider, tot: int) -> Provider:
        for _ in range(tot):
            p = Region(**region_model_dict()).save()
            provider_model.regions.connect(p)
        return provider_model

    @case(tags=["provider"])
    @parametrize(tot=[0, 1, 2])
    def case_identity_providers(self, provider_model: Provider, tot: int) -> Provider:
        for _ in range(tot):
            p = IdentityProvider(**identity_provider_model_dict()).save()
            provider_model.identity_providers.connect(p, auth_method_dict())
        return provider_model

    @case(tags=["region"])
    @parametrize(has_loc=[False, True])
    def case_location(self, region_model: Region, has_loc: bool) -> Region:
        p = Provider(**provider_model_dict()).save()
        region_model.provider.connect(p)
        if has_loc:
            item = Location(**location_model_dict()).save()
            region_model.location.connect(item)
        return region_model

    @case(tags=["region"])
    @parametrize(tot=[0, 1, 2])
    def case_block_storage_services(
        self, provider_model: Provider, region_model: Region, tot: int
    ) -> Region:
        region_model.provider.connect(provider_model)
        for _ in range(tot):
            item = BlockStorageService(**service_model_dict()).save()
            region_model.services.connect(item)
        return region_model

    @case(tags=["region"])
    @parametrize(tot=[0, 1, 2])
    def case_compute_services(
        self, provider_model: Provider, region_model: Region, tot: int
    ) -> Region:
        region_model.provider.connect(provider_model)
        for _ in range(tot):
            item = ComputeService(**service_model_dict()).save()
            region_model.services.connect(item)
        return region_model

    @case(tags=["region"])
    @parametrize(tot=[0, 1, 2])
    def case_identity_services(
        self, provider_model: Provider, region_model: Region, tot: int
    ) -> Region:
        region_model.provider.connect(provider_model)
        for _ in range(tot):
            item = IdentityService(**service_model_dict()).save()
            region_model.services.connect(item)
        return region_model

    @case(tags=["region"])
    @parametrize(tot=[0, 1, 2])
    def case_network_services(
        self, provider_model: Provider, region_model: Region, tot: int
    ) -> Region:
        region_model.provider.connect(provider_model)
        for _ in range(tot):
            item = NetworkService(**service_model_dict()).save()
            region_model.services.connect(item)
        return region_model

    @case(tags=["region"])
    def case_mixed_srv(self, provider_model: Provider, region_model: Region) -> Region:
        p = Provider(**provider_model_dict()).save()
        region_model.provider.connect(p)
        item = BlockStorageService(**service_model_dict()).save()
        region_model.services.connect(item)
        item = ComputeService(**service_model_dict()).save()
        region_model.services.connect(item)
        item = IdentityService(**service_model_dict()).save()
        region_model.services.connect(item)
        item = NetworkService(**service_model_dict()).save()
        region_model.services.connect(item)
        return region_model

    @case(tags=["identity_provider"])
    @parametrize(tot=[0, 1, 2])
    def case_user_groups(
        self,
        provider_model: Provider,
        identity_provider_model: IdentityProvider,
        tot: int,
    ) -> Provider:
        provider_model.identity_providers.connect(
            identity_provider_model, auth_method_dict()
        )
        for _ in range(tot):
            item = UserGroup(**user_group_model_dict()).save()
            identity_provider_model.user_groups.connect(item)
        return provider_model

    @case(tags=["user_group"])
    @parametrize(tot=[0, 1, 2])
    def case_slas(
        self,
        provider_model: Provider,
        identity_provider_model: IdentityProvider,
        user_group_model: UserGroup,
        tot: int,
    ) -> UserGroup:
        provider_model.identity_providers.connect(
            identity_provider_model, auth_method_dict()
        )
        identity_provider_model.user_groups.connect(user_group_model)
        for _ in range(tot):
            item = SLA(**sla_model_dict()).save()
            user_group_model.slas.connect(item)
        return user_group_model

    @case(tags=["block_storage_service"])
    @parametrize(tot=[0, 1, 2])
    def case_block_storage_quotas(
        self,
        provider_model: Provider,
        region_model: Region,
        block_storage_service_model: BlockStorageService,
        tot: int,
    ) -> Region:
        region_model.provider.connect(provider_model)
        block_storage_service_model.regions.connect(region_model)
        for _ in range(tot):
            item = BlockStorageQuota(**quota_model_dict()).save()
            block_storage_service_model.quotas.connect(item)
        return block_storage_service_model

    @case(tags=["compute_service"])
    @parametrize(tot=[0, 1, 2])
    def case_flavors(
        self,
        provider_model: Provider,
        region_model: Region,
        compute_service_model: ComputeService,
        tot: int,
    ) -> Region:
        region_model.provider.connect(provider_model)
        compute_service_model.regions.connect(region_model)
        for _ in range(tot):
            item = Flavor(**flavor_model_dict()).save()
            compute_service_model.flavors.connect(item)
        return compute_service_model

    @case(tags=["compute_service"])
    @parametrize(tot=[0, 1, 2])
    def case_images(
        self,
        provider_model: Provider,
        region_model: Region,
        compute_service_model: ComputeService,
        tot: int,
    ) -> Region:
        region_model.provider.connect(provider_model)
        compute_service_model.regions.connect(region_model)
        for _ in range(tot):
            item = Image(**image_model_dict()).save()
            compute_service_model.images.connect(item)
        return compute_service_model

    @case(tags=["compute_service"])
    @parametrize(tot=[0, 1, 2])
    def case_compute_quotas(
        self,
        provider_model: Provider,
        region_model: Region,
        compute_service_model: ComputeService,
        tot: int,
    ) -> Region:
        region_model.provider.connect(provider_model)
        compute_service_model.regions.connect(region_model)
        for _ in range(tot):
            item = ComputeQuota(**quota_model_dict()).save()
            compute_service_model.quotas.connect(item)
        return compute_service_model

    @case(tags=["network_service"])
    @parametrize(tot=[0, 1, 2])
    def case_network_quotas(
        self,
        provider_model: Provider,
        region_model: Region,
        network_service_model: NetworkService,
        tot: int,
    ) -> Region:
        region_model.provider.connect(provider_model)
        network_service_model.regions.connect(region_model)
        for _ in range(tot):
            item = NetworkQuota(**quota_model_dict()).save()
            network_service_model.quotas.connect(item)
        return network_service_model

    @case(tags=["network_service"])
    @parametrize(tot=[0, 1, 2])
    def case_networks(
        self,
        provider_model: Provider,
        region_model: Region,
        network_service_model: NetworkService,
        tot: int,
    ) -> Region:
        region_model.provider.connect(provider_model)
        network_service_model.regions.connect(region_model)
        for _ in range(tot):
            item = Network(**network_model_dict()).save()
            network_service_model.networks.connect(item)
        return network_service_model

    @case(tags=["location"])
    @parametrize(tot=[1, 2])
    def case_location_regions(self, location_model: Location, tot: int) -> Location:
        for _ in range(tot):
            item = Region(**region_model_dict()).save()
            location_model.regions.connect(item)
        return location_model

    @case(tags=["project"])
    @parametrize(**{"tot,pub": [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)]})
    def case_project_flavors(
        self,
        project_model: Project,
        provider_model: Provider,
        compute_quota_model: ComputeQuota,
        compute_service_model: ComputeService,
        region_model: Region,
        tot: int,
        pub: int,
    ) -> Project:
        project_model.provider.connect(provider_model)
        for _ in range(pub):
            item = Flavor(**flavor_model_dict()).save()
            compute_service_model.flavors.connect(item)
        compute_service_model.quotas.connect(compute_quota_model)
        compute_service_model.regions.connect(region_model)
        project_model.quotas.connect(compute_quota_model)
        for _ in range(tot - pub):
            item = Flavor(**flavor_model_dict(), is_public=False).save()
            project_model.private_flavors.connect(item)
        return project_model

    @case(tags=["project"])
    @parametrize(**{"tot,pub": [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)]})
    def case_project_images(
        self,
        project_model: Project,
        provider_model: Provider,
        compute_quota_model: ComputeQuota,
        compute_service_model: ComputeService,
        region_model: Region,
        tot: int,
        pub: int,
    ) -> Project:
        project_model.provider.connect(provider_model)
        for _ in range(pub):
            item = Image(**image_model_dict()).save()
            compute_service_model.images.connect(item)
        compute_service_model.quotas.connect(compute_quota_model)
        compute_service_model.regions.connect(region_model)
        project_model.quotas.connect(compute_quota_model)
        for _ in range(tot - pub):
            item = Image(**image_model_dict(), is_public=False).save()
            project_model.private_images.connect(item)
        return project_model

    @case(tags=["project"])
    @parametrize(**{"tot,pub": [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (2, 2)]})
    def case_project_networks(
        self,
        project_model: Project,
        provider_model: Provider,
        network_quota_model: NetworkQuota,
        network_service_model: NetworkService,
        region_model: Region,
        tot: int,
        pub: int,
    ) -> Project:
        project_model.provider.connect(provider_model)
        for _ in range(pub):
            item = Network(**network_model_dict()).save()
            network_service_model.networks.connect(item)
        network_service_model.quotas.connect(network_quota_model)
        network_service_model.regions.connect(region_model)
        project_model.quotas.connect(network_quota_model)
        for _ in range(tot - pub):
            item = Network(**network_model_dict(), is_shared=False).save()
            project_model.private_networks.connect(item)
        return project_model

    @case(tags=["project"])
    def case_project_slas(
        self,
        project_model: Project,
        provider_model: Provider,
        identity_provider_model: IdentityProvider,
        user_group_model: UserGroup,
        sla_model: SLA,
    ) -> Project:
        project_model.provider.connect(provider_model)
        identity_provider_model.user_groups.connect(user_group_model)
        user_group_model.slas.connect(sla_model)
        project_model.sla.connect(sla_model)
        return project_model
