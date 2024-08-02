from pytest_cases import case, parametrize

from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    Quota,
)


class CaseAttr:
    @case(tags=("attr", "optional"))
    @parametrize(value=("description", "per_user", "usage"))
    def case_optional(self, value: str) -> str:
        return value

    @case(tags=("attr", "block_storage"))
    @parametrize(value=("gigabytes", "per_volume_gigabytes", "volumes"))
    def case_block_storage(self, value: str) -> str:
        return value

    @case(tags=("attr", "compute"))
    @parametrize(value=("cores", "instances", "ram"))
    def case_compute(self, value: str) -> str:
        return value

    @case(tags=("attr", "network"))
    @parametrize(
        value=(
            "public_ips",
            "networks",
            "ports",
            "security_groups",
            "security_group_rules",
        )
    )
    def case_network(self, value: str) -> str:
        return value

    @case(tags=("attr", "object_store"))
    @parametrize(value=("bytes", "containers", "objects"))
    def case_object_store(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_quota(self) -> type[Quota]:
        return Quota

    @case(tags=("class", "derived"))
    def case_block_storage_quota(self) -> type[BlockStorageQuota]:
        return BlockStorageQuota

    @case(tags=("class", "derived"))
    def case_compute_quota(self) -> type[ComputeQuota]:
        return ComputeQuota

    @case(tags=("class", "derived"))
    def case_network_quota(self) -> type[NetworkQuota]:
        return NetworkQuota

    @case(tags=("class", "derived"))
    def case_object_store_quota(self) -> type[ObjectStoreQuota]:
        return ObjectStoreQuota


class CaseModel:
    @case(tags="model")
    def case_quota(self, quota_model: Quota) -> Quota:
        return quota_model

    @case(tags=("model", "derived"))
    def case_block_storage_quota(
        self, block_storage_quota_model: BlockStorageQuota
    ) -> BlockStorageQuota:
        return block_storage_quota_model

    @case(tags=("model", "derived"))
    def case_compute_quota(self, compute_quota_model: ComputeQuota) -> ComputeQuota:
        return compute_quota_model

    @case(tags=("model", "derived"))
    def case_network_quota(self, network_quota_model: NetworkQuota) -> NetworkQuota:
        return network_quota_model

    @case(tags=("model", "derived"))
    def case_object_store_quota(
        self, object_store_quota_model: ObjectStoreQuota
    ) -> ObjectStoreQuota:
        return object_store_quota_model
