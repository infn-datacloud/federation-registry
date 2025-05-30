"""Module with Create, Read, Update and Delete operations for a Region."""

from fedreg.location.schemas import LocationCreate
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import RegionCreateExtended
from fedreg.region.models import Region
from fedreg.region.schemas import RegionCreate, RegionUpdate
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)

from fed_reg.crud import CRUDBase
from fed_reg.location.crud import location_mgr
from fed_reg.service.crud import service_mgr


class CRUDRegion(CRUDBase[Region, RegionCreate, RegionUpdate]):
    """Region Create, Read, Update and Delete operations."""

    def create(self, *, obj_in: RegionCreateExtended, provider: Provider) -> Region:
        """Create a new Region.

        Connect the region to the given provider. For each received location and
        service, create the corresponding entity.
        """
        db_obj = provider.regions.get_or_none(name=obj_in.name)
        assert db_obj is None, (
            f"Provider {provider.name} already has a region with name {obj_in.name}"
        )

        db_obj = super().create(obj_in=obj_in)
        db_obj.provider.connect(provider)

        if obj_in.location is not None:
            db_loc = location_mgr.get(site=obj_in.location.site)
            if db_loc is None:
                location_mgr.create(obj_in=obj_in.location, region=db_obj)
            else:
                db_obj.location.connect(db_loc)
                location_mgr.patch(db_obj=db_loc, obj_in=obj_in.location)

        for item in (
            obj_in.block_storage_services
            + obj_in.compute_services
            + obj_in.identity_services
            + obj_in.network_services
            + obj_in.object_store_services
        ):
            service_mgr.create(
                obj_in=item, region=db_obj, provider_projects=provider.projects
            )

        return db_obj

    def update(
        self,
        *,
        db_obj: Region,
        obj_in: RegionCreateExtended,
        provider_projects: list[Project] | None = None,
    ) -> Region | None:
        """Update Region attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        if provider_projects is None:
            provider_projects = []
        services = (
            obj_in.block_storage_services
            + obj_in.compute_services
            + obj_in.identity_services
            + obj_in.network_services
            + obj_in.object_store_services
        )
        edit1 = self.__update_location(db_obj=db_obj, location=obj_in.location)
        edit2 = self.__update_services(
            db_obj=db_obj, input_services=services, provider_projects=provider_projects
        )
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj.save() if edit1 or edit2 or edit_content else None

    def __update_location(
        self, *, db_obj: Region, location: LocationCreate | None
    ) -> bool:
        """Update region linked location.

        If no new location is given or the new location differs from the current one,
        disconnect current location if present.

        If there wasn't a location and and a new one is given, or the new location
        differs from the current one, create the new location.

        Otherwise, if the old location match the new location, forcefully update it.
        """
        edit = False
        curr_location = db_obj.location.single()

        if curr_location and (location is None or curr_location.site != location.site):
            db_obj.location.disconnect(curr_location)
            edit = True

        if (curr_location is None and location) or (
            curr_location and location and curr_location.site != location.site
        ):
            db_location = location_mgr.get(site=location.site)
            if db_location is None:
                location_mgr.create(obj_in=location, region=db_obj)
            else:
                db_obj.location.connect(db_location)
                location_mgr.patch(db_obj=db_location, obj_in=location)
            return True

        if curr_location and location and curr_location.site == location.site:
            updated_data = location_mgr.update(db_obj=curr_location, obj_in=location)
            return updated_data is not None

        return edit

    def __update_services(
        self,
        *,
        db_obj: Region,
        input_services: list[
            BlockStorageService
            | ComputeService
            | IdentityService
            | NetworkService
            | ObjectStoreService
        ],
        provider_projects: list[Project],
    ) -> bool:
        """Update region linked block storage services.

        Connect new block storage services not already connect, leave untouched already
        linked ones and delete old ones no more connected to the region.
        """
        edit = False
        db_items = {db_item.endpoint: db_item for db_item in db_obj.services}

        for item in input_services:
            db_item = db_items.pop(item.endpoint, None)
            if db_item is None:
                service_mgr.create(
                    obj_in=item, region=db_obj, provider_projects=provider_projects
                )
                edit = True
            else:
                updated_data = service_mgr.update(
                    db_obj=db_item,
                    obj_in=item,
                    provider_projects=provider_projects,
                )
                edit = edit or updated_data is not None

        for db_item in db_items.values():
            service_mgr.remove(db_obj=db_item)
            edit = True

        return edit


region_mgr = CRUDRegion(
    model=Region, create_schema=RegionCreate, update_schema=RegionUpdate
)
