import pytest
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.models.utils import flavor_model_dict, project_model_dict, service_model_dict


@parametrize_with_cases("flavor_cls", has_tag=("class", "derived"))
def test_flavor_inheritance(
    flavor_cls: type[PrivateFlavor] | type[SharedFlavor],
) -> None:
    """Test PrivateFlavor and SharedFlavor inherits from Flavor."""
    assert issubclass(flavor_cls, Flavor)


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag="attr")
def test_flavor_attr(
    flavor_cls: type[Flavor] | type[PrivateFlavor] | type[SharedFlavor], attr: str
) -> None:
    """Test attribute values (default and set).

    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    d = flavor_model_dict(attr)
    item = flavor_cls(**d)
    assert isinstance(item, flavor_cls)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.disk == d.get("disk", 0)
    assert item.ram == d.get("ram", 0)
    assert item.vcpus == d.get("vcpus", 0)
    assert item.swap == d.get("swap", 0)
    assert item.ephemeral == d.get("ephemeral", 0)
    assert item.infiniband is d.get("infiniband", False)
    assert item.gpus == d.get("gpus", 0)
    assert item.gpu_model is d.get("gpu_model", None)
    assert item.gpu_vendor is d.get("gpu_vendor", None)
    assert item.local_storage is d.get("local_storage", None)

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_flavor_missing_mandatory_attr(
    flavor_cls: type[Flavor] | type[PrivateFlavor] | type[SharedFlavor], attr: str
) -> None:
    """Test Flavor required attributes.

    Creating a model without required values raises a RequiredProperty error.
    Execute this test on Flavor, PrivateFlavor and SharedFlavor.
    """
    err_msg = f"property '{attr}' on objects of class {flavor_cls.__name__}"
    d = flavor_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        flavor_cls(**d).save()


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


def test_shared_flavor_default_attr() -> None:
    """Test SharedFlavor specific attribute values."""
    d = flavor_model_dict()
    item = SharedFlavor(**d)
    assert item.is_public is True


def test_private_flavor_default_attr() -> None:
    """Test SharedFlavor specific attribute values and relationships definition."""
    d = flavor_model_dict()
    item = PrivateFlavor(**d)
    assert item.is_public is False


def test_private_flavor_rel_def(private_flavor_model: PrivateFlavor) -> None:
    """Test relationships definition."""
    assert isinstance(private_flavor_model.projects, RelationshipManager)
    assert private_flavor_model.projects.name
    assert private_flavor_model.projects.source
    assert isinstance(private_flavor_model.projects.source, PrivateFlavor)
    assert private_flavor_model.projects.source.uid == private_flavor_model.uid
    assert private_flavor_model.projects.definition
    assert private_flavor_model.projects.definition["node_class"] == Project


def test_private_flavor_required_rel(private_flavor_model: PrivateFlavor) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        private_flavor_model.projects.all()
    with pytest.raises(CardinalityViolation):
        private_flavor_model.projects.single()


def test_single_linked_project(
    private_flavor_model: PrivateFlavor, project_model: Project
) -> None:
    """Verify `projects` relationship works correctly.

    Connect a single Project to a PrivateFlavor.
    """
    r = private_flavor_model.projects.connect(project_model)
    assert r is True

    assert len(private_flavor_model.projects.all()) == 1
    project = private_flavor_model.projects.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(private_flavor_model: PrivateFlavor) -> None:
    """Verify `services` relationship works correctly.

    Connect a multiple ComputeService to a Flavor.
    """
    item = Project(**project_model_dict()).save()
    private_flavor_model.projects.connect(item)
    item = Project(**project_model_dict()).save()
    private_flavor_model.projects.connect(item)
    assert len(private_flavor_model.projects.all()) == 2
