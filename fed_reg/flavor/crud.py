"""Module with Create, Read, Update and Delete operations for a Flavor."""
from typing import Optional

from fedreg.flavor.models import Flavor
from fedreg.flavor.schemas import (
    FlavorCreate,
    FlavorRead,
    FlavorReadPublic,
    FlavorUpdate,
)
from fedreg.flavor.schemas_extended import FlavorReadExtended, FlavorReadExtendedPublic
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import FlavorCreateExtended
from fedreg.service.models import ComputeService

from fed_reg.crud import CRUDBase


class CRUDFlavor(
    CRUDBase[
        Flavor,
        FlavorCreate,
        FlavorUpdate,
        FlavorRead,
        FlavorReadPublic,
        FlavorReadExtended,
        FlavorReadExtendedPublic,
    ]
):
    """Flavor Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: FlavorCreateExtended,
        service: ComputeService,
        projects: Optional[list[Project]] = None,
    ) -> Flavor:
        """Create a new Flavor.

        At first check that a flavor with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        flavor. In any case connect the flavor to the given service and to any received
        project.
        """
        if projects is None:
            projects = []
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
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)

        for project in filter(lambda x: x.uuid in obj_in.projects, projects):
            db_obj.projects.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: Flavor,
        obj_in: FlavorUpdate | FlavorCreateExtended,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[Flavor]:
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

        if isinstance(obj_in, FlavorCreateExtended):
            obj_in = FlavorUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_projects(
        self,
        *,
        obj_in: FlavorCreateExtended,
        db_obj: Flavor,
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


flavor_mng = CRUDFlavor(
    model=Flavor,
    create_schema=FlavorCreate,
    read_schema=FlavorRead,
    read_public_schema=FlavorReadPublic,
    read_extended_schema=FlavorReadExtended,
    read_extended_public_schema=FlavorReadExtendedPublic,
)
