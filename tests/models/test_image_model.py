import pytest
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize_with_cases

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.create_dict import image_model_dict, project_model_dict, service_model_dict


@parametrize_with_cases("image_cls", has_tag=("class", "derived"))
def test_image_inheritance(
    image_cls: type[PrivateImage] | type[SharedImage],
) -> None:
    """Test PrivateImage and SharedImage inherits from Image."""
    assert issubclass(image_cls, Image)


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag="attr")
def test_image_attr(
    image_cls: type[Image] | type[PrivateImage] | type[SharedImage], attr: str
) -> None:
    """Test attribute values (default and set).

    Execute this test on Image, PrivateImage and SharedImage.
    """
    d = image_model_dict(attr)
    item = image_cls(**d)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.os_type is d.get("os_type", None)
    assert item.os_distro is d.get("os_distro", None)
    assert item.os_version is d.get("os_version", None)
    assert item.architecture is d.get("architecture", None)
    assert item.kernel_id is d.get("kernel_id", None)
    assert item.cuda_support is d.get("cuda_support", False)
    assert item.gpu_driver is d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_image_missing_mandatory_attr(
    image_cls: type[Image] | type[PrivateImage] | type[SharedImage], attr: str
) -> None:
    """Test Image required attributes.

    Creating a model without required values raises a RequiredProperty error.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    err_msg = f"property '{attr}' on objects of class {image_cls.__name__}"
    d = image_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        image_cls(**d).save()


@parametrize_with_cases("image_model", has_tag="model")
def test_rel_def(image_model: Image | PrivateImage | SharedImage) -> None:
    """Test relationships definition.

    Execute this test on Image, PrivateImage and SharedImage.
    """
    assert isinstance(image_model.services, RelationshipManager)
    assert image_model.services.name
    assert image_model.services.source
    assert isinstance(image_model.services.source, type(image_model))
    assert image_model.services.source.uid == image_model.uid
    assert image_model.services.definition
    assert image_model.services.definition["node_class"] == ComputeService


@parametrize_with_cases("image_model", has_tag="model")
def test_required_rel(image_model: Image | PrivateImage | SharedImage) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    with pytest.raises(CardinalityViolation):
        image_model.services.all()
    with pytest.raises(CardinalityViolation):
        image_model.services.single()


@parametrize_with_cases("image_model", has_tag="model")
def test_single_linked_service(
    image_model: Image | PrivateImage | SharedImage,
    compute_service_model: ComputeService,
) -> None:
    """Verify `services` relationship works correctly.

    Connect a single ComputeService to a Image.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    r = image_model.services.connect(compute_service_model)
    assert r is True

    assert len(image_model.services.all()) == 1
    service = image_model.services.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


@parametrize_with_cases("image_model", has_tag="model")
def test_multiple_linked_services(
    image_model: Image | PrivateImage | SharedImage,
) -> None:
    """Verify `services` relationship works correctly.

    Connect a multiple ComputeService to a Image.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    item = ComputeService(**service_model_dict()).save()
    image_model.services.connect(item)
    item = ComputeService(**service_model_dict()).save()
    image_model.services.connect(item)
    assert len(image_model.services.all()) == 2


def test_shared_image_default_attr() -> None:
    """Test SharedImage specific attribute values."""
    d = image_model_dict()
    item = SharedImage(**d)
    assert item.is_public is True


def test_private_image_default_attr() -> None:
    """Test SharedImage specific attribute values and relationships definition."""
    d = image_model_dict()
    item = PrivateImage(**d)
    assert item.is_public is False


def test_private_image_rel_def(private_image_model: PrivateImage) -> None:
    """Test relationships definition."""
    assert isinstance(private_image_model.projects, RelationshipManager)
    assert private_image_model.projects.name
    assert private_image_model.projects.source
    assert isinstance(private_image_model.projects.source, PrivateImage)
    assert private_image_model.projects.source.uid == private_image_model.uid
    assert private_image_model.projects.definition
    assert private_image_model.projects.definition["node_class"] == Project


def test_private_image_required_rel(private_image_model: PrivateImage) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        private_image_model.projects.all()
    with pytest.raises(CardinalityViolation):
        private_image_model.projects.single()


def test_single_linked_project(
    private_image_model: PrivateImage, project_model: Project
) -> None:
    """Verify `projects` relationship works correctly.

    Connect a single Project to a PrivateImage.
    """
    r = private_image_model.projects.connect(project_model)
    assert r is True

    assert len(private_image_model.projects.all()) == 1
    project = private_image_model.projects.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(private_image_model: PrivateImage) -> None:
    """Verify `services` relationship works correctly.

    Connect a multiple ComputeService to a Image.
    """
    item = Project(**project_model_dict()).save()
    private_image_model.projects.connect(item)
    item = Project(**project_model_dict()).save()
    private_image_model.projects.connect(item)
    assert len(private_image_model.projects.all()) == 2
