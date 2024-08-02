from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
)
from pytest_cases import parametrize_with_cases

from fed_reg.project.models import Project
from fed_reg.quota.enum import QuotaType
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    Quota,
)
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    NetworkService,
    ObjectStoreService,
)
from tests.create_dict import project_model_dict, quota_model_dict, service_model_dict


@parametrize_with_cases("quota_cls", has_tag=("class", "derived"))
def test_quota_inheritance(
    quota_cls: type[BlockStorageQuota]
    | type[ComputeQuota]
    | type[NetworkQuota]
    | type[ObjectStoreQuota],
) -> None:
    """Test Quota inheritance.

    Execute this test for BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    assert issubclass(quota_cls, Quota)


@parametrize_with_cases("quota_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag="attr")
def test_quota_attr(
    quota_cls: type[Quota]
    | type[BlockStorageQuota]
    | type[ComputeQuota]
    | type[NetworkQuota]
    | type[ObjectStoreQuota],
    attr: str,
) -> None:
    """Test attribute values (default and set).

    Execute this test on Quota, BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    d = quota_model_dict(attr)
    item = quota_cls(**d)
    assert isinstance(item, quota_cls)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.per_user is d.get("per_user", False)
    assert item.usage is d.get("usage", False)

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("quota_model", has_tag="model")
def test_rel_def(
    quota_model: Quota
    | BlockStorageQuota
    | ComputeQuota
    | NetworkQuota
    | ObjectStoreQuota,
) -> None:
    """Test relationships definition.

    Execute this test on Quota, BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    assert isinstance(quota_model.project, RelationshipManager)
    assert quota_model.project.name
    assert quota_model.project.source
    assert isinstance(quota_model.project.source, type(quota_model))
    assert quota_model.project.source.uid == quota_model.uid
    assert quota_model.project.definition
    assert quota_model.project.definition["node_class"] == Project


@parametrize_with_cases("quota_model", has_tag="model")
def test_required_rel(
    quota_model: Quota
    | BlockStorageQuota
    | ComputeQuota
    | NetworkQuota
    | ObjectStoreQuota,
) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    Execute this test on Quota, BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    with pytest.raises(CardinalityViolation):
        quota_model.project.all()
    with pytest.raises(CardinalityViolation):
        quota_model.project.single()


@parametrize_with_cases("quota_model", has_tag="model")
def test_single_linked_project(
    quota_model: Quota
    | BlockStorageQuota
    | ComputeQuota
    | NetworkQuota
    | ObjectStoreQuota,
    project_model: Project,
) -> None:
    """Verify `project` relationship works correctly.

    Connect a single Project to a Quota.
    Execute this test on Quota, BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    r = quota_model.project.connect(project_model)
    assert r is True

    assert len(quota_model.project.all()) == 1
    project = quota_model.project.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


