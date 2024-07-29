from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
)
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import PrivateFlavor, SharedFlavor
from fed_reg.image.models import PrivateImage, SharedImage
from fed_reg.network.models import Network
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
from tests.create_dict import (
    flavor_model_dict,
    image_model_dict,
    network_model_dict,
    project_model_dict,
    provider_model_dict,
    sla_model_dict,
)


def test_default_attr() -> None:
    d = project_model_dict()
    item = Project(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert isinstance(item.sla, RelationshipManager)
    assert isinstance(item.provider, RelationshipManager)
    assert isinstance(item.quotas, RelationshipManager)
    assert isinstance(item.private_flavors, RelationshipManager)
    assert isinstance(item.private_images, RelationshipManager)
    assert isinstance(item.private_networks, RelationshipManager)


def test_required_rel(project_model: Project) -> None:
    with pytest.raises(CardinalityViolation):
        project_model.provider.all()
    with pytest.raises(CardinalityViolation):
        project_model.provider.single()


def test_optional_rel(project_model: Project) -> None:
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


def test_linked_private_flavor(
    project_model: Project, private_flavor_model: PrivateFlavor
) -> None:
    assert project_model.private_flavors.name
    assert project_model.private_flavors.source
    assert isinstance(project_model.private_flavors.source, Project)
    assert project_model.private_flavors.source.uid == project_model.uid
    assert project_model.private_flavors.definition
    assert project_model.private_flavors.definition["node_class"] == PrivateFlavor

    r = project_model.private_flavors.connect(private_flavor_model)
    assert r is True

    assert len(project_model.private_flavors.all()) == 1
    flavor = project_model.private_flavors.single()
    assert isinstance(flavor, PrivateFlavor)
    assert flavor.uid == private_flavor_model.uid
    assert not flavor.is_public


def test_multiple_linked_private_flavors(project_model: Project) -> None:
    item = PrivateFlavor(**flavor_model_dict()).save()
    project_model.private_flavors.connect(item)
    item = PrivateFlavor(**flavor_model_dict()).save()
    project_model.private_flavors.connect(item)
    assert len(project_model.private_flavors.all()) == 2


def test_linked_public_flavor(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
    public_flavor_model: SharedFlavor,
) -> None:
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)
    compute_service_model.flavors.connect(public_flavor_model)

    public_flavors = project_model.public_flavors()
    assert len(public_flavors) == 1
    flavor = public_flavors[0]
    assert isinstance(flavor, SharedFlavor)
    assert flavor.uid == public_flavor_model.uid


def test_multi_linked_public_flavors(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
) -> None:
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)

    flavor_model = SharedFlavor(**flavor_model_dict()).save()
    compute_service_model.flavors.connect(flavor_model)
    flavor_model = SharedFlavor(**flavor_model_dict()).save()
    compute_service_model.flavors.connect(flavor_model)

    public_flavors = project_model.public_flavors()
    assert len(public_flavors) == 2


def test_priv_pub_flavors_belong_to_diff_lists(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
) -> None:
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)

    flavor_model = SharedFlavor(**flavor_model_dict()).save()
    compute_service_model.flavors.connect(flavor_model)
    flavor_model = PrivateFlavor(**flavor_model_dict()).save()
    project_model.private_flavors.connect(flavor_model)

    assert len(project_model.public_flavors()) == 1
    assert len(project_model.private_flavors.all()) == 1


def test_linked_private_image(
    project_model: Project, private_image_model: PrivateImage
) -> None:
    assert project_model.private_images.name
    assert project_model.private_images.source
    assert isinstance(project_model.private_images.source, Project)
    assert project_model.private_images.source.uid == project_model.uid
    assert project_model.private_images.definition
    assert project_model.private_images.definition["node_class"] == PrivateImage

    r = project_model.private_images.connect(private_image_model)
    assert r is True

    assert len(project_model.private_images.all()) == 1
    image = project_model.private_images.single()
    assert isinstance(image, PrivateImage)
    assert image.uid == private_image_model.uid
    assert not image.is_public


def test_multiple_linked_private_images(project_model: Project) -> None:
    item = PrivateImage(**image_model_dict()).save()
    project_model.private_images.connect(item)
    item = PrivateImage(**image_model_dict()).save()
    project_model.private_images.connect(item)
    assert len(project_model.private_images.all()) == 2


def test_linked_public_image(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
    public_image_model: SharedImage,
) -> None:
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)
    compute_service_model.images.connect(public_image_model)

    public_images = project_model.public_images()
    assert len(public_images) == 1
    image = public_images[0]
    assert isinstance(image, SharedImage)
    assert image.uid == public_image_model.uid


def test_multi_linked_public_images(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
) -> None:
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)

    image_model = SharedImage(**image_model_dict()).save()
    compute_service_model.images.connect(image_model)
    image_model = SharedImage(**image_model_dict()).save()
    compute_service_model.images.connect(image_model)

    public_images = project_model.public_images()
    assert len(public_images) == 2


def test_priv_pub_images_belong_to_diff_lists(
    project_model: Project,
    compute_quota_model: ComputeQuota,
    compute_service_model: ComputeService,
) -> None:
    compute_service_model.quotas.connect(compute_quota_model)
    project_model.quotas.connect(compute_quota_model)

    image_model = SharedImage(**image_model_dict()).save()
    compute_service_model.images.connect(image_model)
    image_model = PrivateImage(**image_model_dict()).save()
    project_model.private_images.connect(image_model)

    assert len(project_model.public_images()) == 1
    assert len(project_model.private_images.all()) == 1


