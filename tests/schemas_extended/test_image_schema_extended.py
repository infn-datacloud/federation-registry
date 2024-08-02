from uuid import UUID

import pytest
from neomodel import CardinalityViolation
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.image.schemas import (
    ImageBase,
    ImageBasePublic,
    PrivateImageCreate,
    SharedImageCreate,
)
from fed_reg.image.schemas_extended import (
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    ImageReadExtended,
    ImageReadExtendedPublic,
    RegionReadExtended,
    RegionReadExtendedPublic,
)
from fed_reg.models import BaseNodeRead, BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas_extended import (
    PrivateImageCreateExtended,
    SharedImageCreateExtended,
)
from fed_reg.region.models import Region
from fed_reg.service.models import ComputeService
from tests.create_dict import image_schema_dict


def test_class_inheritance():
    assert issubclass(PrivateImageCreateExtended, PrivateImageCreate)
    assert issubclass(SharedImageCreateExtended, SharedImageCreate)

    assert issubclass(ImageReadExtended, BaseNodeRead)
    assert issubclass(ImageReadExtended, BaseReadPrivateExtended)
    assert issubclass(ImageReadExtended, ImageBase)

    assert issubclass(ImageReadExtendedPublic, BaseNodeRead)
    assert issubclass(ImageReadExtendedPublic, BaseReadPublicExtended)
    assert issubclass(ImageReadExtendedPublic, ImageBasePublic)


@parametrize_with_cases("projects", has_tag=["create_extended"])
def test_create_private_extended(projects: list[UUID]) -> None:
    d = image_schema_dict()
    d["projects"] = projects
    item = PrivateImageCreateExtended(**d)
    assert item.projects == [i.hex for i in projects]


def test_invalid_create_private_extended(projects: list[UUID]) -> None:
    d = image_schema_dict()
    with pytest.raises(ValidationError):
        PrivateImageCreateExtended(**d)
    with pytest.raises(ValidationError):
        PrivateImageCreateExtended(**d, projects=projects, is_public=True)


def test_create_shared_extended(projects: list[UUID]) -> None:
    d = image_schema_dict()
    SharedImageCreateExtended(**d)
    # Even if we pass projects they are discarded
    item = SharedImageCreateExtended(**d, projects=projects)
    with pytest.raises(AttributeError):
        item.__getattribute__("projects")


def test_invalid_create_shared_extended() -> None:
    d = image_schema_dict()
    with pytest.raises(ValidationError):
        SharedImageCreateExtended(**d, is_public=False)


def test_region_read_ext(provider_model: Provider, region_model: Region):
    with pytest.raises(CardinalityViolation):
        RegionReadExtended.from_orm(region_model)
    provider_model.regions.connect(region_model)
    RegionReadExtended.from_orm(region_model)


def test_region_read_ext_public(provider_model: Provider, region_model: Region):
    with pytest.raises(CardinalityViolation):
        RegionReadExtendedPublic.from_orm(region_model)
    provider_model.regions.connect(region_model)
    RegionReadExtendedPublic.from_orm(region_model)


def test_compute_serv_read_ext(
    provider_model: Provider,
    region_model: Region,
    compute_service_model: ComputeService,
):
    with pytest.raises(CardinalityViolation):
        ComputeServiceReadExtended.from_orm(compute_service_model)
    region_model.services.connect(compute_service_model)
    with pytest.raises(CardinalityViolation):
        ComputeServiceReadExtended.from_orm(compute_service_model)
    provider_model.regions.connect(region_model)
    ComputeServiceReadExtended.from_orm(compute_service_model)


def test_compute_serv_read_ext_public(
    provider_model: Provider,
    region_model: Region,
    compute_service_model: ComputeService,
):
    with pytest.raises(CardinalityViolation):
        ComputeServiceReadExtendedPublic.from_orm(compute_service_model)
    region_model.services.connect(compute_service_model)
    with pytest.raises(CardinalityViolation):
        ComputeServiceReadExtendedPublic.from_orm(compute_service_model)
    provider_model.regions.connect(region_model)
    ComputeServiceReadExtendedPublic.from_orm(compute_service_model)


@parametrize_with_cases("services", has_tag="services")
def test_read_shared_ext(
    shared_image_model: SharedImage,
    services: list[ComputeService],
    region_model: Region,
    provider_model: Provider,
) -> None:
    for service in services:
        provider_model.regions.connect(region_model)
        region_model.services.connect(service)
        service.images.connect(shared_image_model)

    item = ImageReadExtendedPublic.from_orm(shared_image_model)
    assert len(item.projects) == 0
    assert len(item.services) == len(services)

    item = ImageReadExtended.from_orm(shared_image_model)
    assert item.is_public is True
    assert len(item.projects) == 0
    assert len(item.services) == len(services)


@parametrize_with_cases("services", has_tag="services")
@parametrize_with_cases("projects", has_tag="projects")
def test_read_private_ext(
    private_image_model: PrivateImage,
    projects: list[Project],
    services: list[ComputeService],
    region_model: Region,
    provider_model: Provider,
) -> None:
    for service in services:
        provider_model.regions.connect(region_model)
        region_model.services.connect(service)
        service.images.connect(private_image_model)
    for project in projects:
        private_image_model.projects.connect(project)

    item = ImageReadExtendedPublic.from_orm(private_image_model)
    assert len(item.projects) == len(projects)
    assert len(item.services) == len(services)

    item = ImageReadExtended.from_orm(private_image_model)
    assert item.is_public is False
    assert len(item.projects) == len(projects)
    assert len(item.services) == len(services)


@parametrize_with_cases("services", has_tag="services")
def test_read_ext(
    image_model: Image,
    services: list[ComputeService],
    region_model: Region,
    provider_model: Provider,
) -> None:
    for service in services:
        provider_model.regions.connect(region_model)
        region_model.services.connect(service)
        service.images.connect(image_model)

    item = ImageReadExtendedPublic.from_orm(image_model)
    assert len(item.projects) == 0
    assert len(item.services) == len(services)

    item = ImageReadExtended.from_orm(image_model)
    assert item.is_public is None
    assert len(item.projects) == 0
    assert len(item.services) == len(services)
