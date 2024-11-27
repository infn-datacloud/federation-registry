from typing import Any
from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    DoesNotExist,
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
from tests.models.utils import (
    network_model_dict,
    quota_model_dict,
    region_model_dict,
    service_model_dict,
)


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
@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_service_valid_attr(
    service_cls: type[Service]
    | type[BlockStorageService]
    | type[ComputeService]
    | type[IdentityService]
    | type[NetworkService]
    | type[ObjectStoreService],
    data: dict[str, Any],
) -> None:
    """Test attribute values (default and set)."""
    item = service_cls(**data)
    assert isinstance(item, service_cls)
    assert item.uid is not None
    assert item.description == data.get("description", "")
    assert item.endpoint == data.get("endpoint")
    assert item.name == data.get("name")

    if isinstance(data, BlockStorageService):
        assert item.type == ServiceType.BLOCK_STORAGE.value
    if isinstance(data, ComputeService):
        assert item.type == ServiceType.COMPUTE.value
    if isinstance(data, IdentityService):
        assert item.type == ServiceType.IDENTITY.value
    if isinstance(data, NetworkService):
        assert item.type == ServiceType.NETWORK.value
    if isinstance(data, ObjectStoreService):
        assert item.type == ServiceType.OBJECT_STORE.value

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("service_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid"))
def test_service_missing_mandatory_attr(
    service_cls: type[Service]
    | type[BlockStorageService]
    | type[ComputeService]
    | type[IdentityService]
    | type[NetworkService]
    | type[ObjectStoreService],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test Service required attributes.

    Creating a model without required values raises a RequiredProperty error.
    Execute this test on Service, PrivateService and SharedService.
    """
    err_msg = f"property '{attr}' on objects of class {service_cls.__name__}"
    with pytest.raises(RequiredProperty, match=err_msg):
        service_cls(**data).save()


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

    if isinstance(service_model, BlockStorageService):
        assert isinstance(service_model.quotas, RelationshipManager)
        assert service_model.quotas.name
        assert service_model.quotas.source
        assert isinstance(service_model.quotas.source, BlockStorageService)
        assert service_model.quotas.source.uid == service_model.uid
        assert service_model.quotas.definition
        assert service_model.quotas.definition["node_class"] == BlockStorageQuota
    if isinstance(service_model, ComputeService):
        assert isinstance(service_model.flavors, RelationshipManager)
        assert service_model.flavors.name
        assert service_model.flavors.source
        assert isinstance(service_model.flavors.source, ComputeService)
        assert service_model.flavors.source.uid == service_model.uid
        assert service_model.flavors.definition
        assert service_model.flavors.definition["node_class"] == Flavor

        assert isinstance(service_model.images, RelationshipManager)
        assert service_model.images.name
        assert service_model.images.source
        assert isinstance(service_model.images.source, ComputeService)
        assert service_model.images.source.uid == service_model.uid
        assert service_model.images.definition
        assert service_model.images.definition["node_class"] == Image

        assert isinstance(service_model.quotas, RelationshipManager)
        assert service_model.quotas.name
        assert service_model.quotas.source
        assert isinstance(service_model.quotas.source, ComputeService)
        assert service_model.quotas.source.uid == service_model.uid
        assert service_model.quotas.definition
        assert service_model.quotas.definition["node_class"] == ComputeQuota
    if isinstance(service_model, IdentityService):
        pass
    if isinstance(service_model, NetworkService):
        assert isinstance(service_model.networks, RelationshipManager)
        assert service_model.quotas.name
        assert service_model.quotas.source
        assert isinstance(service_model.quotas.source, NetworkService)
        assert service_model.quotas.source.uid == service_model.uid
        assert service_model.quotas.definition
        assert service_model.quotas.definition["node_class"] == NetworkQuota

        assert isinstance(service_model.quotas, RelationshipManager)
        assert service_model.networks.name
        assert service_model.networks.source
        assert isinstance(service_model.networks.source, NetworkService)
        assert service_model.networks.source.uid == service_model.uid
        assert service_model.networks.definition
        assert service_model.networks.definition["node_class"] == Network
    if isinstance(service_model, ObjectStoreService):
        assert isinstance(service_model.quotas, RelationshipManager)
        assert service_model.quotas.name
        assert service_model.quotas.source
        assert isinstance(service_model.quotas.source, ObjectStoreService)
        assert service_model.quotas.source.uid == service_model.uid
        assert service_model.quotas.definition
        assert service_model.quotas.definition["node_class"] == ObjectStoreQuota


@parametrize_with_cases("service_model", has_tag="model")
def test_required_rel(
    service_model: Service
    | BlockStorageService
    | ComputeService
    | IdentityService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Test Service required relationships.

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


@parametrize_with_cases("service_model", has_tag=("model", "derived"))
def test_derived_services_optional_rel(
    service_model: BlockStorageService
    | ComputeService
    | NetworkService
    | ObjectStoreService,
) -> None:
    """Test derived models required relationships.

    All derived models, except for the IdentityService, have an optional relationships
    called quotas.
    Each derived model has its own optional relationships.
    Execute this test on BlockStorageService, ComputeService, NetworkService and
    ObjectStoreService.
    """
    if isinstance(service_model, BlockStorageService):
        assert len(service_model.quotas.all()) == 0
        assert service_model.quotas.single() is None
    if isinstance(service_model, ComputeService):
        assert len(service_model.quotas.all()) == 0
        assert service_model.quotas.single() is None
        assert len(service_model.flavors.all()) == 0
        assert service_model.flavors.single() is None
        assert len(service_model.images.all()) == 0
        assert service_model.images.single() is None
    if isinstance(service_model, IdentityService):
        pass
    if isinstance(service_model, NetworkService):
        assert len(service_model.quotas.all()) == 0
        assert service_model.quotas.single() is None
        assert len(service_model.networks.all()) == 0
        assert service_model.networks.single() is None
    if isinstance(service_model, ObjectStoreService):
        assert len(service_model.quotas.all()) == 0
        assert service_model.quotas.single() is None


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


def test_block_storage_pre_delete_hook_remove_quotas(
    block_storage_service_model: BlockStorageService,
) -> None:
    """Delete block storage service and all related quotas."""
    item1 = BlockStorageQuota(**quota_model_dict()).save()
    block_storage_service_model.quotas.connect(item1)
    item2 = BlockStorageQuota(**quota_model_dict()).save()
    block_storage_service_model.quotas.connect(item2)

    assert block_storage_service_model.delete()
    assert block_storage_service_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()


def test_compute_pre_delete_hook_remove_quotas(
    compute_service_model: ComputeService,
) -> None:
    """Delete compute service and all related quotas."""
    item1 = ComputeQuota(**quota_model_dict()).save()
    compute_service_model.quotas.connect(item1)
    item2 = ComputeQuota(**quota_model_dict()).save()
    compute_service_model.quotas.connect(item2)

    assert compute_service_model.delete()
    assert compute_service_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()


def test_compute_pre_delete_hook_remove_flavor(
    compute_service_model: ComputeService, flavor_model: Flavor
) -> None:
    """Delete project and related SLA"""
    compute_service_model.flavors.connect(flavor_model)

    assert compute_service_model.delete()
    assert compute_service_model.deleted
    with pytest.raises(DoesNotExist):
        flavor_model.refresh()


def test_compute_pre_delete_hook_dont_remove_flavor(flavor_model: Flavor) -> None:
    """SLA with multiple projects is not deleted when deleting one project."""
    item1 = ComputeService(**service_model_dict()).save()
    flavor_model.services.connect(item1)
    item2 = ComputeService(**service_model_dict()).save()
    flavor_model.services.connect(item2)

    assert item1.delete()
    assert item1.deleted
    assert flavor_model.services.single() == item2


def test_compute_pre_delete_hook_remove_image(
    compute_service_model: ComputeService, image_model: Image
) -> None:
    """Delete project and related SLA"""
    compute_service_model.images.connect(image_model)

    assert compute_service_model.delete()
    assert compute_service_model.deleted
    with pytest.raises(DoesNotExist):
        image_model.refresh()


def test_compute_pre_delete_hook_dont_remove_image(image_model: Image) -> None:
    """SLA with multiple projects is not deleted when deleting one project."""
    item1 = ComputeService(**service_model_dict()).save()
    image_model.services.connect(item1)
    item2 = ComputeService(**service_model_dict()).save()
    image_model.services.connect(item2)

    assert item1.delete()
    assert item1.deleted
    assert image_model.services.single() == item2


def test_network_pre_delete_hook_remove_quotas(
    network_service_model: NetworkService,
) -> None:
    """Delete network service and all related quotas."""
    item1 = NetworkQuota(**quota_model_dict()).save()
    network_service_model.quotas.connect(item1)
    item2 = NetworkQuota(**quota_model_dict()).save()
    network_service_model.quotas.connect(item2)

    assert network_service_model.delete()
    assert network_service_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()


def test_network_pre_delete_hook_remove_networks(
    network_service_model: NetworkService,
) -> None:
    """Delete network service and all related networks."""
    item1 = Network(**network_model_dict()).save()
    network_service_model.networks.connect(item1)
    item2 = Network(**network_model_dict()).save()
    network_service_model.networks.connect(item2)

    assert network_service_model.delete()
    assert network_service_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()


def test_object_store_pre_delete_hook_remove_quotas(
    object_store_service_model: ObjectStoreService,
) -> None:
    """Delete object store service and all related quotas."""
    item1 = ObjectStoreQuota(**quota_model_dict()).save()
    object_store_service_model.quotas.connect(item1)
    item2 = ObjectStoreQuota(**quota_model_dict()).save()
    object_store_service_model.quotas.connect(item2)

    assert object_store_service_model.delete()
    assert object_store_service_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()
