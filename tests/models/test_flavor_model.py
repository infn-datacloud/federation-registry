from typing import Any

import pytest
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.models.utils import project_model_dict, service_model_dict


@parametrize_with_cases("flavor_cls", has_tag=("class", "derived"))
def test_flavor_inheritance(
    flavor_cls: type[PrivateFlavor] | type[SharedFlavor],
) -> None:
    """Test PrivateFlavor and SharedFlavor inherits from Flavor."""
    assert issubclass(flavor_cls, Flavor)


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_flavor_valid_attr(
    flavor_cls: type[Flavor] | type[PrivateFlavor] | type[SharedFlavor],
    data: dict[str, Any],
) -> None:
    """Test Flavor mandatory and optional attributes.

    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    item = flavor_cls(**data)
    assert isinstance(item, flavor_cls)
    assert item.uid is not None
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid")
    assert item.disk == data.get("disk", 0)
    assert item.ram == data.get("ram", 0)
    assert item.vcpus == data.get("vcpus", 0)
    assert item.swap == data.get("swap", 0)
    assert item.ephemeral == data.get("ephemeral", 0)
    assert item.infiniband is data.get("infiniband", False)
    assert item.gpus == data.get("gpus", 0)
    assert item.gpu_model is data.get("gpu_model", None)
    assert item.gpu_vendor is data.get("gpu_vendor", None)
    assert item.local_storage is data.get("local_storage", None)

    if flavor_cls == SharedFlavor:
        assert item.is_shared
    if flavor_cls == PrivateFlavor:
        assert not item.is_shared

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "invalid"))
def test_flavor_missing_mandatory_attr(
    flavor_cls: type[Flavor] | type[PrivateFlavor] | type[SharedFlavor],
    data: dict[str, Any],
) -> None:
    """Creating a model without required values raises a RequiredProperty error.

    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    with pytest.raises(RequiredProperty):
        flavor_cls(**data).save()


@parametrize_with_cases("flavor_model", has_tag="model")
def test_rel_def(flavor_model: Flavor | PrivateFlavor | SharedFlavor) -> None:
    """Test relationships definition.

    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    assert isinstance(flavor_model.services, RelationshipManager)
    assert flavor_model.services.name
    assert flavor_model.services.source
    assert isinstance(flavor_model.services.source, type(flavor_model))
    assert flavor_model.services.source.uid == flavor_model.uid
    assert flavor_model.services.definition
    assert flavor_model.services.definition["node_class"] == ComputeService

    if isinstance(flavor_model, PrivateFlavor):
        assert isinstance(flavor_model.projects, RelationshipManager)
        assert flavor_model.projects.name
        assert flavor_model.projects.source
        assert isinstance(flavor_model.projects.source, PrivateFlavor)
        assert flavor_model.projects.source.uid == flavor_model.uid
        assert flavor_model.projects.definition
        assert flavor_model.projects.definition["node_class"] == Project


@parametrize_with_cases("flavor_model", has_tag="model")
def test_required_rel(flavor_model: Flavor | PrivateFlavor | SharedFlavor) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    with pytest.raises(CardinalityViolation):
        flavor_model.services.all()
    with pytest.raises(CardinalityViolation):
        flavor_model.services.single()

    if isinstance(flavor_model, PrivateFlavor):
        with pytest.raises(CardinalityViolation):
            flavor_model.projects.all()
        with pytest.raises(CardinalityViolation):
            flavor_model.projects.single()


@parametrize_with_cases("flavor_model", has_tag="model")
def test_single_linked_service(
    flavor_model: Flavor | PrivateFlavor | SharedFlavor,
    compute_service_model: ComputeService,
) -> None:
    """Verify `services` relationship works correctly.

    Connect a single ComputeService to a Flavor.
    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    r = flavor_model.services.connect(compute_service_model)
    assert r is True

    assert len(flavor_model.services.all()) == 1
    service = flavor_model.services.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


@parametrize_with_cases("flavor_model", has_tag=("model", "private"))
def test_single_linked_project(
    flavor_model: PrivateFlavor, project_model: Project
) -> None:
    """Verify `projects` relationship works correctly.

    Connect a single Project to a PrivateFlavor.
    """
    r = flavor_model.projects.connect(project_model)
    assert r is True

    assert len(flavor_model.projects.all()) == 1
    project = flavor_model.projects.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


@parametrize_with_cases("flavor_model", has_tag="model")
def test_multiple_linked_services(
    flavor_model: Flavor | PrivateFlavor | SharedFlavor,
) -> None:
    """Verify `services` relationship works correctly.

    Connect multiple ComputeService to a Flavor.
    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    item = ComputeService(**service_model_dict()).save()
    flavor_model.services.connect(item)
    item = ComputeService(**service_model_dict()).save()
    flavor_model.services.connect(item)
    assert len(flavor_model.services.all()) == 2


@parametrize_with_cases("flavor_model", has_tag=("model", "private"))
def test_multiple_linked_projects(flavor_model: PrivateFlavor) -> None:
    """Verify `projects` relationship works correctly.

    Connect a multiple Project to a PrivateFlavor.
    """
    item = Project(**project_model_dict()).save()
    flavor_model.projects.connect(item)
    item = Project(**project_model_dict()).save()
    flavor_model.projects.connect(item)
    assert len(flavor_model.projects.all()) == 2
