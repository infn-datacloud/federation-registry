from uuid import uuid4

from pytest_cases import case

from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from tests.utils import random_lower_string


class CaseProjectModelDict:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> str:
        return {"name": random_lower_string(), "uuid": uuid4().hex}

    @case(tags=("dict", "valid"))
    def case_description(self) -> str:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "description": random_lower_string(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> str:
        return {"uuid": uuid4().hex}

    @case(tags=("dict", "invalid"))
    def case_missing_uuid(self) -> str:
        return {"name": random_lower_string()}


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
        return [BlockStorageQuota().save(), BlockStorageQuota().save()]

    @case(tags=("quota", "multi"))
    def case_compute_quotas(self) -> list[ComputeQuota]:
        return [ComputeQuota().save(), ComputeQuota().save()]

    @case(tags=("quota", "multi"))
    def case_network_quotas(self) -> list[NetworkQuota]:
        return [NetworkQuota().save(), NetworkQuota().save()]

    @case(tags=("quota", "multi"))
    def case_object_store_quotas(self) -> list[ObjectStoreQuota]:
        return [ObjectStoreQuota().save(), ObjectStoreQuota().save()]
