from random import choice
from typing import List

from app.provider.schemas_extended import (
    BlockStorageServiceCreateExtended,
    ComputeServiceCreateExtended,
    NetworkServiceCreateExtended,
)
from app.service.enum import (
    BlockStorageServiceName,
    ComputeServiceName,
    IdentityServiceName,
    NetworkServiceName,
    ServiceType,
)
from app.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
)
from app.service.schemas import (
    BlockStorageServiceUpdate,
    ComputeServiceUpdate,
    IdentityServiceCreate,
    IdentityServiceUpdate,
    NetworkServiceUpdate,
)
from app.tests.utils.block_storage_quota import (
    create_random_block_storage_quota,
    validate_create_block_storage_quota_attrs,
)
from app.tests.utils.compute_quota import (
    create_random_compute_quota,
    validate_create_compute_quota_attrs,
)
from app.tests.utils.flavor import create_random_flavor, validate_create_flavor_attrs
from app.tests.utils.image import create_random_image, validate_create_image_attrs
from app.tests.utils.network import create_random_network, validate_create_network_attrs
from app.tests.utils.utils import random_lower_string, random_url


def create_random_block_storage_service(
    *, default: bool = False, projects: List[str] = []
) -> BlockStorageServiceCreateExtended:
    endpoint = random_url()
    name = random_block_storage_service_name()
    kwargs = {}
    if not default:
        kwargs = {"description": random_lower_string()}
    if len(projects):
        kwargs["quotas"] = [create_random_block_storage_quota(project=projects[0])]
    return BlockStorageServiceCreateExtended(endpoint=endpoint, name=name, **kwargs)


def create_random_compute_service(
    *,
    default: bool = False,
    with_flavors: bool = False,
    with_images: bool = False,
    projects: List[str] = [],
) -> ComputeServiceCreateExtended:
    endpoint = random_url()
    name = random_compute_service_name()
    kwargs = {}
    if not default:
        kwargs = {"description": random_lower_string()}
    if with_flavors:
        kwargs["flavors"] = [create_random_flavor(projects=projects)]
    if with_images:
        kwargs["images"] = [create_random_image(projects=projects)]
    if len(projects):
        kwargs["quotas"] = [create_random_compute_quota(project=projects[0])]
    return ComputeServiceCreateExtended(endpoint=endpoint, name=name, **kwargs)


def create_random_identity_service(*, default: bool = False) -> IdentityServiceCreate:
    endpoint = random_url()
    name = random_identity_service_name()
    kwargs = {}
    if not default:
        kwargs = {"description": random_lower_string()}
    return IdentityServiceCreate(endpoint=endpoint, name=name, **kwargs)


def create_random_network_service(
    *, default: bool = False, with_networks: bool = False, projects: List[str] = []
) -> NetworkServiceCreateExtended:
    endpoint = random_url()
    name = random_network_service_name()
    kwargs = {}
    if not default:
        kwargs = {"description": random_lower_string()}
    if with_networks:
        project = None if len(projects) == 0 else projects[0]
        kwargs["networks"] = [create_random_network(project=project)]
    return NetworkServiceCreateExtended(endpoint=endpoint, name=name, **kwargs)


def create_random_block_storage_service_patch(
    default: bool = False,
) -> BlockStorageServiceUpdate:
    if default:
        return BlockStorageServiceUpdate()
    description = random_lower_string()
    endpoint = random_url()
    name = random_block_storage_service_name()
    return BlockStorageServiceUpdate(
        description=description, endpoint=endpoint, name=name
    )


def create_random_compute_service_patch(
    default: bool = False,
) -> ComputeServiceUpdate:
    if default:
        return ComputeServiceUpdate()
    description = random_lower_string()
    endpoint = random_url()
    name = random_compute_service_name()
    return ComputeServiceUpdate(description=description, endpoint=endpoint, name=name)


def create_random_identity_service_patch(
    default: bool = False,
) -> IdentityServiceUpdate:
    if default:
        return IdentityServiceUpdate()
    description = random_lower_string()
    endpoint = random_url()
    name = random_identity_service_name()
    return IdentityServiceUpdate(description=description, endpoint=endpoint, name=name)


def create_random_network_service_patch(
    default: bool = False,
) -> NetworkServiceUpdate:
    if default:
        return NetworkServiceUpdate()
    description = random_lower_string()
    endpoint = random_url()
    name = random_network_service_name()
    return NetworkServiceUpdate(description=description, endpoint=endpoint, name=name)


def random_service_type() -> str:
    return choice([i.value for i in ServiceType])


def random_block_storage_service_name() -> str:
    return choice([i.value for i in BlockStorageServiceName])


def random_compute_service_name() -> str:
    return choice([i.value for i in ComputeServiceName])


def random_identity_service_name() -> str:
    return choice([i.value for i in IdentityServiceName])


def random_network_service_name() -> str:
    return choice([i.value for i in NetworkServiceName])


def validate_block_storage_service_attrs(
    *, obj_in: BlockStorageServiceCreateExtended, db_item: BlockStorageService
) -> None:
    assert db_item.description == obj_in.description
    assert db_item.endpoint == obj_in.endpoint
    assert db_item.name == obj_in.name
    assert db_item.type == obj_in.type
    assert len(db_item.quotas) == len(obj_in.quotas)
    for db_quota, quota_in in zip(db_item.quotas, obj_in.quotas):
        validate_create_block_storage_quota_attrs(db_item=db_quota, obj_in=quota_in)


def validate_compute_service_attrs(
    *, obj_in: ComputeServiceCreateExtended, db_item: ComputeService
) -> None:
    assert db_item.description == obj_in.description
    assert db_item.endpoint == obj_in.endpoint
    assert db_item.name == obj_in.name
    assert db_item.type == obj_in.type
    assert len(db_item.flavors) == len(obj_in.flavors)
    for db_flav, flav_in in zip(db_item.flavors, obj_in.flavors):
        validate_create_flavor_attrs(db_item=db_flav, obj_in=flav_in)
    assert len(db_item.images) == len(obj_in.images)
    for db_img, img_in in zip(db_item.images, obj_in.images):
        validate_create_image_attrs(db_item=db_img, obj_in=img_in)
    assert len(db_item.quotas) == len(obj_in.quotas)
    for db_quota, quota_in in zip(db_item.quotas, obj_in.quotas):
        validate_create_compute_quota_attrs(db_item=db_quota, obj_in=quota_in)


def validate_identity_service_attrs(
    *, obj_in: IdentityServiceCreate, db_item: IdentityService
) -> None:
    assert db_item.description == obj_in.description
    assert db_item.endpoint == obj_in.endpoint
    assert db_item.name == obj_in.name
    assert db_item.type == obj_in.type


def validate_network_service_attrs(
    *, obj_in: NetworkServiceCreateExtended, db_item: NetworkService
) -> None:
    assert db_item.description == obj_in.description
    assert db_item.endpoint == obj_in.endpoint
    assert db_item.name == obj_in.name
    assert db_item.type == obj_in.type
    assert len(db_item.networks) == len(obj_in.networks)
    for db_net, net_in in zip(db_item.networks, obj_in.networks):
        validate_create_network_attrs(db_item=db_net, obj_in=net_in)
