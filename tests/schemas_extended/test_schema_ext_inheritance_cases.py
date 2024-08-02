from pytest_cases import case

from fed_reg.flavor.schemas import (
    FlavorBase,
    FlavorBasePublic,
    PrivateFlavorCreate,
    SharedFlavorCreate,
)
from fed_reg.flavor.schemas_extended import FlavorReadExtended, FlavorReadExtendedPublic
from fed_reg.identity_provider.schemas import (
    IdentityProviderBase,
    IdentityProviderBasePublic,
    IdentityProviderCreate,
)
from fed_reg.identity_provider.schemas_extended import (
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
)
from fed_reg.image.schemas import (
    ImageBase,
    ImageBasePublic,
    PrivateImageCreate,
    SharedImageCreate,
)
from fed_reg.image.schemas_extended import ImageReadExtended, ImageReadExtendedPublic
from fed_reg.location.schemas import (
    LocationBase,
    LocationBasePublic,
)
from fed_reg.location.schemas_extended import (
    LocationReadExtended,
    LocationReadExtendedPublic,
)
from fed_reg.network.schemas import (
    NetworkBase,
    NetworkBasePublic,
    NetworkCreate,
)
from fed_reg.network.schemas_extended import (
    NetworkReadExtended,
    NetworkReadExtendedPublic,
)
from fed_reg.project.schemas import (
    ProjectBase,
    ProjectBasePublic,
)
from fed_reg.project.schemas_extended import (
    ProjectReadExtended,
    ProjectReadExtendedPublic,
)
from fed_reg.provider.schemas import (
    ProviderBase,
    ProviderBasePublic,
    ProviderCreate,
)
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
    ProviderCreateExtended,
    ProviderReadExtended,
    ProviderReadExtendedPublic,
    RegionCreateExtended,
    SharedFlavorCreateExtended,
    SharedImageCreateExtended,
    SLACreateExtended,
    UserGroupCreateExtended,
)
from fed_reg.quota.schemas import (
    BlockStorageQuotaBase,
    BlockStorageQuotaBasePublic,
    BlockStorageQuotaCreate,
    ComputeQuotaBase,
    ComputeQuotaBasePublic,
    ComputeQuotaCreate,
    NetworkQuotaBase,
    NetworkQuotaBasePublic,
    NetworkQuotaCreate,
    ObjectStoreQuotaBase,
    ObjectStoreQuotaBasePublic,
    ObjectStoreQuotaCreate,
)
from fed_reg.quota.schemas_extended import (
    BlockStorageQuotaReadExtended,
    BlockStorageQuotaReadExtendedPublic,
    ComputeQuotaReadExtended,
    ComputeQuotaReadExtendedPublic,
    NetworkQuotaReadExtended,
    NetworkQuotaReadExtendedPublic,
    ObjectStoreQuotaReadExtended,
    ObjectStoreQuotaReadExtendedPublic,
)
from fed_reg.region.schemas import (
    RegionBase,
    RegionBasePublic,
    RegionCreate,
)
from fed_reg.region.schemas_extended import RegionReadExtended, RegionReadExtendedPublic
from fed_reg.service.schemas import (
    BlockStorageServiceBase,
    BlockStorageServiceBasePublic,
    BlockStorageServiceCreate,
    ComputeServiceBase,
    ComputeServiceBasePublic,
    ComputeServiceCreate,
    IdentityServiceBase,
    IdentityServiceBasePublic,
    NetworkServiceBase,
    NetworkServiceBasePublic,
    NetworkServiceCreate,
    ObjectStoreServiceBase,
    ObjectStoreServiceBasePublic,
    ObjectStoreServiceCreate,
)
from fed_reg.service.schemas_extended import (
    BlockStorageServiceReadExtended,
    BlockStorageServiceReadExtendedPublic,
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    IdentityServiceReadExtended,
    IdentityServiceReadExtendedPublic,
    NetworkServiceReadExtended,
    NetworkServiceReadExtendedPublic,
    ObjectStoreServiceReadExtended,
    ObjectStoreServiceReadExtendedPublic,
)
from fed_reg.sla.schemas import (
    SLABase,
    SLABasePublic,
    SLACreate,
)
from fed_reg.sla.schemas_extended import SLAReadExtended, SLAReadExtendedPublic
from fed_reg.user_group.schemas import (
    UserGroupBase,
    UserGroupBasePublic,
    UserGroupCreate,
)
from fed_reg.user_group.schemas_extended import (
    UserGroupReadExtended,
    UserGroupReadExtendedPublic,
)