def test_linked_network(project_model: Project, network_model: Network) -> None:
    assert project_model.private_networks.name
    assert project_model.private_networks.source
    assert isinstance(project_model.private_networks.source, Project)
    assert project_model.private_networks.source.uid == project_model.uid
    assert project_model.private_networks.definition
    assert project_model.private_networks.definition["node_class"] == Network

    r = project_model.private_networks.connect(network_model)
    assert r is True

    assert len(project_model.private_networks.all()) == 1
    network = project_model.private_networks.single()
    assert isinstance(network, Network)
    assert network.uid == network_model.uid
    assert not network.is_shared


def test_multiple_linked_networks(project_model: Project) -> None:
    item = Network(**network_model_dict()).save()
    project_model.private_networks.connect(item)
    item = Network(**network_model_dict()).save()
    project_model.private_networks.connect(item)
    assert len(project_model.private_networks.all()) == 2


def test_linked_provider(project_model: Project, provider_model: Provider) -> None:
    assert project_model.provider.name
    assert project_model.provider.source
    assert isinstance(project_model.provider.source, Project)
    assert project_model.provider.source.uid == project_model.uid
    assert project_model.provider.definition
    assert project_model.provider.definition["node_class"] == Provider

    r = project_model.provider.connect(provider_model)
    assert r is True

    assert len(project_model.provider.all()) == 1
    provider = project_model.provider.single()
    assert isinstance(provider, Provider)
    assert provider.uid == provider_model.uid


def test_multiple_linked_provider(project_model: Project) -> None:
    item = Provider(**provider_model_dict()).save()
    project_model.provider.connect(item)
    item = Provider(**provider_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        project_model.provider.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        project_model.provider.connect(item)
        with pytest.raises(CardinalityViolation):
            project_model.provider.all()


def test_linked_sla(project_model: Project, sla_model: SLA) -> None:
    assert project_model.sla.name
    assert project_model.sla.source
    assert isinstance(project_model.sla.source, Project)
    assert project_model.sla.source.uid == project_model.uid
    assert project_model.sla.definition
    assert project_model.sla.definition["node_class"] == SLA

    r = project_model.sla.connect(sla_model)
    assert r is True

    assert len(project_model.sla.all()) == 1
    sla = project_model.sla.single()
    assert isinstance(sla, SLA)
    assert sla.uid == sla_model.uid


def test_multiple_linked_sla(project_model: Project) -> None:
    item = SLA(**sla_model_dict()).save()
    project_model.sla.connect(item)
    item = SLA(**sla_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        project_model.sla.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        project_model.sla.connect(item)
        with pytest.raises(CardinalityViolation):
            project_model.sla.all()


@parametrize_with_cases("quota_model", has_tag="single")
def test_linked_quota(
    project_model: Project,
    quota_model: BlockStorageQuota | ComputeQuota | NetworkQuota | ObjectStoreQuota,
) -> None:
    assert project_model.quotas.name
    assert project_model.quotas.source
    assert isinstance(project_model.quotas.source, Project)
    assert project_model.quotas.source.uid == project_model.uid
    assert project_model.quotas.definition
    assert project_model.quotas.definition["node_class"] == Quota

    r = project_model.quotas.connect(quota_model)
    assert r is True

    assert len(project_model.quotas.all()) == 1
    quota = project_model.quotas.single()
    assert isinstance(quota, Quota)
    assert quota.uid == quota_model.uid


@parametrize_with_cases("quota_models", has_tag="multi")
def test_multiple_linked_quotas(
    project_model: Project,
    quota_models: list[BlockStorageQuota]
    | list[ComputeQuota]
    | list[NetworkQuota]
    | list[ObjectStoreQuota],
) -> None:
    project_model.quotas.connect(quota_models[0])
    project_model.quotas.connect(quota_models[1])
    assert len(project_model.quotas.all()) == 2


def test_linked_public_network(
    project_model: Project,
    network_quota_model: NetworkQuota,
    network_service_model: NetworkService,
) -> None:
    network_service_model.quotas.connect(network_quota_model)
    project_model.quotas.connect(network_quota_model)

    d = network_model_dict()
    d["is_shared"] = True
    network_model = Network(**d).save()
    network_service_model.networks.connect(network_model)

    public_networks = project_model.public_networks()
    assert len(public_networks) == 1
    network = public_networks[0]
    assert isinstance(network, Network)
    assert network.uid == network_model.uid


def test_multi_linked_public_networks(
    project_model: Project,
    network_quota_model: NetworkQuota,
    network_service_model: NetworkService,
) -> None:
    network_service_model.quotas.connect(network_quota_model)
    project_model.quotas.connect(network_quota_model)

    d = network_model_dict()
    d["is_shared"] = True
    network_model = Network(**d).save()
    network_service_model.networks.connect(network_model)

    d = network_model_dict()
    d["is_shared"] = True
    network_model = Network(**d).save()
    network_service_model.networks.connect(network_model)

    public_networks = project_model.public_networks()
    assert len(public_networks) == 2


# ! Current tests does not check if flavor, image and network are privates or publics.
