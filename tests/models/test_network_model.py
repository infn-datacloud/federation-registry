from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize_with_cases

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.service.models import NetworkService
from tests.create_dict import network_model_dict, project_model_dict, service_model_dict


@parametrize_with_cases("network_cls", has_tag=("class", "derived"))
def test_network_inheritance(
    network_cls: type[PrivateNetwork] | type[SharedNetwork],
) -> None:
    """Test PrivateNetwork and SharedNetwork inherits from Network."""
    assert issubclass(network_cls, Network)


@parametrize_with_cases("network_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag="attr")
def test_network_attr(
    network_cls: type[Network] | type[PrivateNetwork] | type[SharedNetwork], attr: str
) -> None:
    """Test attribute values (default and set).

    Execute this test on Network, PrivateNetwork and SharedNetwork.
    """
    d = network_model_dict(attr)
    item = network_cls(**d)
    assert isinstance(item, network_cls)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.is_router_external is d.get("is_router_external", False)
    assert item.is_default is d.get("is_default", False)
    assert item.mtu is d.get("mtu", None)
    assert item.proxy_host is d.get("proxy_host", None)
    assert item.proxy_user is d.get("proxy_user", None)
    assert item.tags == d.get("tags", [])

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("network_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_network_missing_mandatory_attr(
    network_cls: type[Network] | type[PrivateNetwork] | type[SharedNetwork], attr: str
) -> None:
    """Test Network required attributes.

    Creating a model without required values raises a RequiredProperty error.
    Execute this test on Network, PrivateNetwork and SharedNetwork.
    """
    err_msg = f"property '{attr}' on objects of class {network_cls.__name__}"
    d = network_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        network_cls(**d).save()


@parametrize_with_cases("network_model", has_tag="model")
def test_rel_def(network_model: Network | PrivateNetwork | SharedNetwork) -> None:
    """Test relationships definition.

    Execute this test on Network, PrivateNetwork and SharedNetwork.
    """
    assert isinstance(network_model.service, RelationshipManager)
    assert network_model.service.name
    assert network_model.service.source
    assert isinstance(network_model.service.source, type(network_model))
    assert network_model.service.source.uid == network_model.uid
    assert network_model.service.definition
    assert network_model.service.definition["node_class"] == NetworkService


@parametrize_with_cases("network_model", has_tag="model")
def test_required_rel(network_model: Network | PrivateNetwork | SharedNetwork) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    Execute this test on Network, PrivateNetwork and SharedNetwork.
    """
    with pytest.raises(CardinalityViolation):
        network_model.service.all()
    with pytest.raises(CardinalityViolation):
        network_model.service.single()


@parametrize_with_cases("network_model", has_tag="model")
def test_single_linked_service(
    network_model: Network | PrivateNetwork | SharedNetwork,
    network_service_model: NetworkService,
) -> None:
    """Verify `service` relationship works correctly.

    Connect a single NetworkService to a Network.
    Execute this test on Network, PrivateNetwork and SharedNetwork.
    """
    r = network_model.service.connect(network_service_model)
    assert r is True

    assert len(network_model.service.all()) == 1
    service = network_model.service.single()
    assert isinstance(service, NetworkService)
    assert service.uid == network_service_model.uid


@parametrize_with_cases("network_model", has_tag="model")
def test_multiple_linked_services_error(
    network_model: Network | PrivateNetwork | SharedNetwork,
) -> None:
    """Verify `service` relationship works correctly.

    Trying to connect multiple NetworkService to a Network raises an
    AttemptCardinalityViolation error.
    Execute this test on Network, PrivateNetwork and SharedNetwork.
    """
    item = NetworkService(**service_model_dict()).save()
    network_model.service.connect(item)
    item = NetworkService(**service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        network_model.service.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        network_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            network_model.service.all()


def test_shared_network_default_attr() -> None:
    """Test SharedNetwork specific attribute values."""
    d = network_model_dict()
    item = SharedNetwork(**d)
    assert item.is_shared is True


def test_private_network_default_attr() -> None:
    """Test SharedNetwork specific attribute values and relationships definition."""
    d = network_model_dict()
    item = PrivateNetwork(**d)
    assert item.is_shared is False


def test_private_network_rel_def(private_network_model: PrivateNetwork) -> None:
    """Test relationships definition."""
    assert isinstance(private_network_model.project, RelationshipManager)
    assert private_network_model.project.name
    assert private_network_model.project.source
    assert isinstance(private_network_model.project.source, PrivateNetwork)
    assert private_network_model.project.source.uid == private_network_model.uid
    assert private_network_model.project.definition
    assert private_network_model.project.definition["node_class"] == Project


def test_private_network_required_rel(private_network_model: PrivateNetwork) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        private_network_model.project.all()
    with pytest.raises(CardinalityViolation):
        private_network_model.project.single()


def test_single_linked_project(
    private_network_model: PrivateNetwork, project_model: Project
) -> None:
    """Verify `projects` relationship works correctly.

    Connect a single Project to a PrivateNetwork.
    """
    r = private_network_model.project.connect(project_model)
    assert r is True

    assert len(private_network_model.project.all()) == 1
    project = private_network_model.project.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(private_network_model: PrivateNetwork) -> None:
    """Verify `services` relationship works correctly.

    Trying to connect multiple Project to a PrivateNetwork raises an
    AttemptCardinalityViolation error.
    """
    item = Project(**project_model_dict()).save()
    private_network_model.project.connect(item)
    item = Project(**project_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        private_network_model.project.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        private_network_model.project.connect(item)
        with pytest.raises(CardinalityViolation):
            private_network_model.project.all()
