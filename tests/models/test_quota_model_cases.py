from typing import Any

from pytest_cases import case

from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    Quota,
)
from tests.models.utils import quota_model_dict
from tests.utils import random_int, random_lower_string


class CaseQuotaModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return quota_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {**quota_model_dict(), "description": random_lower_string()}

    @case(tags=("dict", "valid"))
    def case_per_user(self) -> dict[str, Any]:
        return {**quota_model_dict(), "per_user": True}

    @case(tags=("dict", "valid"))
    def case_usage(self) -> dict[str, Any]:
        return {**quota_model_dict(), "usage": True}

    @case(tags=("attr", "valid", "block_storage"))
    def case_gigabytes(self) -> dict[str, Any]:
        return {**quota_model_dict(), "gigabytes": random_int()}

    @case(tags=("attr", "valid", "block_storage"))
    def case_per_volume_gigabytes(self) -> dict[str, Any]:
        return {**quota_model_dict(), "per_volume_gigabytes": random_int()}

    @case(tags=("attr", "valid", "block_storage"))
    def case_volumes(self) -> dict[str, Any]:
        return {**quota_model_dict(), "volumes": random_int()}

    @case(tags=("attr", "valid", "compute"))
    def case_cores(self) -> dict[str, Any]:
        return {**quota_model_dict(), "cores": random_int()}

    @case(tags=("attr", "valid", "compute"))
    def case_instances(self) -> dict[str, Any]:
        return {**quota_model_dict(), "instances": random_int()}

    @case(tags=("attr", "valid", "compute"))
    def case_ram(self) -> dict[str, Any]:
        return {**quota_model_dict(), "ram": random_int()}

    @case(tags=("attr", "valid", "network"))
    def case_public_ips(self) -> dict[str, Any]:
        return {**quota_model_dict(), "public_ips": random_int()}

    @case(tags=("attr", "valid", "network"))
    def case_networks(self) -> dict[str, Any]:
        return {**quota_model_dict(), "networks": random_int()}

    @case(tags=("attr", "valid", "network"))
    def case_ports(self) -> dict[str, Any]:
        return {**quota_model_dict(), "ports": random_int()}

    @case(tags=("attr", "valid", "network"))
    def case_security_groups(self) -> dict[str, Any]:
        return {**quota_model_dict(), "security_groups": random_int()}

    @case(tags=("attr", "valid", "network"))
    def case_security_group_rules(self) -> dict[str, Any]:
        return {**quota_model_dict(), "security_group_rules": random_int()}

    @case(tags=("attr", "valid", "object_store"))
    def case_bytes(self) -> dict[str, Any]:
        return {**quota_model_dict(), "bytes": random_int()}

    @case(tags=("attr", "valid", "object_store"))
    def case_containers(self) -> dict[str, Any]:
        return {**quota_model_dict(), "containers": random_int()}

    @case(tags=("attr", "valid", "object_store"))
    def case_objects(self) -> dict[str, Any]:
        return {**quota_model_dict(), "objects": random_int()}

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

    @case(tags="model")
    def case_quota_model(self, quota_model: Quota) -> Quota:
        return quota_model

    @case(tags=("model", "derived"))
    def case_block_storage_quota_model(
        self, block_storage_quota_model: BlockStorageQuota
    ) -> BlockStorageQuota:
        return block_storage_quota_model

    @case(tags=("model", "derived"))
    def case_compute_quota_model(
        self, compute_quota_model: ComputeQuota
    ) -> ComputeQuota:
        return compute_quota_model

    @case(tags=("model", "derived"))
    def case_network_quota_model(
        self, network_quota_model: NetworkQuota
    ) -> NetworkQuota:
        return network_quota_model

    @case(tags=("model", "derived"))
    def case_object_store_quota_model(
        self, object_store_quota_model: ObjectStoreQuota
    ) -> ObjectStoreQuota:
        return object_store_quota_model