class CaseClassInheritance:
    @case(tags=["create"])
    def case_private_flavor_create(self):
        return PrivateFlavorCreateExtended, PrivateFlavorCreate

    @case(tags=["create"])
    def case_shared_flavor_create(self):
        return SharedFlavorCreateExtended, SharedFlavorCreate

    @case(tags=["create"])
    def case_identity_provider_create(self):
        return IdentityProviderCreateExtended, IdentityProviderCreate

    @case(tags=["create"])
    def case_private_image_create(self):
        return PrivateImageCreateExtended, PrivateImageCreate

    @case(tags=["create"])
    def case_shared_image_create(self):
        return SharedImageCreateExtended, SharedImageCreate

    @case(tags=["create"])
    def case_network_create(self):
        return NetworkCreateExtended, NetworkCreate

    @case(tags=["create"])
    def case_provider_create(self):
        return ProviderCreateExtended, ProviderCreate

    @case(tags=["create"])
    def case_block_storage_quota_create(self):
        return BlockStorageQuotaCreateExtended, BlockStorageQuotaCreate

    @case(tags=["create"])
    def case_compute_quota_create(self):
        return ComputeQuotaCreateExtended, ComputeQuotaCreate

    @case(tags=["create"])
    def case_network_quota_create(self):
        return NetworkQuotaCreateExtended, NetworkQuotaCreate

    @case(tags=["create"])
    def case_object_store_quota_create(self):
        return ObjectStoreQuotaCreateExtended, ObjectStoreQuotaCreate

    @case(tags=["create"])
    def case_region_create(self):
        return RegionCreateExtended, RegionCreate

    @case(tags=["create"])
    def case_block_storage_service_create(self):
        return BlockStorageServiceCreateExtended, BlockStorageServiceCreate

    @case(tags=["create"])
    def case_compute_service_create(self):
        return ComputeServiceCreateExtended, ComputeServiceCreate

    @case(tags=["create"])
    def case_network_service_create(self):
        return NetworkServiceCreateExtended, NetworkServiceCreate

    @case(tags=["create"])
    def case_object_store_service_create(self):
        return ObjectStoreServiceCreateExtended, ObjectStoreServiceCreate

    @case(tags=["create"])
    def case_sla_create(self):
        return SLACreateExtended, SLACreate

    @case(tags=["create"])
    def case_user_group_create(self):
        return UserGroupCreateExtended, UserGroupCreate

    @case(tags=["read"])
    def case_flavor_read(self):
        return FlavorReadExtended, FlavorBase

    @case(tags=["read"])
    def case_identity_provider_read(self):
        return IdentityProviderReadExtended, IdentityProviderBase

    @case(tags=["read"])
    def case_image_read(self):
        return ImageReadExtended, ImageBase

    @case(tags=["read"])
    def case_location_read(self):
        return LocationReadExtended, LocationBase

    @case(tags=["read"])
    def case_network_read(self):
        return NetworkReadExtended, NetworkBase

    @case(tags=["read"])
    def case_project_read(self):
        return ProjectReadExtended, ProjectBase

    @case(tags=["read"])
    def case_provider_read(self):
        return ProviderReadExtended, ProviderBase

    @case(tags=["read"])
    def case_block_storage_quota_read(self):
        return BlockStorageQuotaReadExtended, BlockStorageQuotaBase

    @case(tags=["read"])
    def case_compute_quota_read(self):
        return ComputeQuotaReadExtended, ComputeQuotaBase

    @case(tags=["read"])
    def case_network_quota_read(self):
        return NetworkQuotaReadExtended, NetworkQuotaBase

    @case(tags=["read"])
    def case_object_store_quota_read(self):
        return ObjectStoreQuotaReadExtended, ObjectStoreQuotaBase

    @case(tags=["read"])
    def case_region_read(self):
        return RegionReadExtended, RegionBase

    @case(tags=["read"])
    def case_block_storage_service_read(self):
        return BlockStorageServiceReadExtended, BlockStorageServiceBase

    @case(tags=["read"])
    def case_compute_service_read(self):
        return ComputeServiceReadExtended, ComputeServiceBase

    @case(tags=["read"])
    def case_identity_service_read(self):
        return IdentityServiceReadExtended, IdentityServiceBase

    @case(tags=["read"])
    def case_network_service_read(self):
        return NetworkServiceReadExtended, NetworkServiceBase

    @case(tags=["read"])
    def case_object_store_service_read(self):
        return ObjectStoreServiceReadExtended, ObjectStoreServiceBase

    @case(tags=["read"])
    def case_sla_read(self):
        return SLAReadExtended, SLABase

    @case(tags=["read"])
    def case_user_group_read(self):
        return UserGroupReadExtended, UserGroupBase

    @case(tags=["read_public"])
    def case_flavor_read_public(self):
        return FlavorReadExtendedPublic, FlavorBasePublic

    @case(tags=["read_public"])
    def case_identity_provider_read_public(self):
        return IdentityProviderReadExtendedPublic, IdentityProviderBasePublic

    @case(tags=["read_public"])
    def case_image_read_public(self):
        return ImageReadExtendedPublic, ImageBasePublic

    @case(tags=["read_public"])
    def case_location_read_public(self):
        return LocationReadExtendedPublic, LocationBasePublic

    @case(tags=["read_public"])
    def case_network_read_public(self):
        return NetworkReadExtendedPublic, NetworkBasePublic

    @case(tags=["read_public"])
    def case_project_read_public(self):
        return ProjectReadExtendedPublic, ProjectBasePublic

    @case(tags=["read_public"])
    def case_provider_read_public(self):
        return ProviderReadExtendedPublic, ProviderBasePublic

    @case(tags=["read_public"])
    def case_block_storage_quota_read_public(self):
        return BlockStorageQuotaReadExtendedPublic, BlockStorageQuotaBasePublic

    @case(tags=["read_public"])
    def case_compute_quota_read_public(self):
        return ComputeQuotaReadExtendedPublic, ComputeQuotaBasePublic

    @case(tags=["read_public"])
    def case_network_quota_read_public(self):
        return NetworkQuotaReadExtendedPublic, NetworkQuotaBasePublic

    @case(tags=["read_public"])
    def case_object_store_quota_read_public(self):
        return ObjectStoreQuotaReadExtendedPublic, ObjectStoreQuotaBasePublic

    @case(tags=["read_public"])
    def case_region_read_public(self):
        return RegionReadExtendedPublic, RegionBasePublic

    @case(tags=["read_public"])
    def case_block_storage_service_read_public(self):
        return BlockStorageServiceReadExtendedPublic, BlockStorageServiceBasePublic

    @case(tags=["read_public"])
    def case_compute_service_read_public(self):
        return ComputeServiceReadExtendedPublic, ComputeServiceBasePublic

    @case(tags=["read_public"])
    def case_identity_service_read_public(self):
        return IdentityServiceReadExtendedPublic, IdentityServiceBasePublic

    @case(tags=["read_public"])
    def case_network_service_read_public(self):
        return NetworkServiceReadExtendedPublic, NetworkServiceBasePublic

    @case(tags=["read_public"])
    def case_object_store_service_read_public(self):
        return ObjectStoreServiceReadExtendedPublic, ObjectStoreServiceBasePublic

    @case(tags=["read_public"])
    def case_sla_read_public(self):
        return SLAReadExtendedPublic, SLABasePublic

    @case(tags=["read_public"])
    def case_user_group_read_public(self):
        return UserGroupReadExtendedPublic, UserGroupBasePublic
