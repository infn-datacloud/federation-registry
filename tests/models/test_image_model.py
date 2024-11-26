from typing import Any

import pytest
from neomodel import CardinalityViolation, RelationshipManager, RequiredProperty
from pytest_cases import parametrize_with_cases

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.models.utils import project_model_dict, service_model_dict


@parametrize_with_cases("image_cls", has_tag=("class", "derived"))
def test_image_inheritance(
    image_cls: type[PrivateImage] | type[SharedImage],
) -> None:
    """Test PrivateImage and SharedImage inherits from Image."""
    assert issubclass(image_cls, Image)


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_image_valid_attr(
    image_cls: type[Image] | type[PrivateImage] | type[SharedImage],
    data: dict[str, Any],
) -> None:
    """Test Image mandatory and optional attributes.

    Execute this test on Image, PrivateImage and SharedImage.
    """
    item = image_cls(**data)
    assert item.uid is not None
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid")
    assert item.os_type is data.get("os_type", None)
    assert item.os_distro is data.get("os_distro", None)
    assert item.os_version is data.get("os_version", None)
    assert item.architecture is data.get("architecture", None)
    assert item.kernel_id is data.get("kernel_id", None)
    assert item.cuda_support is data.get("cuda_support", False)
    assert item.gpu_driver is data.get("gpu_driver", False)
    assert item.tags == data.get("tags", [])

    if image_cls == SharedImage:
        assert item.is_shared
    if image_cls == PrivateImage:
        assert not item.is_shared

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "invalid"))
def test_image_missing_mandatory_attr(
    image_cls: type[Image] | type[PrivateImage] | type[SharedImage],
    data: dict[str, Any],
) -> None:
    """Test Image required attributes.

    Creating a model without required values raises a RequiredProperty error.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    with pytest.raises(RequiredProperty):
        image_cls(**data).save()


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

    if isinstance(image_model, PrivateImage):
        assert isinstance(image_model.projects, RelationshipManager)
        assert image_model.projects.name
        assert image_model.projects.source
        assert isinstance(image_model.projects.source, PrivateImage)
        assert image_model.projects.source.uid == image_model.uid
        assert image_model.projects.definition
        assert image_model.projects.definition["node_class"] == Project


@parametrize_with_cases("image_model", has_tag="model")
def test_required_rel(image_model: Image | PrivateImage | SharedImage) -> None:
    """Test Image required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    with pytest.raises(CardinalityViolation):
        image_model.services.all()
    with pytest.raises(CardinalityViolation):
        image_model.services.single()

    if isinstance(image_model, PrivateImage):
        with pytest.raises(CardinalityViolation):
            image_model.projects.all()
        with pytest.raises(CardinalityViolation):
            image_model.projects.single()


@parametrize_with_cases("image_model", has_tag="model")
def test_single_linked_service(
    image_model: Image | PrivateImage | SharedImage,
    compute_service_model: ComputeService,
) -> None:
    """Verify `services` relationship works correctly.

    Connect a single ComputeService to an Image.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    r = image_model.services.connect(compute_service_model)
    assert r is True

    assert len(image_model.services.all()) == 1
    service = image_model.services.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


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


@parametrize_with_cases("image_model", has_tag="model")
def test_multiple_linked_services(
    image_model: Image | PrivateImage | SharedImage,
) -> None:
    """Verify `services` relationship works correctly.

    Connect a multiple ComputeService to an Image.
    Execute this test on Image, PrivateImage and SharedImage.
    """
    item = ComputeService(**service_model_dict()).save()
    image_model.services.connect(item)
    item = ComputeService(**service_model_dict()).save()
    image_model.services.connect(item)
    assert len(image_model.services.all()) == 2


def test_multiple_linked_projects(private_image_model: PrivateImage) -> None:
    """Verify `services` relationship works correctly.

    Connect a multiple Project to a PrivateImage.
    """
    item = Project(**project_model_dict()).save()
    private_image_model.projects.connect(item)
    item = Project(**project_model_dict()).save()
    private_image_model.projects.connect(item)
    assert len(private_image_model.projects.all()) == 2
