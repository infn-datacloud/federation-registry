from uuid import UUID

import pytest
from neomodel import CardinalityViolation
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.flavor.schemas import (
    FlavorBase,
    FlavorBasePublic,
    PrivateFlavorCreate,
    SharedFlavorCreate,
)
from fed_reg.flavor.schemas_extended import (
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    FlavorReadExtended,
    FlavorReadExtendedPublic,
    RegionReadExtended,
    RegionReadExtendedPublic,
)
from fed_reg.models import BaseNodeRead, BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas_extended import (
    PrivateFlavorCreateExtended,
    SharedFlavorCreateExtended,
)
from fed_reg.region.models import Region
from fed_reg.service.models import ComputeService
from tests.create_dict import flavor_schema_dict


def test_class_inheritance():
    assert issubclass(PrivateFlavorCreateExtended, PrivateFlavorCreate)
    assert issubclass(SharedFlavorCreateExtended, SharedFlavorCreate)

    assert issubclass(FlavorReadExtended, BaseNodeRead)
    assert issubclass(FlavorReadExtended, BaseReadPrivateExtended)
    assert issubclass(FlavorReadExtended, FlavorBase)

    assert issubclass(FlavorReadExtendedPublic, BaseNodeRead)
    assert issubclass(FlavorReadExtendedPublic, BaseReadPublicExtended)
    assert issubclass(FlavorReadExtendedPublic, FlavorBasePublic)


@parametrize_with_cases("projects", has_tag=["create_extended"])
def test_create_private_extended(projects: list[UUID]) -> None:
    d = flavor_schema_dict()
    d["projects"] = projects
    item = PrivateFlavorCreateExtended(**d)
    assert item.projects == [i.hex for i in projects]


def test_invalid_create_private_extended(projects: list[UUID]) -> None:
    d = flavor_schema_dict()
    with pytest.raises(ValidationError):
        PrivateFlavorCreateExtended(**d)
    with pytest.raises(ValidationError):
        PrivateFlavorCreateExtended(**d, projects=projects, is_public=True)


def test_create_shared_extended() -> None:
    d = flavor_schema_dict()
    SharedFlavorCreateExtended(**d)


def test_invalid_create_shared_extended(projects: list[UUID]) -> None:
    d = flavor_schema_dict()
    with pytest.raises(ValidationError):
        SharedFlavorCreateExtended(**d, projects=projects)
    with pytest.raises(ValidationError):
        SharedFlavorCreateExtended(**d, is_public=False)


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
    shared_flavor_model: SharedFlavor,
    services: list[ComputeService],
    region_model: Region,
    provider_model: Provider,
) -> None:
    for service in services:
        provider_model.regions.connect(region_model)
        region_model.services.connect(service)
        service.flavors.connect(shared_flavor_model)

    item = FlavorReadExtendedPublic.from_orm(shared_flavor_model)
    assert len(item.projects) == 0
    assert len(item.services) == len(services)

    item = FlavorReadExtended.from_orm(shared_flavor_model)
    assert item.is_public is True
    assert len(item.projects) == 0
    assert len(item.services) == len(services)


@parametrize_with_cases("services", has_tag="services")
@parametrize_with_cases("projects", has_tag="projects")
def test_read_private_ext(
    private_flavor_model: PrivateFlavor,
    projects: list[Project],
    services: list[ComputeService],
    region_model: Region,
    provider_model: Provider,
) -> None:
    for service in services:
        provider_model.regions.connect(region_model)
        region_model.services.connect(service)
        service.flavors.connect(private_flavor_model)
    for project in projects:
        private_flavor_model.projects.connect(project)

    item = FlavorReadExtendedPublic.from_orm(private_flavor_model)
    assert len(item.projects) == len(projects)
    assert len(item.services) == len(services)

    item = FlavorReadExtended.from_orm(private_flavor_model)
    assert item.is_public is False
    assert len(item.projects) == len(projects)
    assert len(item.services) == len(services)


@parametrize_with_cases("services", has_tag="services")
def test_read_ext(
    flavor_model: Flavor,
    services: list[ComputeService],
    region_model: Region,
    provider_model: Provider,
) -> None:
    for service in services:
        provider_model.regions.connect(region_model)
        region_model.services.connect(service)
        service.flavors.connect(flavor_model)

    item = FlavorReadExtendedPublic.from_orm(flavor_model)
    assert len(item.projects) == 0
    assert len(item.services) == len(services)

    item = FlavorReadExtended.from_orm(flavor_model)
    assert item.is_public is None
    assert len(item.projects) == 0
    assert len(item.services) == len(services)
