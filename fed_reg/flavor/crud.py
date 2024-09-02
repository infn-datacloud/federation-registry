from fed_reg.crud2 import CRUDInterface
from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.flavor.schemas import FlavorUpdate
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    PrivateFlavorCreateExtended,
    SharedFlavorCreateExtended,
)
from fed_reg.region.models import Region
from fed_reg.service.models import ComputeService


class CRUDPrivateFlavor(
    CRUDInterface[PrivateFlavor, PrivateFlavorCreateExtended, FlavorUpdate]
):
    @property
    def model(self) -> type[PrivateFlavor]:
        return PrivateFlavor

    def create(
        self,
        *,
        obj_in: PrivateFlavorCreateExtended,
        service: ComputeService,
        projects: list[Project],
    ) -> PrivateFlavor:
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
            # If a flavor with the same properties already exists, we need to check if
            # they belong to the same provider. If they belong to different providers we
            # treat them as separate entities.
            # We choose any service; it's irrelevant since we want to reach the provider
            db_service: ComputeService = db_obj.services.single()
            db_region: Region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)
        for project in filter(lambda x: x.uuid in obj_in.projects, projects):
            db_obj.projects.connect(project)

        return db_obj

    def update(
        self,
        *,
        db_obj: PrivateFlavor,
        obj_in: FlavorUpdate | PrivateFlavorCreateExtended,
        projects: list[Project] | None = None,
        force: bool = False,
    ) -> PrivateFlavor | None:
        """Update Flavor attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            edit = self.__update_projects(
                db_obj=db_obj, obj_in=obj_in, provider_projects=projects
            )

        if isinstance(obj_in, PrivateFlavorCreateExtended):
            obj_in = FlavorUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_projects(
        self,
        *,
        obj_in: PrivateFlavorCreateExtended,
        db_obj: PrivateFlavor,
        provider_projects: list[Project],
    ) -> bool:
        """Update flavor linked projects.

        Connect new projects not already connect, leave untouched already linked ones
        and delete old ones no more connected to the flavor.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.projects}
        db_projects = {db_item.uuid: db_item for db_item in provider_projects}
        for proj in obj_in.projects:
            db_item = db_items.pop(proj, None)
            if not db_item:
                db_item = db_projects.get(proj)
                db_obj.projects.connect(db_item)
                edit = True
        for db_item in db_items.values():
            db_obj.projects.disconnect(db_item)
            edit = True
        return edit


class CRUDSharedFlavor(
    CRUDInterface[SharedFlavor, SharedFlavorCreateExtended, FlavorUpdate]
):
    @property
    def model(self) -> type[SharedFlavor]:
        return SharedFlavor

    def create(
        self, *, obj_in: SharedFlavorCreateExtended, service: ComputeService
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
            # If a flavor with the same properties already exists, we need to check if
            # they belong to the same provider. If they belong to different providers we
            # treat them as separate entities.
            # We choose any service; it's irrelevant since we want to reach the provider
            db_service: ComputeService = db_obj.services.single()
            db_region: Region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)
        db_obj.services.connect(service)
        return db_obj


class CRUDFlavor(
    CRUDInterface[
        Flavor, PrivateFlavorCreateExtended | SharedFlavorCreateExtended, FlavorUpdate
    ]
):
    @property
    def model(self) -> type[Flavor]:
        return Flavor

    def create(
        self,
        *,
        obj_in: PrivateFlavorCreateExtended | SharedFlavorCreateExtended,
        service: ComputeService,
        projects: list[Project] | None = None,
    ) -> Flavor:
        if isinstance(obj_in, PrivateFlavorCreateExtended):
            return CRUDPrivateFlavor().create(
                obj_in=obj_in, service=service, projects=projects
            )
        return CRUDSharedFlavor().create(obj_in=obj_in, service=service)

    def update(
        self,
        *,
        db_obj: Flavor,
        obj_in: FlavorUpdate | PrivateFlavorCreateExtended | SharedFlavorCreateExtended,
        projects: list[Project] | None = None,
        force: bool = False,
    ) -> Flavor | None:
        """Update Flavor attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        # TODO: manage when current type differs from new type
        # (i.e DB is Private, new item is shared)
        if isinstance(obj_in, PrivateFlavorCreateExtended):
            return CRUDPrivateFlavor().update(
                db_obj=db_obj, obj_in=obj_in, projects=projects, force=force
            )
        elif isinstance(obj_in, SharedFlavorCreateExtended):
            return CRUDSharedFlavor().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return super().update(db_obj=db_obj, obj_in=obj_in, force=force)


private_flavor_mgr = CRUDPrivateFlavor()
shared_flavor_mgr = CRUDSharedFlavor()
flavor_mgr = CRUDFlavor()
