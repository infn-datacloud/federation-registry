from typing import Any, Literal

from pytest_cases import case

from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from tests.models.utils import project_model_dict, quota_model_dict
from tests.utils import random_lower_string


class CaseProjectModelDict:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return project_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            **project_model_dict(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = project_model_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid"))
    def case_missing_uuid(self) -> tuple[dict[str, Any], Literal["uuid"]]:
        d = project_model_dict()
        d.pop("uuid")
        return d, "uuid"


class CaseQuota:
    @case(tags=("quota", "single"))
    def case_block_storage_quota(
        self, block_storage_quota_model: BlockStorageQuota
    ) -> BlockStorageQuota:
        return block_storage_quota_model

    @case(tags=("quota", "single"))
    def case_compute_quota(self, compute_quota_model: ComputeQuota) -> ComputeQuota:
        return compute_quota_model

    @case(tags=("quota", "single"))
    def case_network_quota(self, network_quota_model: NetworkQuota) -> NetworkQuota:
        return network_quota_model

    @case(tags=("quota", "single"))
    def case_object_store_quota(
        self, object_store_quota_model: ObjectStoreQuota
    ) -> ObjectStoreQuota:
        return object_store_quota_model

    @case(tags=("quota", "multi"))
    def case_block_storage_quotas(self) -> list[BlockStorageQuota]:
        return [
            BlockStorageQuota(**quota_model_dict()).save(),
            BlockStorageQuota(**quota_model_dict()).save(),
        ]

    @case(tags=("quota", "multi"))
    def case_compute_quotas(self) -> list[ComputeQuota]:
        return [
            ComputeQuota(**quota_model_dict()).save(),
            ComputeQuota(**quota_model_dict()).save(),
        ]

    @case(tags=("quota", "multi"))
    def case_network_quotas(self) -> list[NetworkQuota]:
        return [
            NetworkQuota(**quota_model_dict()).save(),
            NetworkQuota(**quota_model_dict()).save(),
        ]

    @case(tags=("quota", "multi"))
    def case_object_store_quotas(self) -> list[ObjectStoreQuota]:
        return [
            ObjectStoreQuota(**quota_model_dict()).save(),
            ObjectStoreQuota(**quota_model_dict()).save(),
        ]
