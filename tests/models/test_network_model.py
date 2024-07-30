from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
)

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.service.models import NetworkService
from tests.create_dict import (
    network_model_dict,
    network_service_model_dict,
    project_model_dict,
)


def test_default_attr() -> None:
    d = network_model_dict()
    item = Network(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.is_router_external is False
    assert item.is_default is False
    assert item.mtu is None
    assert item.proxy_host is None
    assert item.proxy_user is None
    assert item.tags == []
    assert isinstance(item.service, RelationshipManager)


def test_required_rel(network_model: Network) -> None:
    with pytest.raises(CardinalityViolation):
        network_model.service.all()
    with pytest.raises(CardinalityViolation):
        network_model.service.single()


def test_linked_service(
    network_model: Network, network_service_model: NetworkService
) -> None:
    assert network_model.service.name
    assert network_model.service.source
    assert isinstance(network_model.service.source, Network)
    assert network_model.service.source.uid == network_model.uid
    assert network_model.service.definition
    assert network_model.service.definition["node_class"] == NetworkService

    r = network_model.service.connect(network_service_model)
    assert r is True

    assert len(network_model.service.all()) == 1
    service = network_model.service.single()
    assert isinstance(service, NetworkService)
    assert service.uid == network_service_model.uid


def test_multiple_linked_services(network_model: Network) -> None:
    item = NetworkService(**network_service_model_dict()).save()
    network_model.service.connect(item)
    item = NetworkService(**network_service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        network_model.service.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        network_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            network_model.service.all()


def test_shared_network_default_attr() -> None:
    assert issubclass(SharedNetwork, Network)

    d = network_model_dict()
    item = SharedNetwork(**d)
    assert item.is_shared is True


def test_private_network_default_attr() -> None:
    assert issubclass(PrivateNetwork, Network)

    d = network_model_dict()
    item = PrivateNetwork(**d)
    assert item.is_shared is False
    assert isinstance(item.project, RelationshipManager)


def test_private_network_required_rel(private_network_model: PrivateNetwork) -> None:
    with pytest.raises(CardinalityViolation):
        private_network_model.project.all()
    with pytest.raises(CardinalityViolation):
        private_network_model.project.single()


def test_linked_project(
    private_network_model: PrivateNetwork, project_model: Project
) -> None:
    assert private_network_model.project.name
    assert private_network_model.project.source
    assert isinstance(private_network_model.project.source, PrivateNetwork)
    assert private_network_model.project.source.uid == private_network_model.uid
    assert private_network_model.project.definition
    assert private_network_model.project.definition["node_class"] == Project

    r = private_network_model.project.connect(project_model)
    assert r is True

    assert len(private_network_model.project.all()) == 1
    project = private_network_model.project.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(private_network_model: PrivateNetwork) -> None:
    item = Project(**project_model_dict()).save()
    private_network_model.project.connect(item)
    item = Project(**project_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        private_network_model.project.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        private_network_model.project.connect(item)
        with pytest.raises(CardinalityViolation):
            private_network_model.project.all()
