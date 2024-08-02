from pytest_cases import case, parametrize

from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from tests.create_dict import quota_model_dict


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(value=("description",))
    def case_optional(self, value: str) -> str:
        return value


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
