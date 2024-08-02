from pytest_cases import case

from fed_reg.flavor.schemas import (
    FlavorBase,
    FlavorBasePublic,
    FlavorQuery,
    FlavorRead,
    FlavorReadPublic,
    FlavorUpdate,
    PrivateFlavorCreate,
    SharedFlavorCreate,
)
from fed_reg.identity_provider.schemas import (
    IdentityProviderBase,
    IdentityProviderBasePublic,
    IdentityProviderCreate,
    IdentityProviderQuery,
    IdentityProviderRead,
    IdentityProviderReadPublic,
    IdentityProviderUpdate,
)
from fed_reg.image.schemas import (
    ImageBase,
    ImageBasePublic,
    ImageQuery,
    ImageRead,
    ImageReadPublic,
    ImageUpdate,
    PrivateImageCreate,
    SharedImageCreate,
)
from fed_reg.location.schemas import (
    LocationBase,
    LocationBasePublic,
    LocationCreate,
    LocationQuery,
    LocationRead,
    LocationReadPublic,
    LocationUpdate,
)
from fed_reg.network.schemas import (
    NetworkBase,
    NetworkBasePublic,
    NetworkQuery,
    NetworkRead,
    NetworkReadPublic,
    NetworkUpdate,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from fed_reg.project.schemas import (
    ProjectBase,
    ProjectBasePublic,
    ProjectCreate,
    ProjectQuery,
    ProjectRead,
    ProjectReadPublic,
    ProjectUpdate,
)
from fed_reg.provider.schemas import (
    ProviderBase,
    ProviderBasePublic,
    ProviderCreate,
    ProviderQuery,
    ProviderRead,
    ProviderReadPublic,
    ProviderUpdate,
)
from fed_reg.quota.schemas import (
    BlockStorageQuotaBase,
    BlockStorageQuotaBasePublic,
    BlockStorageQuotaCreate,
    BlockStorageQuotaQuery,
    BlockStorageQuotaRead,
    BlockStorageQuotaReadPublic,
    BlockStorageQuotaUpdate,
    ComputeQuotaBase,
    ComputeQuotaBasePublic,
    ComputeQuotaCreate,
    ComputeQuotaQuery,
    ComputeQuotaRead,
    ComputeQuotaReadPublic,
    ComputeQuotaUpdate,
    NetworkQuotaBase,
    NetworkQuotaBasePublic,
    NetworkQuotaCreate,
    NetworkQuotaQuery,
    NetworkQuotaRead,
    NetworkQuotaReadPublic,
    NetworkQuotaUpdate,
    ObjectStoreQuotaBase,
    ObjectStoreQuotaBasePublic,
    ObjectStoreQuotaCreate,
    ObjectStoreQuotaQuery,
    ObjectStoreQuotaRead,
    ObjectStoreQuotaReadPublic,
    ObjectStoreQuotaUpdate,
    QuotaBase,
)
from fed_reg.region.schemas import (
    RegionBase,
    RegionBasePublic,
    RegionCreate,
    RegionQuery,
    RegionRead,
    RegionReadPublic,
    RegionUpdate,
)
from fed_reg.service.schemas import (
    BlockStorageServiceBase,
    BlockStorageServiceBasePublic,
    BlockStorageServiceCreate,
    BlockStorageServiceQuery,
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    BlockStorageServiceUpdate,
    ComputeServiceBase,
    ComputeServiceBasePublic,
    ComputeServiceCreate,
    ComputeServiceQuery,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    ComputeServiceUpdate,
    IdentityServiceBase,
    IdentityServiceBasePublic,
    IdentityServiceCreate,
    IdentityServiceQuery,
    IdentityServiceRead,
    IdentityServiceReadPublic,
    IdentityServiceUpdate,
    NetworkServiceBase,
    NetworkServiceBasePublic,
    NetworkServiceCreate,
    NetworkServiceQuery,
    NetworkServiceRead,
    NetworkServiceReadPublic,
    NetworkServiceUpdate,
    ObjectStoreServiceBase,
    ObjectStoreServiceBasePublic,
    ObjectStoreServiceCreate,
    ObjectStoreServiceQuery,
    ObjectStoreServiceRead,
    ObjectStoreServiceReadPublic,
    ObjectStoreServiceUpdate,
    ServiceBase,
)
from fed_reg.sla.schemas import (
    SLABase,
    SLABasePublic,
    SLACreate,
    SLAQuery,
    SLARead,
    SLAReadPublic,
    SLAUpdate,
)
from fed_reg.user_group.schemas import (
    UserGroupBase,
    UserGroupBasePublic,
    UserGroupCreate,
    UserGroupQuery,
    UserGroupRead,
    UserGroupReadPublic,
    UserGroupUpdate,
)


class CaseClassInheritance:
    @case(tags=["base_public"])
    def case_flavor_base_public(self):
        return FlavorBasePublic

    @case(tags=["base_public"])
    def case_identity_provider_base_public(self):
        return IdentityProviderBasePublic

    @case(tags=["base_public"])
    def case_image_base_public(self):
        return ImageBasePublic

    @case(tags=["base_public"])
    def case_location_base_public(self):
        return LocationBasePublic

    @case(tags=["base_public"])
    def case_network_base_public(self):
        return NetworkBasePublic

    @case(tags=["base_public"])
    def case_project_base_public(self):
        return ProjectBasePublic

    @case(tags=["base_public"])
    def case_provider_base_public(self):
        return ProviderBasePublic

    @case(tags=["base_public"])
    def case_quota_base_public(self):
        return QuotaBase

    @case(tags=["base_public"])
    def case_region_base_public(self):
        return RegionBasePublic

    @case(tags=["base_public"])
    def case_service_base_public(self):
        return ServiceBase

    @case(tags=["base_public"])
    def case_sla_base_public(self):
        return SLABasePublic

    @case(tags=["base_public"])
    def case_user_group_base_public(self):
        return UserGroupBasePublic

    @case(tags=["base"])
    def case_flavor_base(self):
        return FlavorBase, FlavorBasePublic

    @case(tags=["base"])
    def case_identity_provider_base(self):
        return IdentityProviderBase, IdentityProviderBasePublic

    @case(tags=["base"])
    def case_image_base(self):
        return ImageBase, ImageBasePublic

    @case(tags=["base"])
    def case_location_base(self):
        return LocationBase, LocationBasePublic

    @case(tags=["base"])
    def case_network_base(self):
        return NetworkBase, NetworkBasePublic

    @case(tags=["base"])
    def case_project_base(self):
        return ProjectBase, ProjectBasePublic

    @case(tags=["base"])
    def case_provider_base(self):
        return ProviderBase, ProviderBasePublic

    @case(tags=["base"])
    def case_block_storage_quota_base_public(self):
        return BlockStorageQuotaBasePublic, QuotaBase

    @case(tags=["base"])
    def case_compute_quota_base_public(self):
        return ComputeQuotaBasePublic, QuotaBase

    @case(tags=["base"])
    def case_network_quota_base_public(self):
        return NetworkQuotaBasePublic, QuotaBase

    @case(tags=["base"])
    def case_object_store_quota_base_public(self):
        return ObjectStoreQuotaBasePublic, QuotaBase

    @case(tags=["base"])
    def case_block_storage_quota_base(self):
        return BlockStorageQuotaBase, BlockStorageQuotaBasePublic

    @case(tags=["base"])
    def case_compute_quota_base(self):
        return ComputeQuotaBase, ComputeQuotaBasePublic

    @case(tags=["base"])
    def case_network_quota_base(self):
        return NetworkQuotaBase, NetworkQuotaBasePublic

    @case(tags=["base"])
    def case_object_store_quota_base(self):
        return ObjectStoreQuotaBase, ObjectStoreQuotaBasePublic

    @case(tags=["base"])
    def case_region_base(self):
        return RegionBase, RegionBasePublic

    @case(tags=["base"])
    def case_block_storage_service_base_public(self):
        return BlockStorageServiceBasePublic, ServiceBase

    @case(tags=["base"])
    def case_compute_service_base_public(self):
        return ComputeServiceBasePublic, ServiceBase

    @case(tags=["base"])
    def case_identity_service_base_public(self):
        return IdentityServiceBasePublic, ServiceBase

    @case(tags=["base"])
    def case_network_service_base_public(self):
        return NetworkServiceBasePublic, ServiceBase

    @case(tags=["base"])
    def case_object_store_service_base_public(self):
        return ObjectStoreServiceBasePublic, ServiceBase

    @case(tags=["base"])
    def case_block_storage_service_base(self):
        return BlockStorageServiceBase, BlockStorageServiceBasePublic

    @case(tags=["base"])
    def case_compute_service_base(self):
        return ComputeServiceBase, ComputeServiceBasePublic

    @case(tags=["base"])
    def case_identity_service_base(self):
        return IdentityServiceBase, IdentityServiceBasePublic

    @case(tags=["base"])
    def case_network_service_base(self):
        return NetworkServiceBase, NetworkServiceBasePublic

    @case(tags=["base"])
    def case_object_store_service_base(self):
        return ObjectStoreServiceBase, ObjectStoreServiceBasePublic

    @case(tags=["base"])
    def case_sla_base(self):
        return SLABase, SLABasePublic

    @case(tags=["base"])
    def case_user_group_base(self):
        return UserGroupBase, UserGroupBasePublic

    @case(tags=["create"])
    def case_private_flavor_create(self):
        return PrivateFlavorCreate, FlavorBase

    @case(tags=["create"])
    def case_shared_flavor_create(self):
        return SharedFlavorCreate, FlavorBase

    @case(tags=["create"])
    def case_identity_provider_create(self):
        return IdentityProviderCreate, IdentityProviderBase

    @case(tags=["create"])
    def case_private_image_create(self):
        return PrivateImageCreate, ImageBase

    @case(tags=["create"])
    def case_shared_image_create(self):
        return SharedImageCreate, ImageBase

    @case(tags=["create"])
    def case_location_create(self):
        return LocationCreate, LocationBase

    @case(tags=["create"])
    def case_private_network_create(self):
        return PrivateNetworkCreate, NetworkBase

    @case(tags=["create"])
    def case_shared_network_create(self):
        return SharedNetworkCreate, NetworkBase

    @case(tags=["create"])
    def case_project_create(self):
        return ProjectCreate, ProjectBase

    @case(tags=["create"])
    def case_provider_create(self):
        return ProviderCreate, ProviderBase

    @case(tags=["create"])
    def case_block_storage_quota_create(self):
        return BlockStorageQuotaCreate, BlockStorageQuotaBase

    @case(tags=["create"])
    def case_compute_quota_create(self):
        return ComputeQuotaCreate, ComputeQuotaBase

    @case(tags=["create"])
    def case_network_quota_create(self):
        return NetworkQuotaCreate, NetworkQuotaBase

    @case(tags=["create"])
    def case_object_store_quota_create(self):
        return ObjectStoreQuotaCreate, ObjectStoreQuotaBase

    @case(tags=["create"])
    def case_region_create(self):
        return RegionCreate, RegionBase

    @case(tags=["create"])
    def case_block_storage_service_create(self):
        return BlockStorageServiceCreate, BlockStorageServiceBase

    @case(tags=["create"])
    def case_compute_service_create(self):
        return ComputeServiceCreate, ComputeServiceBase

    @case(tags=["create"])
    def case_identity_service_create(self):
        return IdentityServiceCreate, IdentityServiceBase

    @case(tags=["create"])
    def case_network_service_create(self):
        return NetworkServiceCreate, NetworkServiceBase

    @case(tags=["create"])
    def case_object_store_service_create(self):
        return ObjectStoreServiceCreate, ObjectStoreServiceBase

    @case(tags=["create"])
    def case_sla_create(self):
        return SLACreate, SLABase

    @case(tags=["create"])
    def case_user_group_create(self):
        return UserGroupCreate, UserGroupBase

    @case(tags=["update"])
    def case_flavor_update(self):
        return FlavorUpdate, FlavorBase

    @case(tags=["update"])
    def case_identity_provider_update(self):
        return IdentityProviderUpdate, IdentityProviderBase

    @case(tags=["update"])
    def case_image_update(self):
        return ImageUpdate, ImageBase

    @case(tags=["update"])
    def case_location_update(self):
        return LocationUpdate, LocationBase

    @case(tags=["update"])
    def case_network_update(self):
        return NetworkUpdate, NetworkBase

    @case(tags=["update"])
    def case_project_update(self):
        return ProjectUpdate, ProjectBase

    @case(tags=["update"])
    def case_provider_update(self):
        return ProviderUpdate, ProviderBase

    @case(tags=["update"])
    def case_block_storage_quota_update(self):
        return BlockStorageQuotaUpdate, BlockStorageQuotaBase

    @case(tags=["update"])
    def case_compute_quota_update(self):
        return ComputeQuotaUpdate, ComputeQuotaBase

    @case(tags=["update"])
    def case_network_quota_update(self):
        return NetworkQuotaUpdate, NetworkQuotaBase

    @case(tags=["update"])
    def case_object_store_quota_update(self):
        return ObjectStoreQuotaUpdate, ObjectStoreQuotaBase

    @case(tags=["update"])
    def case_region_update(self):
        return RegionUpdate, RegionBase

    @case(tags=["update"])
    def case_block_storage_service_update(self):
        return BlockStorageServiceUpdate, BlockStorageServiceBase

    @case(tags=["update"])
    def case_compute_service_update(self):
        return ComputeServiceUpdate, ComputeServiceBase

    @case(tags=["update"])
    def case_identity_service_update(self):
        return IdentityServiceUpdate, IdentityServiceBase

    @case(tags=["update"])
    def case_network_service_update(self):
        return NetworkServiceUpdate, NetworkServiceBase

    @case(tags=["update"])
    def case_object_store_service_update(self):
        return ObjectStoreServiceUpdate, ObjectStoreServiceBase

    @case(tags=["update"])
    def case_sla_update(self):
        return SLAUpdate, SLABase

    @case(tags=["update"])
    def case_user_group_update(self):
        return UserGroupUpdate, UserGroupBase

    @case(tags=["query"])
    def case_flavor_query(self):
        return FlavorQuery

    @case(tags=["query"])
    def case_identity_provider_query(self):
        return IdentityProviderQuery

    @case(tags=["query"])
    def case_image_query(self):
        return ImageQuery

    @case(tags=["query"])
    def case_location_query(self):
        return LocationQuery

    @case(tags=["query"])
    def case_network_query(self):
        return NetworkQuery

    @case(tags=["query"])
    def case_project_query(self):
        return ProjectQuery

    @case(tags=["query"])
    def case_provider_query(self):
        return ProviderQuery

    @case(tags=["query"])
    def case_block_storage_quota_query(self):
        return BlockStorageQuotaQuery

    @case(tags=["query"])
    def case_compute_quota_query(self):
        return ComputeQuotaQuery

    @case(tags=["query"])
    def case_network_quota_query(self):
        return NetworkQuotaQuery

    @case(tags=["query"])
    def case_object_store_quota_query(self):
        return ObjectStoreQuotaQuery

    @case(tags=["query"])
    def case_region_query(self):
        return RegionQuery

    @case(tags=["query"])
    def case_block_storage_service_query(self):
        return BlockStorageServiceQuery

    @case(tags=["query"])
    def case_compute_service_query(self):
        return ComputeServiceQuery

    @case(tags=["query"])
    def case_identity_service_query(self):
        return IdentityServiceQuery

    @case(tags=["query"])
    def case_network_service_query(self):
        return NetworkServiceQuery

    @case(tags=["query"])
    def case_object_store_service_query(self):
        return ObjectStoreServiceQuery

    @case(tags=["query"])
    def case_sla_query(self):
        return SLAQuery

    @case(tags=["query"])
    def case_user_group_query(self):
        return UserGroupQuery

    @case(tags=["read"])
    def case_flavor_read(self):
        return FlavorRead, FlavorBase

    @case(tags=["read"])
    def case_identity_provider_read(self):
        return IdentityProviderRead, IdentityProviderBase

    @case(tags=["read"])
    def case_image_read(self):
        return ImageRead, ImageBase

    @case(tags=["read"])
    def case_location_read(self):
        return LocationRead, LocationBase

    @case(tags=["read"])
    def case_network_read(self):
        return NetworkRead, NetworkBase

    @case(tags=["read"])
    def case_project_read(self):
        return ProjectRead, ProjectBase

    @case(tags=["read"])
    def case_provider_read(self):
        return ProviderRead, ProviderBase

    @case(tags=["read"])
    def case_block_storage_quota_read(self):
        return BlockStorageQuotaRead, BlockStorageQuotaBase

    @case(tags=["read"])
    def case_compute_quota_read(self):
        return ComputeQuotaRead, ComputeQuotaBase

    @case(tags=["read"])
    def case_network_quota_read(self):
        return NetworkQuotaRead, NetworkQuotaBase

    @case(tags=["read"])
    def case_object_store_quota_read(self):
        return ObjectStoreQuotaRead, ObjectStoreQuotaBase

    @case(tags=["read"])
    def case_region_read(self):
        return RegionRead, RegionBase

    @case(tags=["read"])
    def case_block_storage_service_read(self):
        return BlockStorageServiceRead, BlockStorageServiceBase

    @case(tags=["read"])
    def case_compute_service_read(self):
        return ComputeServiceRead, ComputeServiceBase

    @case(tags=["read"])
    def case_identity_service_read(self):
        return IdentityServiceRead, IdentityServiceBase

    @case(tags=["read"])
    def case_network_service_read(self):
        return NetworkServiceRead, NetworkServiceBase

    @case(tags=["read"])
    def case_object_store_service_read(self):
        return ObjectStoreServiceRead, ObjectStoreServiceBase

    @case(tags=["read"])
    def case_sla_read(self):
        return SLARead, SLABase

    @case(tags=["read"])
    def case_user_group_read(self):
        return UserGroupRead, UserGroupBase

    @case(tags=["read_public"])
    def case_flavor_read_public(self):
        return FlavorReadPublic, FlavorBasePublic

    @case(tags=["read_public"])
    def case_identity_provider_read_public(self):
        return IdentityProviderReadPublic, IdentityProviderBasePublic

    @case(tags=["read_public"])
    def case_image_read_public(self):
        return ImageReadPublic, ImageBasePublic

    @case(tags=["read_public"])
    def case_location_read_public(self):
        return LocationReadPublic, LocationBasePublic

    @case(tags=["read_public"])
    def case_network_read_public(self):
        return NetworkReadPublic, NetworkBasePublic

    @case(tags=["read_public"])
    def case_project_read_public(self):
        return ProjectReadPublic, ProjectBasePublic

    @case(tags=["read_public"])
    def case_provider_read_public(self):
        return ProviderReadPublic, ProviderBasePublic

    @case(tags=["read_public"])
    def case_block_storage_quota_read_public(self):
        return BlockStorageQuotaReadPublic, BlockStorageQuotaBasePublic

    @case(tags=["read_public"])
    def case_compute_quota_read_public(self):
        return ComputeQuotaReadPublic, ComputeQuotaBasePublic

    @case(tags=["read_public"])
    def case_network_quota_read_public(self):
        return NetworkQuotaReadPublic, NetworkQuotaBasePublic

    @case(tags=["read_public"])
    def case_object_store_quota_read_public(self):
        return ObjectStoreQuotaReadPublic, ObjectStoreQuotaBasePublic

    @case(tags=["read_public"])
    def case_region_read_public(self):
        return RegionReadPublic, RegionBasePublic

    @case(tags=["read_public"])
    def case_block_storage_service_read_public(self):
        return BlockStorageServiceReadPublic, BlockStorageServiceBasePublic

    @case(tags=["read_public"])
    def case_compute_service_read_public(self):
        return ComputeServiceReadPublic, ComputeServiceBasePublic

    @case(tags=["read_public"])
    def case_identity_service_read_public(self):
        return IdentityServiceReadPublic, IdentityServiceBasePublic

    @case(tags=["read_public"])
    def case_network_service_read_public(self):
        return NetworkServiceReadPublic, NetworkServiceBasePublic

    @case(tags=["read_public"])
    def case_object_store_service_read_public(self):
        return ObjectStoreServiceReadPublic, ObjectStoreServiceBasePublic

    @case(tags=["read_public"])
    def case_sla_read_public(self):
        return SLAReadPublic, SLABasePublic

    @case(tags=["read_public"])
    def case_user_group_read_public(self):
        return UserGroupReadPublic, UserGroupBasePublic
