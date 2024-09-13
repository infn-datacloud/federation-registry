from fed_reg.crud import CRUDInterface
from fed_reg.quota.crud import (
    CRUDBlockStorageQuota,
    CRUDComputeQuota,
    CRUDNetworkQuota,
    CRUDObjectStoreQuota,
    block_storage_quota_mgr,
    compute_quota_mgr,
    network_quota_mgr,
    object_store_quota_mgr,
)
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fed_reg.quota.schemas import (
    BlockStorageQuotaCreate,
    ComputeQuotaCreate,
    NetworkQuotaCreate,
    ObjectStoreQuotaCreate,
)


def test_inheritance():
    """Test CRUD classes inheritance."""
    # assert issubclass(CRUDQuota, CRUDInterface)
    assert issubclass(CRUDBlockStorageQuota, CRUDInterface)
    assert issubclass(CRUDComputeQuota, CRUDInterface)
    assert issubclass(CRUDNetworkQuota, CRUDInterface)
    assert issubclass(CRUDObjectStoreQuota, CRUDInterface)

    # assert isinstance(quota_mgr, CRUDQuota)
    assert isinstance(block_storage_quota_mgr, CRUDBlockStorageQuota)
    assert isinstance(compute_quota_mgr, CRUDComputeQuota)
    assert isinstance(network_quota_mgr, CRUDNetworkQuota)
    assert isinstance(object_store_quota_mgr, CRUDObjectStoreQuota)

    # assert quota_mgr.model == Quota
    # assert quota_mgr.schema_create is None
    assert block_storage_quota_mgr.model == BlockStorageQuota
    assert block_storage_quota_mgr.schema_create == BlockStorageQuotaCreate
    assert compute_quota_mgr.model == ComputeQuota
    assert compute_quota_mgr.schema_create == ComputeQuotaCreate
    assert network_quota_mgr.model == NetworkQuota
    assert network_quota_mgr.schema_create == NetworkQuotaCreate
    assert object_store_quota_mgr.model == ObjectStoreQuota
    assert object_store_quota_mgr.schema_create == ObjectStoreQuotaCreate
