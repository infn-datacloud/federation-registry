from typing import Any, Literal

from pytest_cases import case

from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from tests.models.utils import region_model_dict, service_model_dict
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return region_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {**region_model_dict(), "description": random_lower_string()}

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = region_model_dict()
        d.pop("name")
        return d, "name"


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
