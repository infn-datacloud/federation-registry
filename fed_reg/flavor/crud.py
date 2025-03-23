"""Module with Create, Read, Update and Delete operations for a Flavor."""

from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.flavor.schemas import (
    FlavorRead,
    FlavorReadPublic,
    FlavorUpdate,
    PrivateFlavorCreate,
    SharedFlavorCreate,
)
from fedreg.flavor.schemas_extended import FlavorReadExtended, FlavorReadExtendedPublic
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import PrivateFlavorCreateExtended
from fedreg.service.models import ComputeService

from fed_reg.crud import CRUDBase, CRUDMultiProject, CRUDPrivateSharedDispatcher


class CRUDPrivateFlavor(
    CRUDMultiProject[
        PrivateFlavor,
        PrivateFlavorCreate,
        PrivateFlavorCreateExtended,
        FlavorUpdate,
        FlavorRead,
        FlavorReadPublic,
        FlavorReadExtended,
        FlavorReadExtendedPublic,
    ]
):
    """Private Flavor Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: PrivateFlavorCreateExtended,
        service: ComputeService,
        provider_projects: list[Project],
    ) -> PrivateFlavor:
        """Create a new Flavor.

        At first check that a flavor with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        flavor. In any case connect the flavor to the given service and to any received
        project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"

        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # It's indifferent which service, we want to reach the provider
            db_service = db_obj.services.single()
            db_region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            assert db_provider1 != db_provider2, (
                f"A private flavor with uuid {obj_in.uuid} belonging to provider "
                f"{db_provider1.name} already exists"
            )
            db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)
        super()._connect_projects(
            db_obj=db_obj,
            input_uuids=obj_in.projects,
            provider_projects=provider_projects,
        )

        return db_obj


class CRUDSharedFlavor(
    CRUDBase[
        SharedFlavor,
        SharedFlavorCreate,
        FlavorUpdate,
        FlavorRead,
        FlavorReadPublic,
        FlavorReadExtended,
        FlavorReadExtendedPublic,
    ]
):
    """Flavor Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: SharedFlavorCreate, service: ComputeService
    ) -> SharedFlavor:
        """Create a new Flavor.

        At first check that a flavor with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        flavor. In any case connect the flavor to the given service and to any received
        project.
        """
        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # It's indifferent which service, we want to reach the provider
            db_service = db_obj.services.single()
            db_region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            assert db_provider1 != db_provider2, (
                f"A shared flavor with uuid {obj_in.uuid} belonging to provider "
                f"{db_provider1.name} already exists"
            )
            db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)

        return db_obj


class CRUDFlavor(
    CRUDPrivateSharedDispatcher[
        PrivateFlavor,
        SharedFlavor,
        CRUDPrivateFlavor,
        CRUDSharedFlavor,
        PrivateFlavorCreateExtended,
        SharedFlavorCreate,
        FlavorUpdate,
    ]
):
    """Private and Shared Flavor Create, Read, Update and Delete operations."""


private_flavor_mng = CRUDPrivateFlavor(
    model=PrivateFlavor,
    create_schema=PrivateFlavorCreate,
    update_schema=FlavorUpdate,
    read_schema=FlavorRead,
    read_public_schema=FlavorReadPublic,
    read_extended_schema=FlavorReadExtended,
    read_extended_public_schema=FlavorReadExtendedPublic,
)
shared_flavor_mng = CRUDSharedFlavor(
    model=SharedFlavor,
    create_schema=SharedFlavorCreate,
    update_schema=FlavorUpdate,
    read_schema=FlavorRead,
    read_public_schema=FlavorReadPublic,
    read_extended_schema=FlavorReadExtended,
    read_extended_public_schema=FlavorReadExtendedPublic,
)
flavor_mgr = CRUDFlavor(
    private_mgr=private_flavor_mng,
    shared_mgr=shared_flavor_mng,
    shared_model=SharedFlavor,
    shared_create_schema=SharedFlavorCreate,
)
