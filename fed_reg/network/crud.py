"""Module with Create, Read, Update and Delete operations for a Network."""

from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.network.schemas import (
    NetworkUpdate,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import PrivateNetworkCreateExtended
from fedreg.service.models import NetworkService

from fed_reg.crud import CRUDBase, CRUDMultiProject, CRUDPrivateSharedDispatcher


class CRUDPrivateNetwork(
    CRUDMultiProject[
        PrivateNetwork,
        PrivateNetworkCreate,
        PrivateNetworkCreateExtended,
        NetworkUpdate,
    ]
):
    """Private Network Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: PrivateNetworkCreateExtended,
        service: NetworkService,
        provider_projects: list[Project],
    ) -> PrivateNetwork:
        """Create a new Network.

        At first check that a network with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        network. In any case connect the network to the given service and to any
        received project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"

        db_obj = service.networks.get_or_none(uuid=obj_in.uuid)
        db_region = service.region.single()
        db_provider = db_region.provider.single()
        assert db_obj is None, (
            f"A private network with uuid {obj_in.uuid} belonging to provider "
            f"{db_provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)

        db_obj.service.connect(service)
        self._connect_projects(
            db_obj=db_obj,
            input_uuids=obj_in.projects,
            provider_projects=provider_projects,
        )

        return db_obj


class CRUDSharedNetwork(CRUDBase[SharedNetwork, SharedNetworkCreate, NetworkUpdate]):
    """Network Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: SharedNetworkCreate, service: NetworkService
    ) -> SharedNetwork:
        """Create a new Network.

        At first check that a network with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        network. In any case connect the network to the given service and to any
        received project.
        """
        db_obj = service.networks.get_or_none(uuid=obj_in.uuid)
        db_region = service.region.single()
        db_provider = db_region.provider.single()
        assert db_obj is None, (
            f"A shared network with uuid {obj_in.uuid} belonging to provider "
            f"{db_provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)

        db_obj.service.connect(service)

        return db_obj


class CRUDNetwork(
    CRUDPrivateSharedDispatcher[
        PrivateNetwork,
        SharedNetwork,
        CRUDPrivateNetwork,
        CRUDSharedNetwork,
        PrivateNetworkCreateExtended,
        SharedNetworkCreate,
        NetworkUpdate,
    ]
):
    """Private and Shared Network Create, Read, Update and Delete operations."""


private_network_mng = CRUDPrivateNetwork(
    model=PrivateNetwork,
    create_schema=PrivateNetworkCreate,
    update_schema=NetworkUpdate,
)

shared_network_mng = CRUDSharedNetwork(
    model=SharedNetwork, create_schema=SharedNetworkCreate, update_schema=NetworkUpdate
)
network_mgr = CRUDNetwork(
    private_mgr=private_network_mng,
    shared_mgr=shared_network_mng,
    shared_model=SharedNetwork,
    shared_create_schema=SharedNetworkCreate,
)
