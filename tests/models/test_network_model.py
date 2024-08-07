from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
)

from fed_reg.network.models import Network
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
    assert item.is_shared is True
    assert item.is_router_external is False
    assert item.is_default is False
    assert item.mtu is None
    assert item.proxy_host is None
    assert item.proxy_user is None
    assert item.tags == []
    assert isinstance(item.project, RelationshipManager)
    assert isinstance(item.service, RelationshipManager)


def test_required_rel(network_model: Network) -> None:
    with pytest.raises(CardinalityViolation):
        network_model.service.all()
    with pytest.raises(CardinalityViolation):
        network_model.service.single()


def test_optional_rel(network_model: Network) -> None:
    assert len(network_model.project.all()) == 0
    assert network_model.project.single() is None


def test_linked_project(network_model: Network, project_model: Project) -> None:
    assert network_model.project.name
    assert network_model.project.source
    assert isinstance(network_model.project.source, Network)
    assert network_model.project.source.uid == network_model.uid
    assert network_model.project.definition
    assert network_model.project.definition["node_class"] == Project

    r = network_model.project.connect(project_model)
    assert r is True

    assert len(network_model.project.all()) == 1
    project = network_model.project.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(network_model: Network) -> None:
    item = Project(**project_model_dict()).save()
    network_model.project.connect(item)
    item = Project(**project_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        network_model.project.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        network_model.project.connect(item)
        with pytest.raises(CardinalityViolation):
            network_model.project.all()


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
