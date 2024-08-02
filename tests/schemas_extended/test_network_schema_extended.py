from uuid import uuid4

import pytest
from neomodel import CardinalityViolation
from pydantic import ValidationError

from fed_reg.models import BaseNodeRead, BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.network.schemas import (
    NetworkBase,
    NetworkBasePublic,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from fed_reg.network.schemas_extended import (
    NetworkReadExtended,
    NetworkReadExtendedPublic,
    NetworkServiceReadExtended,
    NetworkServiceReadExtendedPublic,
    RegionReadExtended,
    RegionReadExtendedPublic,
)
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas_extended import (
    PrivateNetworkCreateExtended,
    SharedNetworkCreateExtended,
)
from fed_reg.region.models import Region
from fed_reg.service.models import NetworkService
from tests.create_dict import network_schema_dict


def test_class_inheritance():
    assert issubclass(PrivateNetworkCreateExtended, PrivateNetworkCreate)
    assert issubclass(SharedNetworkCreateExtended, SharedNetworkCreate)

    assert issubclass(NetworkReadExtended, BaseNodeRead)
    assert issubclass(NetworkReadExtended, BaseReadPrivateExtended)
    assert issubclass(NetworkReadExtended, NetworkBase)

    assert issubclass(NetworkReadExtendedPublic, BaseNodeRead)
    assert issubclass(NetworkReadExtendedPublic, BaseReadPublicExtended)
    assert issubclass(NetworkReadExtendedPublic, NetworkBasePublic)


def test_create_private_extended() -> None:
    d = network_schema_dict()
    d["project"] = uuid4()
    item = PrivateNetworkCreateExtended(**d)
    assert item.project == d.get("project").hex


def test_invalid_create_private_extended() -> None:
    project = uuid4()
    d = network_schema_dict()
    with pytest.raises(ValidationError):
        PrivateNetworkCreateExtended(**d)
    with pytest.raises(ValidationError):
        PrivateNetworkCreateExtended(**d, project=project, is_shared=True)


def test_create_shared_extended() -> None:
    project = uuid4()
    d = network_schema_dict()
    SharedNetworkCreateExtended(**d)
    # Even if we pass projects they are discarded
    item = SharedNetworkCreateExtended(**d, project=project)
    with pytest.raises(AttributeError):
        item.__getattribute__("projects")


def test_invalid_create_shared_extended() -> None:
    d = network_schema_dict()
    with pytest.raises(ValidationError):
        SharedNetworkCreateExtended(**d, is_shared=False)


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


def test_network_serv_read_ext(
    provider_model: Provider,
    region_model: Region,
    network_service_model: NetworkService,
):
    with pytest.raises(CardinalityViolation):
        NetworkServiceReadExtended.from_orm(network_service_model)
    region_model.services.connect(network_service_model)
    with pytest.raises(CardinalityViolation):
        NetworkServiceReadExtended.from_orm(network_service_model)
    provider_model.regions.connect(region_model)
    NetworkServiceReadExtended.from_orm(network_service_model)


def test_network_serv_read_ext_public(
    provider_model: Provider,
    region_model: Region,
    network_service_model: NetworkService,
):
    with pytest.raises(CardinalityViolation):
        NetworkServiceReadExtendedPublic.from_orm(network_service_model)
    region_model.services.connect(network_service_model)
    with pytest.raises(CardinalityViolation):
        NetworkServiceReadExtendedPublic.from_orm(network_service_model)
    provider_model.regions.connect(region_model)
    NetworkServiceReadExtendedPublic.from_orm(network_service_model)


def test_read_shared_ext(
    shared_network_model: SharedNetwork,
    network_service_model: NetworkService,
    region_model: Region,
    provider_model: Provider,
) -> None:
    provider_model.regions.connect(region_model)
    region_model.services.connect(network_service_model)
    network_service_model.networks.connect(shared_network_model)

    item = NetworkReadExtendedPublic.from_orm(shared_network_model)
    assert item.project is None
    assert item.service is not None

    item = NetworkReadExtended.from_orm(shared_network_model)
    assert item.is_shared is True
    assert item.project is None
    assert item.service is not None


def test_read_private_ext(
    private_network_model: PrivateNetwork,
    project_model: Project,
    network_service_model: NetworkService,
    region_model: Region,
    provider_model: Provider,
) -> None:
    provider_model.regions.connect(region_model)
    region_model.services.connect(network_service_model)
    network_service_model.networks.connect(private_network_model)
    private_network_model.project.connect(project_model)

    item = NetworkReadExtendedPublic.from_orm(private_network_model)
    assert item.project is not None
    assert item.service is not None

    item = NetworkReadExtended.from_orm(private_network_model)
    assert item.is_shared is False
    assert item.project is not None
    assert item.service is not None


def test_read_ext(
    network_model: Network,
    network_service_model: NetworkService,
    region_model: Region,
    provider_model: Provider,
) -> None:
    provider_model.regions.connect(region_model)
    region_model.services.connect(network_service_model)
    network_service_model.networks.connect(network_model)

    item = NetworkReadExtendedPublic.from_orm(network_model)
    assert item.project is None
    assert item.service is not None

    item = NetworkReadExtended.from_orm(network_model)
    assert item.is_shared is None
    assert item.project is None
    assert item.service is not None
