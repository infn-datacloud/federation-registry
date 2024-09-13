from fed_reg.crud import CRUDInterface
from fed_reg.service.crud import (
    CRUDBlockStorageService,
    CRUDComputeService,
    CRUDIdentityService,
    CRUDNetworkService,
    CRUDObjectStoreService,
    block_storage_service_mgr,
    compute_service_mgr,
    identity_service_mgr,
    network_service_mgr,
    object_store_service_mgr,
)
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fed_reg.service.schemas import (
    BlockStorageServiceCreate,
    ComputeServiceCreate,
    IdentityServiceCreate,
    NetworkServiceCreate,
    ObjectStoreServiceCreate,
)


def test_inheritance():
    """Test CRUD classes inheritance."""
    # assert issubclass(CRUDService, CRUDInterface)
    assert issubclass(CRUDBlockStorageService, CRUDInterface)
    assert issubclass(CRUDComputeService, CRUDInterface)
    assert issubclass(CRUDIdentityService, CRUDInterface)
    assert issubclass(CRUDNetworkService, CRUDInterface)
    assert issubclass(CRUDObjectStoreService, CRUDInterface)

    # assert isinstance(service_mgr, CRUDService)
    assert isinstance(block_storage_service_mgr, CRUDBlockStorageService)
    assert isinstance(compute_service_mgr, CRUDComputeService)
    assert isinstance(identity_service_mgr, CRUDIdentityService)
    assert isinstance(network_service_mgr, CRUDNetworkService)
    assert isinstance(object_store_service_mgr, CRUDObjectStoreService)

    # assert service_mgr.model == Service
    # assert service_mgr.schema_create is None
    assert block_storage_service_mgr.model == BlockStorageService
    assert block_storage_service_mgr.schema_create == BlockStorageServiceCreate
    assert compute_service_mgr.model == ComputeService
    assert compute_service_mgr.schema_create == ComputeServiceCreate
    assert identity_service_mgr.model == IdentityService
    assert identity_service_mgr.schema_create == IdentityServiceCreate
    assert network_service_mgr.model == NetworkService
    assert network_service_mgr.schema_create == NetworkServiceCreate
    assert object_store_service_mgr.model == ObjectStoreService
    assert object_store_service_mgr.schema_create == ObjectStoreServiceCreate
