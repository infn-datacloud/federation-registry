import pytest
from neomodel import CardinalityViolation, RelationshipManager

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.create_dict import (
    compute_service_model_dict,
    image_model_dict,
    project_model_dict,
)


def test_default_attr() -> None:
    d = image_model_dict()
    item = Image(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid")
    assert item.os_type is None
    assert item.os_distro is None
    assert item.os_version is None
    assert item.architecture is None
    assert item.kernel_id is None
    assert item.cuda_support is False
    assert item.gpu_driver is False
    assert item.tags == []
    assert isinstance(item.services, RelationshipManager)


def test_required_rel(image_model: Image) -> None:
    with pytest.raises(CardinalityViolation):
        image_model.services.all()
    with pytest.raises(CardinalityViolation):
        image_model.services.single()


def test_linked_service(
    image_model: Image, compute_service_model: ComputeService
) -> None:
    assert image_model.services.name
    assert image_model.services.source
    assert isinstance(image_model.services.source, Image)
    assert image_model.services.source.uid == image_model.uid
    assert image_model.services.definition
    assert image_model.services.definition["node_class"] == ComputeService

    r = image_model.services.connect(compute_service_model)
    assert r is True

    assert len(image_model.services.all()) == 1
    service = image_model.services.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


def test_multiple_linked_services(image_model: Image) -> None:
    item = ComputeService(**compute_service_model_dict()).save()
    image_model.services.connect(item)
    item = ComputeService(**compute_service_model_dict()).save()
    image_model.services.connect(item)
    assert len(image_model.services.all()) == 2


def test_public_image_default_attr() -> None:
    assert issubclass(SharedImage, Image)

    d = image_model_dict()
    item = SharedImage(**d)
    assert item.is_public is True


def test_private_image_default_attr() -> None:
    assert issubclass(PrivateImage, Image)

    d = image_model_dict()
    item = PrivateImage(**d)
    assert item.is_public is False
    assert isinstance(item.projects, RelationshipManager)


def test_private_image_required_rel(private_image_model: PrivateImage) -> None:
    with pytest.raises(CardinalityViolation):
        private_image_model.projects.all()
    with pytest.raises(CardinalityViolation):
        private_image_model.projects.single()


def test_linked_project(
    private_image_model: PrivateImage, project_model: Project
) -> None:
    assert private_image_model.projects.name
    assert private_image_model.projects.source
    assert isinstance(private_image_model.projects.source, PrivateImage)
    assert private_image_model.projects.source.uid == private_image_model.uid
    assert private_image_model.projects.definition
    assert private_image_model.projects.definition["node_class"] == Project

    r = private_image_model.projects.connect(project_model)
    assert r is True

    assert len(private_image_model.projects.all()) == 1
    project = private_image_model.projects.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


def test_multiple_linked_projects(private_image_model: PrivateImage) -> None:
    item = Project(**project_model_dict()).save()
    private_image_model.projects.connect(item)
    item = Project(**project_model_dict()).save()
    private_image_model.projects.connect(item)
    assert len(private_image_model.projects.all()) == 2
