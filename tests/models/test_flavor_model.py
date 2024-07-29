import pytest
from neomodel import CardinalityViolation, RelationshipManager

from fed_reg.flavor.models import Flavor, PrivateFlavor, PublicFlavor
from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.create_dict import (
    compute_service_model_dict,
    flavor_model_dict,
    project_model_dict,
)


def test_default_attr() -> None:
    d = flavor_model_dict()
    item = Flavor(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.disk == 0
    assert item.ram == 0
    assert item.vcpus == 0
    assert item.swap == 0
    assert item.ephemeral == 0
    assert item.infiniband is False
    assert item.gpus == 0
    assert item.gpu_model is None
    assert item.gpu_vendor is None
    assert item.local_storage is None
    assert isinstance(item.services, RelationshipManager)


def test_required_rel(flavor_model: Flavor) -> None:
    with pytest.raises(CardinalityViolation):
        flavor_model.services.all()
    with pytest.raises(CardinalityViolation):
        flavor_model.services.single()


def test_linked_service(
    flavor_model: Flavor, compute_service_model: ComputeService
) -> None:
    assert flavor_model.services.name
    assert flavor_model.services.source
    assert isinstance(flavor_model.services.source, Flavor)
    assert flavor_model.services.source.uid == flavor_model.uid
    assert flavor_model.services.definition
    assert flavor_model.services.definition["node_class"] == ComputeService

    r = flavor_model.services.connect(compute_service_model)
    assert r is True

    assert len(flavor_model.services.all()) == 1
    service = flavor_model.services.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


def test_multiple_linked_services(flavor_model: Flavor) -> None:
    item = ComputeService(**compute_service_model_dict()).save()
    flavor_model.services.connect(item)
    item = ComputeService(**compute_service_model_dict()).save()
    flavor_model.services.connect(item)
    assert len(flavor_model.services.all()) == 2


def test_public_flavor_default_attr() -> None:
    assert issubclass(PublicFlavor, Flavor)

    d = flavor_model_dict()
    item = PublicFlavor(**d)
    assert item.is_public is True


def test_private_flavor_default_attr() -> None:
    assert issubclass(PrivateFlavor, Flavor)

    d = flavor_model_dict()
    item = PrivateFlavor(**d)
    assert item.is_public is False
    assert isinstance(item.projects, RelationshipManager)


def test_private_flavor_required_rel(private_flavor_model: PrivateFlavor) -> None:
    with pytest.raises(CardinalityViolation):
        private_flavor_model.projects.all()
    with pytest.raises(CardinalityViolation):
        private_flavor_model.projects.single()


def test_linked_project(
    private_flavor_model: PrivateFlavor, project_model: Project
) -> None:
    assert private_flavor_model.projects.name
    assert private_flavor_model.projects.source
    assert isinstance(private_flavor_model.projects.source, PrivateFlavor)
    assert private_flavor_model.projects.source.uid == private_flavor_model.uid
    assert private_flavor_model.projects.definition
    assert private_flavor_model.projects.definition["node_class"] == Project

    r = private_flavor_model.projects.connect(project_model)
    assert r is True

    assert len(private_flavor_model.projects.all()) == 1
    project = private_flavor_model.projects.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(private_flavor_model: PrivateFlavor) -> None:
    item = Project(**project_model_dict()).save()
    private_flavor_model.projects.connect(item)
    item = Project(**project_model_dict()).save()
    private_flavor_model.projects.connect(item)
    assert len(private_flavor_model.projects.all()) == 2
