from pytest_cases import case

from fed_reg.identity_provider.schemas import (
    IdentityProviderRead,
    IdentityProviderReadPublic,
)
from fed_reg.provider.schemas_extended import (
    BlockStorageServiceReadExtended,
    BlockStorageServiceReadExtendedPublic,
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
    NetworkServiceReadExtended,
    NetworkServiceReadExtendedPublic,
    ObjectStorageServiceReadExtended,
    ObjectStorageServiceReadExtendedPublic,
    RegionReadExtended,
    RegionReadExtendedPublic,
    UserGroupReadExtended,
    UserGroupReadExtendedPublic,
)
from fed_reg.region.schemas import RegionRead, RegionReadPublic
from fed_reg.service.schemas import (
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    NetworkServiceRead,
    NetworkServiceReadPublic,
    ObjectStorageServiceRead,
    ObjectStorageServiceReadPublic,
)
from fed_reg.user_group.schemas import UserGroupRead, UserGroupReadPublic


class CaseProviderInheritance:
    @case(tags=["read"])
    def case_identity_provider_read(self):
        return IdentityProviderReadExtended, IdentityProviderRead

    @case(tags=["read"])
    def case_region_read(self):
        return RegionReadExtended, RegionRead

    @case(tags=["read"])
    def case_block_storage_service_read(self):
        return BlockStorageServiceReadExtended, BlockStorageServiceRead

    @case(tags=["read"])
    def case_compute_service_read(self):
        return ComputeServiceReadExtended, ComputeServiceRead

    @case(tags=["read"])
    def case_network_service_read(self):
        return NetworkServiceReadExtended, NetworkServiceRead

    @case(tags=["read"])
    def case_object_storage_service_read(self):
        return ObjectStorageServiceReadExtended, ObjectStorageServiceRead

    @case(tags=["read"])
    def case_user_group_read(self):
        return UserGroupReadExtended, UserGroupRead

    @case(tags=["read_public"])
    def case_identity_provider_read_public(self):
        return IdentityProviderReadExtendedPublic, IdentityProviderReadPublic

    @case(tags=["read_public"])
    def case_region_read_public(self):
        return RegionReadExtendedPublic, RegionReadPublic

    @case(tags=["read_public"])
    def case_block_storage_service_read_public(self):
        return BlockStorageServiceReadExtendedPublic, BlockStorageServiceReadPublic

    @case(tags=["read_public"])
    def case_compute_service_read_public(self):
        return ComputeServiceReadExtendedPublic, ComputeServiceReadPublic

    @case(tags=["read_public"])
    def case_network_service_read_public(self):
        return NetworkServiceReadExtendedPublic, NetworkServiceReadPublic

    @case(tags=["read_public"])
    def case_object_storage_service_read_public(self):
        return ObjectStorageServiceReadExtendedPublic, ObjectStorageServiceReadPublic

    @case(tags=["read_public"])
    def case_user_group_read_public(self):
        return UserGroupReadExtendedPublic, UserGroupReadPublic
