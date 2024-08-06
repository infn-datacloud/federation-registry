from pytest_cases import case, parametrize

from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from tests.models.utils import service_model_dict


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name",))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(value=("description",))
    def case_optional(self, value: str) -> str:
        return value


class CaseService:
    @case(tags=("service", "single"))
    def case_block_storage_service(
        self, block_storage_service_model: BlockStorageService
    ) -> BlockStorageService:
        return block_storage_service_model

    @case(tags=("service", "single"))
    def case_compute_service(
        self, compute_service_model: ComputeService
    ) -> ComputeService:
        return compute_service_model

    @case(tags=("service", "single"))
    def case_identity_service(
        self, identity_service_model: IdentityService
    ) -> IdentityService:
        return identity_service_model

    @case(tags=("service", "single"))
    def case_network_service(
        self, network_service_model: NetworkService
    ) -> NetworkService:
        return network_service_model

    @case(tags=("service", "single"))
    def case_object_store_service(
        self, object_store_service_model: ObjectStoreService
    ) -> ObjectStoreService:
        return object_store_service_model

    @case(tags=("service", "multi"))
    def case_block_storage_services(self) -> list[BlockStorageService]:
        return [
            BlockStorageService(**service_model_dict()).save(),
            BlockStorageService(**service_model_dict()).save(),
        ]

    @case(tags=("service", "multi"))
    def case_compute_services(self) -> list[ComputeService]:
        return [
            ComputeService(**service_model_dict()).save(),
            ComputeService(**service_model_dict()).save(),
        ]

    @case(tags=("service", "multi"))
    def case_identity_services(self) -> list[IdentityService]:
        return [
            IdentityService(**service_model_dict()).save(),
            IdentityService(**service_model_dict()).save(),
        ]

    @case(tags=("service", "multi"))
    def case_network_services(self) -> list[NetworkService]:
        return [
            NetworkService(**service_model_dict()).save(),
            NetworkService(**service_model_dict()).save(),
        ]

    @case(tags=("service", "multi"))
    def case_object_store_services(self) -> list[ObjectStoreService]:
        return [
            ObjectStoreService(**service_model_dict()).save(),
            ObjectStoreService(**service_model_dict()).save(),
        ]
