"""Module with the router architecture."""

from fastapi import APIRouter

from fed_reg.flavor.api.v1.endpoints import router as flavor_router_v1
from fed_reg.identity_provider.api.v1.endpoints import (
    router as identity_provider_router_v1,
)
from fed_reg.image.api.v1.endpoints import router as image_router_v1
from fed_reg.location.api.v1.endpoints import router as location_router_v1
from fed_reg.network.api.v1.endpoints import router as network_router_v1
from fed_reg.project.api.v1.endpoints import router as project_router_v1
from fed_reg.provider.api.v1.endpoints import router as provider_router_v1
from fed_reg.quota.api.v1.endpoints import (
    bs_router as block_storage_quota_router_v1,
)
from fed_reg.quota.api.v1.endpoints import c_router as compute_quota_router_v1
from fed_reg.quota.api.v1.endpoints import n_router as network_quota_router_v1
from fed_reg.quota.api.v1.endpoints import (
    os_router as object_storage_quota_router_v1,
)
from fed_reg.region.api.v1.endpoints import router as region_router_v1
from fed_reg.service.api.v1.endpoints import (
    bs_router as block_storage_service_router_v1,
)
from fed_reg.service.api.v1.endpoints import c_router as compute_service_router_v1
from fed_reg.service.api.v1.endpoints import i_router as identity_service_router_v1
from fed_reg.service.api.v1.endpoints import n_router as network_service_router_v1
from fed_reg.service.api.v1.endpoints import (
    os_router as object_storage_service_router_v1,
)
from fed_reg.sla.api.v1.endpoints import router as sla_router_v1
from fed_reg.user_group.api.v1.endpoints import router as user_group_router_v1

router_v1 = APIRouter()
router_v1.include_router(flavor_router_v1)
router_v1.include_router(identity_provider_router_v1)
router_v1.include_router(image_router_v1)
router_v1.include_router(location_router_v1)
router_v1.include_router(network_router_v1)
router_v1.include_router(project_router_v1)
router_v1.include_router(provider_router_v1)
router_v1.include_router(block_storage_quota_router_v1)
router_v1.include_router(compute_quota_router_v1)
router_v1.include_router(network_quota_router_v1)
router_v1.include_router(object_storage_quota_router_v1)
router_v1.include_router(region_router_v1)
router_v1.include_router(block_storage_service_router_v1)
router_v1.include_router(compute_service_router_v1)
router_v1.include_router(identity_service_router_v1)
router_v1.include_router(network_service_router_v1)
router_v1.include_router(object_storage_service_router_v1)
router_v1.include_router(sla_router_v1)
router_v1.include_router(user_group_router_v1)
