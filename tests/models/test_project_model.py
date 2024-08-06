from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import PrivateFlavor, SharedFlavor
from fed_reg.image.models import PrivateImage, SharedImage
from fed_reg.network.models import PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    Quota,
)
from fed_reg.service.models import ComputeService, NetworkService
from fed_reg.sla.models import SLA
from tests.models.utils import (
    flavor_model_dict,
    image_model_dict,
    network_model_dict,
    project_model_dict,
    provider_model_dict,
    sla_model_dict,
)


@parametrize_with_cases("attr", has_tag="attr")
def test_project_attr(attr: str) -> None:
    """Test attribute values (default and set)."""
    d = project_model_dict(attr)
    item = Project(**d)
    assert isinstance(item, Project)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_project_missing_mandatory_attr(attr: str) -> None:
    """Test Project required attributes.

    Creating a model without required values raises a RequiredProperty error.
    """
    err_msg = f"property '{attr}' on objects of class {Project.__name__}"
    d = flavor_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        Project(**d).save()


def test_rel_def(project_model: Project) -> None:
    """Test relationships definition."""
    assert isinstance(project_model.sla, RelationshipManager)
    assert project_model.sla.name
    assert project_model.sla.source
    assert isinstance(project_model.sla.source, Project)
    assert project_model.sla.source.uid == project_model.uid
    assert project_model.sla.definition
    assert project_model.sla.definition["node_class"] == SLA

    assert isinstance(project_model.provider, RelationshipManager)
    assert project_model.provider.name
    assert project_model.provider.source
    assert isinstance(project_model.provider.source, Project)
    assert project_model.provider.source.uid == project_model.uid
    assert project_model.provider.definition
    assert project_model.provider.definition["node_class"] == Provider

    assert isinstance(project_model.quotas, RelationshipManager)
    assert project_model.quotas.name
    assert project_model.quotas.source
    assert isinstance(project_model.quotas.source, Project)
    assert project_model.quotas.source.uid == project_model.uid
    assert project_model.quotas.definition
    assert project_model.quotas.definition["node_class"] == Quota

    assert isinstance(project_model.private_flavors, RelationshipManager)
    assert project_model.private_flavors.name
    assert project_model.private_flavors.source
    assert isinstance(project_model.private_flavors.source, Project)
    assert project_model.private_flavors.source.uid == project_model.uid
    assert project_model.private_flavors.definition
    assert project_model.private_flavors.definition["node_class"] == PrivateFlavor

    assert isinstance(project_model.private_images, RelationshipManager)
    assert project_model.private_images.name
    assert project_model.private_images.source
    assert isinstance(project_model.private_images.source, Project)
    assert project_model.private_images.source.uid == project_model.uid
    assert project_model.private_images.definition
    assert project_model.private_images.definition["node_class"] == PrivateImage

    assert isinstance(project_model.private_networks, RelationshipManager)
    assert project_model.private_networks.name
    assert project_model.private_networks.source
    assert isinstance(project_model.private_networks.source, Project)
    assert project_model.private_networks.source.uid == project_model.uid
    assert project_model.private_networks.definition
    assert project_model.private_networks.definition["node_class"] == PrivateNetwork


def test_required_rel(project_model: Project) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        project_model.provider.all()
    with pytest.raises(CardinalityViolation):
        project_model.provider.single()


def test_single_linked_provider(
    project_model: Project, provider_model: Provider
) -> None:
    """Verify `provider` relationship works correctly.

    Connect a single Provider to a Project.
    """
    r = project_model.provider.connect(provider_model)
    assert r is True

    assert len(project_model.provider.all()) == 1
    provider = project_model.provider.single()
    assert isinstance(provider, Provider)
    assert provider.uid == provider_model.uid