@parametrize_with_cases("quota_model", has_tag="model")
def test_multiple_linked_projects(
    quota_model: Quota
    | BlockStorageQuota
    | ComputeQuota
    | NetworkQuota
    | ObjectStoreQuota,
) -> None:
    """Verify `project` relationship works correctly.

    Trying to connect multiple Project to a Quota raises an
    AttemptCardinalityViolation error.
    Execute this test on Quota, BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    item = Project(**project_model_dict()).save()
    quota_model.project.connect(item)
    item = Project(**project_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        quota_model.project.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        quota_model.project.connect(item)
        with pytest.raises(CardinalityViolation):
            quota_model.project.all()


@parametrize_with_cases("attr", has_tag=("attr", "block_storage"))
def test_block_storage_default_attr(attr: str) -> None:
    """Test BlockStorageQuota specific attribute values."""
    d = quota_model_dict(attr)
    item = BlockStorageQuota(**d)
    assert item.type == QuotaType.BLOCK_STORAGE.value
    assert item.gigabytes is d.get("gigabytes", None)
    assert item.per_volume_gigabytes is d.get("per_volume_gigabytes", None)
    assert item.volumes is d.get("volumes", None)


def test_block_storage_quota_rel_def(
    block_storage_quota_model: BlockStorageQuota,
) -> None:
    """Test relationships definition."""
    assert isinstance(block_storage_quota_model.service, RelationshipManager)
    assert block_storage_quota_model.service.name
    assert block_storage_quota_model.service.source
    assert isinstance(block_storage_quota_model.service.source, BlockStorageQuota)
    assert block_storage_quota_model.service.source.uid == block_storage_quota_model.uid
    assert block_storage_quota_model.service.definition
    assert (
        block_storage_quota_model.service.definition["node_class"]
        == BlockStorageService
    )


@parametrize_with_cases("attr", has_tag=("attr", "compute"))
def test_compute_default_attr(attr: str) -> None:
    """Test ComputeQuota specific attribute values."""
    d = quota_model_dict(attr)
    item = ComputeQuota(**d)
    assert item.type == QuotaType.COMPUTE.value
    assert item.cores is d.get("cores", None)
    assert item.instances is d.get("instances", None)
    assert item.ram is d.get("ram", None)


def test_compute_quota_rel_def(
    compute_quota_model: ComputeQuota,
) -> None:
    """Test relationships definition."""
    assert isinstance(compute_quota_model.service, RelationshipManager)
    assert compute_quota_model.service.name
    assert compute_quota_model.service.source
    assert isinstance(compute_quota_model.service.source, ComputeQuota)
    assert compute_quota_model.service.source.uid == compute_quota_model.uid
    assert compute_quota_model.service.definition
    assert compute_quota_model.service.definition["node_class"] == ComputeService


@parametrize_with_cases("attr", has_tag=("attr", "network"))
def test_network_default_attr(attr: str) -> None:
    """Test NetworkQuota specific attribute values."""
    d = quota_model_dict(attr)
    item = NetworkQuota(**d)
    assert item.type == QuotaType.NETWORK.value
    assert item.public_ips is d.get("public_ips", None)
    assert item.networks is d.get("networks", None)
    assert item.ports is d.get("ports", None)
    assert item.security_groups is d.get("security_groups", None)
    assert item.security_group_rules is d.get("security_group_rules", None)


def test_network_quota_rel_def(
    network_quota_model: NetworkQuota,
) -> None:
    """Test relationships definition."""
    assert isinstance(network_quota_model.service, RelationshipManager)
    assert network_quota_model.service.name
    assert network_quota_model.service.source
    assert isinstance(network_quota_model.service.source, NetworkQuota)
    assert network_quota_model.service.source.uid == network_quota_model.uid
    assert network_quota_model.service.definition
    assert network_quota_model.service.definition["node_class"] == NetworkService


@parametrize_with_cases("attr", has_tag=("attr", "object_store"))
def test_object_store_default_attr(attr: str) -> None:
    """Test ObjectStoreQuota specific attribute values."""
    d = quota_model_dict(attr)
    item = ObjectStoreQuota(**d)
    assert item.type == QuotaType.OBJECT_STORE.value
    assert item.bytes is d.get("bytes", None)
    assert item.containers is d.get("containers", None)
    assert item.objects is d.get("objects", None)


def test_object_store_quota_rel_def(
    object_store_quota_model: ObjectStoreQuota,
) -> None:
    """Test relationships definition."""
    assert isinstance(object_store_quota_model.service, RelationshipManager)
    assert object_store_quota_model.service.name
    assert object_store_quota_model.service.source
    assert isinstance(object_store_quota_model.service.source, ObjectStoreQuota)
    assert object_store_quota_model.service.source.uid == object_store_quota_model.uid
    assert object_store_quota_model.service.definition
    assert (
        object_store_quota_model.service.definition["node_class"] == ObjectStoreService
    )


@parametrize_with_cases("quota_model", has_tag=("model", "derived"))
def test_derived_quotas_required_rel(
    quota_model: BlockStorageQuota | ComputeQuota | NetworkQuota | ObjectStoreQuota,
) -> None:
    """Test derived models required relationships.

    All derived models have a required relationships called service.
    This relationship can be empty but when querying those values, it raises a
    CardinalityViolation error.
    Execute this test on BlockStorageQuota, ComputeQuota, NetworkQuota and
    ObjectStoreQuota.
    """
    with pytest.raises(CardinalityViolation):
        quota_model.service.all()
    with pytest.raises(CardinalityViolation):
        quota_model.service.single()


def test_single_linked_block_storage_service(
    block_storage_quota_model: BlockStorageQuota,
    block_storage_service_model: BlockStorageService,
) -> None:
    """Verify `service` relationship works correctly.

    Connect a single BlockStorageService to a BlockStorageQuota.
    """
    r = block_storage_quota_model.service.connect(block_storage_service_model)
    assert r is True

    assert len(block_storage_quota_model.service.all()) == 1
    service = block_storage_quota_model.service.single()
    assert isinstance(service, BlockStorageService)
    assert service.uid == block_storage_service_model.uid


def test_multiple_linked_block_storage_services(
    block_storage_quota_model: BlockStorageQuota,
) -> None:
    """Verify `service` relationship works correctly.

    Trying to connect multiple BlockStorageService to a BlockStorageQuota raises an
    AttemptCardinalityViolation error.
    """
    item = BlockStorageService(**service_model_dict()).save()
    block_storage_quota_model.service.connect(item)
    item = BlockStorageService(**service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        block_storage_quota_model.service.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        block_storage_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            block_storage_quota_model.service.all()


def test_single_linked_compute_service(
    compute_quota_model: ComputeQuota, compute_service_model: ComputeService
) -> None:
    """Verify `service` relationship works correctly.

    Connect a single ComputeService to a ComputeQuota.
    """
    r = compute_quota_model.service.connect(compute_service_model)
    assert r is True

    assert len(compute_quota_model.service.all()) == 1
    service = compute_quota_model.service.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


def test_multiple_linked_compute_services(compute_quota_model: ComputeQuota) -> None:
    """Verify `service` relationship works correctly.

    Trying to connect multiple ComputeService to a ComputeQuota raises an
    AttemptCardinalityViolation error.
    """
    item = ComputeService(**service_model_dict()).save()
    compute_quota_model.service.connect(item)
    item = ComputeService(**service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        compute_quota_model.service.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        compute_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            compute_quota_model.service.all()


def test_single_linked_network_service(
    network_quota_model: NetworkQuota, network_service_model: NetworkService
) -> None:
    """Verify `service` relationship works correctly.

    Connect a single NetworkService to a NetworkQuota.
    """
    r = network_quota_model.service.connect(network_service_model)
    assert r is True

    assert len(network_quota_model.service.all()) == 1
    service = network_quota_model.service.single()
    assert isinstance(service, NetworkService)
    assert service.uid == network_service_model.uid


def test_multiple_linked_network_services(network_quota_model: NetworkQuota) -> None:
    """Verify `service` relationship works correctly.

    Trying to connect multiple NetworkService to a NetworkQuota raises an
    AttemptCardinalityViolation error.
    """
    item = NetworkService(**service_model_dict()).save()
    network_quota_model.service.connect(item)
    item = NetworkService(**service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        network_quota_model.service.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        network_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            network_quota_model.service.all()


def test_single_linked_object_store_service(
    object_store_quota_model: ObjectStoreQuota,
    object_store_service_model: ObjectStoreService,
) -> None:
    """Verify `service` relationship works correctly.

    Connect a single ObjectStoreService to a ObjectStoreQuota.
    """
    r = object_store_quota_model.service.connect(object_store_service_model)
    assert r is True

    assert len(object_store_quota_model.service.all()) == 1
    service = object_store_quota_model.service.single()
    assert isinstance(service, ObjectStoreService)
    assert service.uid == object_store_service_model.uid


def test_multiple_linked_object_store_services(
    object_store_quota_model: ObjectStoreQuota,
) -> None:
    """Verify `service` relationship works correctly.

    Trying to connect multiple ObjectStoreService to a ObjectStoreQuota raises an
    AttemptCardinalityViolation error.
    """
    item = ObjectStoreService(**service_model_dict()).save()
    object_store_quota_model.service.connect(item)
    item = ObjectStoreService(**service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        object_store_quota_model.service.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        object_store_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            object_store_quota_model.service.all()
