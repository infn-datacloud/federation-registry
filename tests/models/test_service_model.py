from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fed_reg.region.models import Region
from fed_reg.service.enum import ServiceType
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
    Service,
)
from tests.create_dict import quota_model_dict, region_model_dict, service_model_dict


@parametrize_with_cases("service_cls", has_tag=("class", "derived"))
def test_service_inheritance(
    service_cls: type[BlockStorageService]
    | type[ComputeService]
    | type[IdentityService]
    | type[NetworkService]
    | type[ObjectStoreService],
) -> None:
    """Test Service inheritance.

    Execute this test for BlockStorageService, ComputeService, NetworkService and
    ObjectStoreService.
    """
    assert issubclass(service_cls, Service)


@parametrize_with_cases("service_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag="attr")
def test_service_attr(
    service_cls: type[Service]
    | type[BlockStorageService]
    | type[ComputeService]
    | type[IdentityService]
    | type[NetworkService]
    | type[ObjectStoreService],
    attr: str,
) -> None:
    """Test attribute values (default and set)."""
    d = service_model_dict(attr)
    item = service_cls(**d)
    assert isinstance(item, service_cls)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")
    assert item.name == d.get("name")

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("service_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_service_missing_mandatory_attr(
    service_cls: type[Service]
    | type[BlockStorageService]
    | type[ComputeService]
    | type[IdentityService]
    | type[NetworkService]
    | type[ObjectStoreService],
    attr: str,
) -> None:
    """Test Service required attributes.

    Creating a model without required values raises a RequiredProperty error.
    Execute this test on Service, PrivateService and SharedService.
    """
    err_msg = f"property '{attr}' on objects of class {service_cls.__name__}"
    d = service_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        service_cls(**d).save()


@parametrize_with_cases("service_model", has_tag="model")
def test_rel_def(
    service_model: Service
    | BlockStorageService
    | ComputeService
    | IdentityService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Test relationships definition.

    Execute this test on Service, BlockStorageService, ComputeService, IdentityService,
    NetworkService and ObjectStoreService.
    """
    assert isinstance(service_model.region, RelationshipManager)
    assert service_model.region.name
    assert service_model.region.source
    assert isinstance(service_model.region.source, type(service_model))
    assert service_model.region.source.uid == service_model.uid
    assert service_model.region.definition
    assert service_model.region.definition["node_class"] == Region


@parametrize_with_cases("service_model", has_tag="model")
def test_required_rel(
    service_model: Service
    | BlockStorageService
    | ComputeService
    | IdentityService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    Execute this test on Service, BlockStorageService, ComputeService, IdentityService,
    NetworkService and ObjectStoreService.
    """
    with pytest.raises(CardinalityViolation):
        service_model.region.all()
    with pytest.raises(CardinalityViolation):
        service_model.region.single()


@parametrize_with_cases("service_model", has_tag="model")
def test_single_linked_region(
    service_model: Service
    | BlockStorageQuota
    | ComputeQuota
    | IdentityService
    | NetworkQuota
    | ObjectStoreQuota,
    region_model: Region,
) -> None:
    """Verify `region` relationship works correctly.

    Connect a single Region to a Service.
    Execute this test on Service, BlockStorageService, ComputeService, IdentityService,
    NetworkService and ObjectStoreService.
    """
    r = service_model.region.connect(region_model)
    assert r is True

    assert len(service_model.region.all()) == 1
    region = service_model.region.single()
    assert isinstance(region, Region)
    assert region.uid == region_model.uid


@parametrize_with_cases("service_model", has_tag="model")
def test_multiple_linked_regions(
    service_model: BlockStorageService
    | ComputeService
    | IdentityService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Verify `region` relationship works correctly.

    Trying to connect multiple Region to a Service raises an
    AttemptCardinalityViolation error.
    Execute this test on Service, BlockStorageService, ComputeService, IdentityService,
    NetworkService and ObjectStoreService.
    """
    item = Region(**region_model_dict()).save()
    service_model.region.connect(item)
    item = Region(**region_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        service_model.region.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        service_model.region.connect(item)
        with pytest.raises(CardinalityViolation):
            service_model.region.all()


def test_block_storage_default_attr() -> None:
    """Test BlockStorageService specific attribute values and relationships"""
    d = service_model_dict()
    item = BlockStorageService(**d)
    assert item.type == ServiceType.BLOCK_STORAGE.value


def test_block_storage_rel_def(
    block_storage_service_model: BlockStorageService,
) -> None:
    """Test relationships definition."""
    assert isinstance(block_storage_service_model.quotas, RelationshipManager)
    assert block_storage_service_model.quotas.name
    assert block_storage_service_model.quotas.source
    assert isinstance(block_storage_service_model.quotas.source, BlockStorageService)
    assert (
        block_storage_service_model.quotas.source.uid == block_storage_service_model.uid
    )
    assert block_storage_service_model.quotas.definition
    assert (
        block_storage_service_model.quotas.definition["node_class"] == BlockStorageQuota
    )


def test_compute_default_attr() -> None:
    """Test ComputeService specific attribute values and relationships"""
    d = service_model_dict()
    item = ComputeService(**d)
    assert item.type == ServiceType.COMPUTE.value


def test_compute_rel_def(
    compute_service_model: ComputeService,
) -> None:
    """Test relationships definition."""
    assert isinstance(compute_service_model.flavors, RelationshipManager)
    assert compute_service_model.flavors.name
    assert compute_service_model.flavors.source
    assert isinstance(compute_service_model.flavors.source, ComputeService)
    assert compute_service_model.flavors.source.uid == compute_service_model.uid
    assert compute_service_model.flavors.definition
    assert compute_service_model.flavors.definition["node_class"] == Flavor

    assert isinstance(compute_service_model.images, RelationshipManager)
    assert compute_service_model.images.name
    assert compute_service_model.images.source
    assert isinstance(compute_service_model.images.source, ComputeService)
    assert compute_service_model.images.source.uid == compute_service_model.uid
    assert compute_service_model.images.definition
    assert compute_service_model.images.definition["node_class"] == Image

    assert isinstance(compute_service_model.quotas, RelationshipManager)
    assert compute_service_model.quotas.name
    assert compute_service_model.quotas.source
    assert isinstance(compute_service_model.quotas.source, ComputeService)
    assert compute_service_model.quotas.source.uid == compute_service_model.uid
    assert compute_service_model.quotas.definition
    assert compute_service_model.quotas.definition["node_class"] == ComputeQuota


def test_identity_default_attr() -> None:
    """Test IdentityService specific attribute values and relationships"""
    d = service_model_dict()
    item = IdentityService(**d)
    assert item.type == ServiceType.IDENTITY.value


def test_network_default_attr() -> None:
    """Test NetworkService specific attribute values and relationships"""
    d = service_model_dict()
    item = NetworkService(**d)
    assert item.type == ServiceType.NETWORK.value


def test_network_rel_def(
    network_service_model: NetworkService,
) -> None:
    """Test relationships definition."""
    assert isinstance(network_service_model.networks, RelationshipManager)
    assert network_service_model.quotas.name
    assert network_service_model.quotas.source
    assert isinstance(network_service_model.quotas.source, NetworkService)
    assert network_service_model.quotas.source.uid == network_service_model.uid
    assert network_service_model.quotas.definition
    assert network_service_model.quotas.definition["node_class"] == NetworkQuota

    assert isinstance(network_service_model.quotas, RelationshipManager)
    assert network_service_model.networks.name
    assert network_service_model.networks.source
    assert isinstance(network_service_model.networks.source, NetworkService)
    assert network_service_model.networks.source.uid == network_service_model.uid
    assert network_service_model.networks.definition
    assert network_service_model.networks.definition["node_class"] == Network


def test_object_store_default_attr() -> None:
    """Test ObjectStore specific attribute values and relationships"""
    d = service_model_dict()
    item = ObjectStoreService(**d)
    assert item.type == ServiceType.OBJECT_STORE.value


def test_object_store_rel_def(
    object_store_service_model: ObjectStoreService,
) -> None:
    """Test relationships definition."""
    assert isinstance(object_store_service_model.quotas, RelationshipManager)
    assert object_store_service_model.quotas.name
    assert object_store_service_model.quotas.source
    assert isinstance(object_store_service_model.quotas.source, ObjectStoreService)
    assert (
        object_store_service_model.quotas.source.uid == object_store_service_model.uid
    )
    assert object_store_service_model.quotas.definition
    assert (
        object_store_service_model.quotas.definition["node_class"] == ObjectStoreQuota
    )


@parametrize_with_cases("service_model", has_tag=("model", "derived", "with_quotas"))
def test_derived_services_required_rel(
    service_model: BlockStorageService
    | ComputeService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Test derived models required relationships.

    All derived models, except for the IdentityService, have an optional relationships
    called quotas.
    Execute this test on BlockStorageService, ComputeService, NetworkService and
    ObjectStoreService.
    """
    assert len(service_model.quotas.all()) == 0
    assert service_model.quotas.single() is None


def test_compute_optional_rel(compute_service_model: ComputeService) -> None:
    """Test ComputeService specific optional relationships."""
    assert len(compute_service_model.flavors.all()) == 0
    assert compute_service_model.flavors.single() is None
    assert len(compute_service_model.images.all()) == 0
    assert compute_service_model.images.single() is None


def test_network_optional_rel(network_service_model: NetworkService) -> None:
    """Test NetworkService specific optional relationships."""
    assert len(network_service_model.networks.all()) == 0
    assert network_service_model.networks.single() is None


def test_single_linked_block_storage_quota(
    block_storage_service_model: BlockStorageService,
    block_storage_quota_model: BlockStorageQuota,
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect a single BlockStorageQuota to a BlockStorageService.
    """
    r = block_storage_service_model.quotas.connect(block_storage_quota_model)
    assert r is True

    assert len(block_storage_service_model.quotas.all()) == 1
    quotas = block_storage_service_model.quotas.single()
    assert isinstance(quotas, BlockStorageQuota)
    assert quotas.uid == block_storage_quota_model.uid


def test_multiple_linked_block_storage_quotas(
    block_storage_service_model: BlockStorageService,
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect multiple BlockStorageQuota to a BlockStorageService.
    """
    item = BlockStorageQuota(**quota_model_dict()).save()
    block_storage_service_model.quotas.connect(item)
    item = BlockStorageQuota(**quota_model_dict()).save()
    block_storage_service_model.quotas.connect(item)
    assert len(block_storage_service_model.quotas.all()) == 2


def test_single_linked_compute_quota(
    compute_service_model: ComputeService, compute_quota_model: ComputeQuota
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect a single ComputeQuota to a ComputeService.
    """
    r = compute_service_model.quotas.connect(compute_quota_model)
    assert r is True

    assert len(compute_service_model.quotas.all()) == 1
    quotas = compute_service_model.quotas.single()
    assert isinstance(quotas, ComputeQuota)
    assert quotas.uid == compute_quota_model.uid


def test_multiple_linked_compute_quotas(compute_service_model: ComputeService) -> None:
    """Verify `quotas` relationship works correctly.

    Connect multiple ComputeQuota to a ComputeService.
    """
    item = ComputeQuota(**quota_model_dict()).save()
    compute_service_model.quotas.connect(item)
    item = ComputeQuota(**quota_model_dict()).save()
    compute_service_model.quotas.connect(item)
    assert len(compute_service_model.quotas.all()) == 2


@parametrize_with_cases("flavor_model", has_tag=("flavor", "single"))
def test_single_linked_flavor(
    compute_service_model: ComputeService,
    flavor_model: Flavor | PrivateFlavor | SharedFlavor,
) -> None:
    """Verify `flavors` relationship works correctly.

    Connect a single Flavor (private or shared) to a ComputeService.
    """
    r = compute_service_model.flavors.connect(flavor_model)
    assert r is True

    assert len(compute_service_model.flavors.all()) == 1
    flavors = compute_service_model.flavors.single()
    assert isinstance(flavors, type(flavor_model))
    assert flavors.uid == flavor_model.uid


@parametrize_with_cases("flavor_models", has_tag=("flavor", "multi"))
def test_multiple_linked_flavors(
    compute_service_model: ComputeService,
    flavor_models: list[PrivateFlavor | SharedFlavor],
) -> None:
    """Verify `flavors` relationship works correctly.

    Connect multiple Flavor (private and shared) to a ComputeService.
    """
    for flavor_model in flavor_models:
        compute_service_model.flavors.connect(flavor_model)
    assert len(compute_service_model.flavors.all()) == len(flavor_models)


@parametrize_with_cases("image_model", has_tag=("image", "single"))
def test_single_linked_image(
    compute_service_model: ComputeService,
    image_model: Image | PrivateImage | SharedImage,
) -> None:
    """Verify `images` relationship works correctly.

    Connect a single Image (private or shared) to a ComputeService.
    """
    r = compute_service_model.images.connect(image_model)
    assert r is True

    assert len(compute_service_model.images.all()) == 1
    images = compute_service_model.images.single()
    assert isinstance(images, type(image_model))
    assert images.uid == image_model.uid


@parametrize_with_cases("image_models", has_tag=("image", "multi"))
def test_multiple_linked_images(
    compute_service_model: ComputeService, image_models: list[PrivateImage, SharedImage]
) -> None:
    """Verify `images` relationship works correctly.

    Connect multiple Image (private and shared) to a ComputeService.
    """
    for image_model in image_models:
        compute_service_model.images.connect(image_model)
    assert len(compute_service_model.images.all()) == len(image_models)


def test_single_linked_network_quota(
    network_service_model: NetworkService, network_quota_model: NetworkQuota
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect a single NetworkQuota to a NetworkService.
    """
    r = network_service_model.quotas.connect(network_quota_model)
    assert r is True

    assert len(network_service_model.quotas.all()) == 1
    quotas = network_service_model.quotas.single()
    assert isinstance(quotas, NetworkQuota)
    assert quotas.uid == network_quota_model.uid


def test_multiple_linked_network_quotas(network_service_model: NetworkService) -> None:
    """Verify `quotas` relationship works correctly.

    Connect multiple NetworkQuota to a NetworkService.
    """
    item = NetworkQuota(**quota_model_dict()).save()
    network_service_model.quotas.connect(item)
    item = NetworkQuota(**quota_model_dict()).save()
    network_service_model.quotas.connect(item)
    assert len(network_service_model.quotas.all()) == 2


@parametrize_with_cases("network_model", has_tag=("network", "single"))
def test_single_linked_network(
    network_service_model: NetworkService,
    network_model: Network | PrivateNetwork | SharedNetwork,
) -> None:
    """Verify `networks` relationship works correctly.

    Connect a single Network (private or shared) to a NetworkService.
    """
    r = network_service_model.networks.connect(network_model)
    assert r is True

    assert len(network_service_model.networks.all()) == 1
    networks = network_service_model.networks.single()
    assert isinstance(networks, type(network_model))
    assert networks.uid == network_model.uid


@parametrize_with_cases("network_models", has_tag=("network", "multi"))
def test_multiple_linked_networks(
    network_service_model: NetworkService,
    network_models: list[PrivateNetwork, SharedNetwork],
) -> None:
    """Verify `networks` relationship works correctly.

    Connect multiple Network (private and shared) to a NetworkService.
    """
    for network_model in network_models:
        network_service_model.networks.connect(network_model)
    assert len(network_service_model.networks.all()) == len(network_models)


def test_single_linked_object_store_quota(
    object_store_service_model: ObjectStoreService,
    object_store_quota_model: ObjectStoreQuota,
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect a single ObjectStoreQuota to a ObjectStoreService.
    """
    r = object_store_service_model.quotas.connect(object_store_quota_model)
    assert r is True

    assert len(object_store_service_model.quotas.all()) == 1
    quotas = object_store_service_model.quotas.single()
    assert isinstance(quotas, ObjectStoreQuota)
    assert quotas.uid == object_store_quota_model.uid


def test_multiple_linked_object_store_quotas(
    object_store_service_model: ObjectStoreService,
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect multiple ObjectStoreQuota to a ObjectStoreService.
    """
    item = ObjectStoreQuota(**quota_model_dict()).save()
    object_store_service_model.quotas.connect(item)
    item = ObjectStoreQuota(**quota_model_dict()).save()
    object_store_service_model.quotas.connect(item)
    assert len(object_store_service_model.quotas.all()) == 2
