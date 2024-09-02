"""Module with Create, Read, Update and Delete operations for a Network."""
from typing import Optional

from fed_reg.crud2 import CRUDInterface
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.network.schemas import (
    NetworkUpdate,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    PrivateNetworkCreateExtended,
    SharedNetworkCreateExtended,
)
from fed_reg.service.models import NetworkService


class CRUDPrivateNetwork(
    CRUDInterface[PrivateNetwork, PrivateNetworkCreate, NetworkUpdate]
):
    """Network Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[PrivateNetwork]:
        return PrivateNetwork

    def create(
        self,
        *,
        obj_in: PrivateNetworkCreateExtended,
        service: NetworkService,
        project: Project,
    ) -> PrivateNetwork:
        """Create a new Network.

        At first check that a network with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        network. In any case connect the network to the given service and to any
        received project.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        db_obj.project.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: PrivateNetwork,
        obj_in: NetworkUpdate | PrivateNetworkCreateExtended,
        project: Project,
        force: bool = False,
    ) -> PrivateNetwork | None:
        """Update Network attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        edit = False
        if force:
            if project != db_obj.project.single():
                db_obj.project.replace(project)
                edit = True

        if isinstance(obj_in, PrivateNetworkCreateExtended):
            obj_in = NetworkUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data


class CRUDSharedNetwork(
    CRUDInterface[SharedNetwork, SharedNetworkCreate, NetworkUpdate]
):
    """Network Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[SharedNetwork]:
        return SharedNetwork

    def create(
        self, *, obj_in: SharedNetworkCreateExtended, service: NetworkService
    ) -> SharedNetwork:
        """Create a new Network.

        At first check that a network with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        network. In any case connect the network to the given service and to any
        received project.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        return db_obj


class CRUDNetwork(
    CRUDInterface[
        Network,
        PrivateNetworkCreateExtended | SharedNetworkCreateExtended,
        NetworkUpdate,
    ]
):
    """Network Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[Network]:
        return Network

    def create(
        self,
        *,
        obj_in: PrivateNetworkCreateExtended | SharedNetworkCreateExtended,
        service: NetworkService,
        project: Optional[Project] = None,
    ) -> Network:
        """Create a new Network.

        Connect the network to the given service and to the optional received project.
        """
        if isinstance(obj_in, PrivateNetworkCreateExtended):
            return CRUDPrivateNetwork().create(
                obj_in=obj_in, service=service, project=project
            )
        return CRUDSharedNetwork().create(obj_in=obj_in, service=service)

    def update(
        self,
        *,
        db_obj: Network,
        obj_in: NetworkUpdate
        | PrivateNetworkCreateExtended
        | SharedNetworkCreateExtended,
        project: Optional[Project] = None,
        force: bool = False,
    ) -> Optional[Network]:
        """Update Network attributes.

        By default do not update relationships or default values. If force is True,
        update linked project and apply default values when explicit.
        """
        if isinstance(obj_in, PrivateNetworkCreateExtended):
            return CRUDPrivateNetwork().update(
                db_obj=db_obj, obj_in=obj_in, project=project, force=force
            )
        elif isinstance(obj_in, SharedNetworkCreateExtended):
            return CRUDSharedNetwork().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return super().update(db_obj=db_obj, obj_in=obj_in, force=force)


private_network_mgr = CRUDPrivateNetwork()
shared_network_mgr = CRUDSharedNetwork()
network_mgr = CRUDNetwork()
