"""Module with Create, Read, Update and Delete operations for a Network."""

from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.network.schemas import (
    NetworkRead,
    NetworkReadPublic,
    NetworkUpdate,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from fedreg.network.schemas_extended import (
    NetworkReadExtended,
    NetworkReadExtendedPublic,
)
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import PrivateNetworkCreateExtended
from fedreg.service.models import NetworkService

from fed_reg.crud import CRUDBase, ResourceMultiProjectsBase


class CRUDPrivateNetwork(
    CRUDBase[
        PrivateNetwork,
        PrivateNetworkCreate,
        NetworkUpdate,
        NetworkRead,
        NetworkReadPublic,
        NetworkReadExtended,
        NetworkReadExtendedPublic,
    ],
    ResourceMultiProjectsBase[PrivateNetwork, PrivateNetworkCreateExtended],
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
        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # It's indifferent which service, we want to reach the provider
            db_service = db_obj.service.single()
            db_region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)
            else:
                raise ValueError(
                    f"A private network with uuid {obj_in.uuid} belonging to provider "
                    f"{db_provider1.name} already exists"
                )

        db_obj.service.connect(service)
        super()._connect_projects(
            db_obj=db_obj,
            input_uuids=obj_in.projects,
            provider_projects=provider_projects,
        )

        return db_obj

    def update(
        self,
        *,
        db_obj: PrivateNetwork,
        obj_in: PrivateNetworkCreateExtended,
        provider_projects: list[Project],
    ) -> PrivateNetwork | None:
        """Update Network attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        db_obj = super()._update_projects(
            db_obj=db_obj, obj_in=obj_in, provider_projects=provider_projects
        )
        obj_in = NetworkUpdate.parse_obj(obj_in)
        db_obj = super().update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj


class CRUDSharedNetwork(
    CRUDBase[
        SharedNetwork,
        SharedNetworkCreate,
        NetworkUpdate,
        NetworkRead,
        NetworkReadPublic,
        NetworkReadExtended,
        NetworkReadExtendedPublic,
    ]
):
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
        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # It's indifferent which service, we want to reach the provider
            db_service = db_obj.service.single()
            db_region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)
            else:
                raise ValueError(
                    f"A shared network with uuid {obj_in.uuid} belonging to provider "
                    f"{db_provider1.name} already exists"
                )

        db_obj.service.connect(service)

        return db_obj

    def patch(
        self, *, db_obj: SharedNetwork, obj_in: NetworkUpdate
    ) -> SharedNetwork | None:
        """Update Network attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        return super().update(db_obj=db_obj, obj_in=obj_in)

    def update(
        self, *, db_obj: SharedNetwork, obj_in: SharedNetworkCreate
    ) -> SharedNetwork | None:
        """Update Network attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        obj_in = NetworkUpdate.parse_obj(obj_in)
        return super().update(db_obj=db_obj, obj_in=obj_in, force=True)


private_network_mng = CRUDPrivateNetwork(
    model=PrivateNetwork,
    create_schema=PrivateNetworkCreate,
    read_schema=NetworkRead,
    read_public_schema=NetworkReadPublic,
    read_extended_schema=NetworkReadExtended,
    read_extended_public_schema=NetworkReadExtendedPublic,
)

shared_network_mng = CRUDSharedNetwork(
    model=SharedNetwork,
    create_schema=SharedNetworkCreate,
    read_schema=NetworkRead,
    read_public_schema=NetworkReadPublic,
    read_extended_schema=NetworkReadExtended,
    read_extended_public_schema=NetworkReadExtendedPublic,
)