def test_multiple_linked_provider(project_model: Project) -> None:
    """Verify `provider` relationship works correctly.

    Trying to connect multiple Provider to a Project raises an
    AttemptCardinalityViolation error.
    """
    item = Provider(**provider_model_dict()).save()
    project_model.provider.connect(item)
    item = Provider(**provider_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        project_model.provider.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        project_model.provider.connect(item)
        with pytest.raises(CardinalityViolation):
            project_model.provider.all()


def test_optional_rel(project_model: Project) -> None:
    """Test Model optional relationships."""
    assert len(project_model.sla.all()) == 0
    assert project_model.sla.single() is None
    assert len(project_model.quotas.all()) == 0
    assert project_model.quotas.single() is None
    assert len(project_model.private_flavors.all()) == 0
    assert project_model.private_flavors.single() is None
    assert len(project_model.private_images.all()) == 0
    assert project_model.private_images.single() is None
    assert len(project_model.private_networks.all()) == 0
    assert project_model.private_networks.single() is None


def test_single_linked_sla(project_model: Project, sla_model: SLA) -> None:
    """Verify `sla` relationship works correctly.

    Connect a single SLA to a Project.
    """
    r = project_model.sla.connect(sla_model)
    assert r is True

    assert len(project_model.sla.all()) == 1
    sla = project_model.sla.single()
    assert isinstance(sla, SLA)
    assert sla.uid == sla_model.uid


def test_multiple_linked_sla(project_model: Project) -> None:
    """Verify `sla` relationship works correctly.

    Trying to connect multiple SLA to a Project raises an
    AttemptCardinalityViolation error.
    """
    item = SLA(**sla_model_dict()).save()
    project_model.sla.connect(item)
    item = SLA(**sla_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        project_model.sla.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        project_model.sla.connect(item)
        with pytest.raises(CardinalityViolation):
            project_model.sla.all()


@parametrize_with_cases("quota_model", has_tag=("quota", "single"))
def test_single_linked_quota(
    project_model: Project,
    quota_model: BlockStorageQuota | ComputeQuota | NetworkQuota | ObjectStoreQuota,
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect a single Quota to a Project.
    Execute this test for these quota types: BlockStorage, Compute, Network and
    ObjectStore.
    """
    r = project_model.quotas.connect(quota_model)
    assert r is True

    assert len(project_model.quotas.all()) == 1
    quota = project_model.quotas.single()
    assert isinstance(quota, Quota)
    assert quota.uid == quota_model.uid


@parametrize_with_cases("quota_models", has_tag=("quota", "multi"))
def test_multiple_linked_quotas(
    project_model: Project,
    quota_models: list[BlockStorageQuota]
    | list[ComputeQuota]
    | list[NetworkQuota]
    | list[ObjectStoreQuota],
) -> None:
    """Verify `quotas` relationship works correctly.

    Connect multiple Quota to a Project.
    Execute this test for these quota types: BlockStorage, Compute, Network and
    ObjectStore.
    """
    for quota_model in quota_models:
        project_model.quotas.connect(quota_model)
    assert len(project_model.quotas.all()) == len(quota_models)


def test_single_linked_private_flavor(
    project_model: Project, private_flavor_model: PrivateFlavor
) -> None:
    """Verify `private_flavors` relationship works correctly.

    Connect a single PrivateFlavor to a Project.
    """
    r = project_model.private_flavors.connect(private_flavor_model)
    assert r is True

    assert len(project_model.private_flavors.all()) == 1
    flavor = project_model.private_flavors.single()
    assert isinstance(flavor, PrivateFlavor)
    assert flavor.uid == private_flavor_model.uid
    assert not flavor.is_public


def test_multiple_linked_private_flavors(project_model: Project) -> None:
    """Verify `private_flavors` relationship works correctly.

    Connect multiple PrivateFlavor to a Project.
    """
    item = PrivateFlavor(**flavor_model_dict()).save()
    project_model.private_flavors.connect(item)
    item = PrivateFlavor(**flavor_model_dict()).save()
    project_model.private_flavors.connect(item)
    assert len(project_model.private_flavors.all()) == 2


def test_single_linked_private_image(
    project_model: Project, private_image_model: PrivateImage
) -> None:
    """Verify `private_images` relationship works correctly.

    Connect a single PrivateImage to a Project.
    """
    r = project_model.private_images.connect(private_image_model)
    assert r is True

    assert len(project_model.private_images.all()) == 1
    image = project_model.private_images.single()
    assert isinstance(image, PrivateImage)
    assert image.uid == private_image_model.uid
    assert not image.is_public


def test_multiple_linked_private_images(project_model: Project) -> None:
    """Verify `private_images` relationship works correctly.

    Connect multiple PrivateImage to a Project.
    """
    item = PrivateImage(**image_model_dict()).save()
    project_model.private_images.connect(item)
    item = PrivateImage(**image_model_dict()).save()
    project_model.private_images.connect(item)
    assert len(project_model.private_images.all()) == 2


def test_single_linked_private_network(
    project_model: Project, private_network_model: PrivateNetwork
) -> None:
    """Verify `private_networks` relationship works correctly.

    Connect a single PrivateNetwork to a Project.
    """
    r = project_model.private_networks.connect(private_network_model)
    assert r is True

    assert len(project_model.private_networks.all()) == 1
    network = project_model.private_networks.single()
    assert isinstance(network, PrivateNetwork)
    assert network.uid == private_network_model.uid
    assert not network.is_shared


def test_multiple_linked_private_networks(project_model: Project) -> None:
    """Verify `private_networks` relationship works correctly.

    Connect multiple PrivateNetwork to a Project.
    """
    item = PrivateNetwork(**network_model_dict()).save()
    project_model.private_networks.connect(item)
    item = PrivateNetwork(**network_model_dict()).save()
    project_model.private_networks.connect(item)
    assert len(project_model.private_networks.all()) == 2


def test_linked_shared_flavors(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
    shared_flavor_model: SharedFlavor,
) -> None:
    """Verify `shared_flavors` function works correctly.

    We detect shared flavors through services connected by at least one quota to the
    target Project.
    """
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)
    compute_service_model.flavors.connect(shared_flavor_model)

    shared_flavors = project_model.shared_flavors()
    assert len(shared_flavors) == 1
    flavor = shared_flavors[0]
    assert isinstance(flavor, SharedFlavor)
    assert flavor.uid == shared_flavor_model.uid

    flavor_model = SharedFlavor(**flavor_model_dict()).save()
    compute_service_model.flavors.connect(flavor_model)
    shared_flavors = project_model.shared_flavors()
    assert len(shared_flavors) == 2


def test_linked_shared_images(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
    shared_image_model: SharedImage,
) -> None:
    """Verify `shared_images` function works correctly.

    We detect shared images through services connected by at least one quota to the
    target Project.
    """
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)
    compute_service_model.images.connect(shared_image_model)

    shared_images = project_model.shared_images()
    assert len(shared_images) == 1
    image = shared_images[0]
    assert isinstance(image, SharedImage)
    assert image.uid == shared_image_model.uid

    image_model = SharedImage(**image_model_dict()).save()
    compute_service_model.images.connect(image_model)
    shared_images = project_model.shared_images()
    assert len(shared_images) == 2


def test_linked_public_networks(
    project_model: Project,
    network_quota_model: NetworkQuota,
    network_service_model: NetworkService,
    shared_network_model: SharedNetwork,
) -> None:
    """Verify `shared_networks` function works correctly.

    We detect shared networks through services connected by at least one quota to the
    target Project.
    """
    network_service_model.quotas.connect(network_quota_model)
    project_model.quotas.connect(network_quota_model)
    network_service_model.networks.connect(shared_network_model)

    shared_networks = project_model.shared_networks()
    assert len(shared_networks) == 1
    network = shared_networks[0]
    assert isinstance(network, SharedNetwork)
    assert network.uid == shared_network_model.uid

    network_model = SharedNetwork(**network_model_dict()).save()
    network_service_model.networks.connect(network_model)
    shared_networks = project_model.shared_networks()
    assert len(shared_networks) == 2


def test_priv_pub_flavors_belong_to_diff_lists(
    project_model: Project,
    private_flavor_model: PrivateFlavor,
    shared_flavor_model: SharedFlavor,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
) -> None:
    """Verify `shared_flavors` function works correctly.

    We detect only SharedFlavor through `shared_flavors`. Private ones are detected
    through the dedicated relationship.
    """
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)
    compute_service_model.flavors.connect(shared_flavor_model)
    compute_service_model.flavors.connect(private_flavor_model)
    project_model.private_flavors.connect(private_flavor_model)
    assert len(project_model.shared_flavors()) == 1
    assert len(project_model.private_flavors.all()) == 1


def test_priv_pub_images_belong_to_diff_lists(
    project_model: Project,
    private_image_model: PrivateImage,
    shared_image_model: SharedImage,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
) -> None:
    """Verify `shared_images` function works correctly.

    We detect only SharedImage through `shared_images`. Private ones are detected
    through the dedicated relationship.
    """
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)
    compute_service_model.images.connect(shared_image_model)
    compute_service_model.images.connect(private_image_model)
    project_model.private_images.connect(private_image_model)
    assert len(project_model.shared_images()) == 1
    assert len(project_model.private_images.all()) == 1


def test_priv_pub_networks_belong_to_diff_lists(
    project_model: Project,
    private_network_model: PrivateNetwork,
    shared_network_model: SharedNetwork,
    network_quota_model: NetworkQuota,
    network_service_model: NetworkService,
) -> None:
    """Verify `shared_networks` function works correctly.

    We detect only SharedNetwork through `shared_networks`. Private ones are detected
    through the dedicated relationship.
    """
    network_service_model.quotas.connect(network_quota_model)
    project_model.quotas.connect(network_quota_model)
    network_service_model.networks.connect(shared_network_model)
    network_service_model.networks.connect(private_network_model)
    project_model.private_networks.connect(private_network_model)
    assert len(project_model.shared_networks()) == 1
    assert len(project_model.private_networks.all()) == 1
