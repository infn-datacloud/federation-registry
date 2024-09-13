"""Module with Create, Read, Update and Delete operations for a Provider."""
from typing import Optional

from fed_reg.crud import CRUDInterface
from fed_reg.identity_provider.crud import identity_provider_mgr
from fed_reg.project.crud import project_mgr
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas import ProviderCreate, ProviderUpdate
from fed_reg.provider.schemas_extended import ProviderCreateExtended
from fed_reg.region.crud import region_mgr


class CRUDProvider(CRUDInterface[Provider, ProviderCreate, ProviderUpdate]):
    """Flavor Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[Provider]:
        return Provider

    @property
    def schema_create(self) -> type[ProviderCreate]:
        return ProviderCreate

    def create(self, *, obj_in: ProviderCreateExtended) -> Provider:
        """Create a new Provider.

        For each received project, identity provider and region, create the
        corresponding entity.
        """
        db_obj = super().create(obj_in=obj_in)
        for item in obj_in.projects:
            project_mgr.create(obj_in=item, provider=db_obj)
        for item in obj_in.identity_providers:
            identity_provider_mgr.create(obj_in=item, provider=db_obj)
        for item in obj_in.regions:
            region_mgr.create(obj_in=item, provider=db_obj)
        return db_obj

    def update(
        self,
        *,
        db_obj: Provider,
        obj_in: ProviderUpdate | ProviderCreateExtended,
        force: bool = False,
    ) -> Optional[Provider]:
        """Update Provider attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects, identity providers and apply default values when
        explicit.
        """
        edit = False
        if force:
            projects_updated = self.__update_projects(db_obj=db_obj, obj_in=obj_in)
            idps_updated = self.__update_identity_providers(
                db_obj=db_obj, obj_in=obj_in
            )
            regions_updated = self.__update_regions(db_obj=db_obj, obj_in=obj_in)
            edit = projects_updated or idps_updated or regions_updated

        if isinstance(obj_in, ProviderCreateExtended):
            obj_in = ProviderUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_projects(
        self, *, obj_in: ProviderCreateExtended, db_obj: Provider
    ) -> bool:
        """Update provider linked projects.

        Connect new projects not already connect, leave untouched already linked ones
        and delete old ones no more connected to the flavor.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.projects}
        for item in obj_in.projects:
            db_item = db_items.pop(item.uuid, None)
            if not db_item:
                project_mgr.create(obj_in=item, provider=db_obj)
                edit = True
            else:
                updated_data = project_mgr.update(
                    db_obj=db_item, obj_in=item, force=True
                )
                if not edit and updated_data is not None:
                    edit = True
        for db_item in db_items.values():
            project_mgr.remove(db_obj=db_item)
            edit = True
        return edit

    def __update_identity_providers(
        self, *, obj_in: ProviderCreateExtended, db_obj: Provider
    ) -> bool:
        """Update provider linked identity providers.

        Connect new identity providers not already connect, leave untouched already
        linked ones and delete/disconnect old ones no more connected to the provider.
        """
        edit = False
        db_items = {db_item.endpoint: db_item for db_item in db_obj.identity_providers}
        for item in obj_in.identity_providers:
            db_item = db_items.pop(item.endpoint, None)
            if not db_item:
                identity_provider_mgr.create(obj_in=item, provider=db_obj)
                edit = True
            else:
                updated_data = identity_provider_mgr.update(
                    db_obj=db_item,
                    obj_in=item,
                    projects=db_obj.projects,
                    provider=db_obj,
                    force=True,
                )
                if not edit and updated_data is not None:
                    edit = True
        for db_item in db_items.values():
            if len(db_item.providers) <= 1:
                identity_provider_mgr.remove(db_obj=db_item)
            else:
                db_obj.identity_providers.disconnect(db_item)
            edit = True
        return edit

    def __update_regions(
        self, *, obj_in: ProviderCreateExtended, db_obj: Provider
    ) -> bool:
        """Update provider linked regions.

        Connect new regions not already connect, leave untouched already linked ones and
        delete old ones no more connected to the provider.
        """
        edit = False
        db_items = {db_item.name: db_item for db_item in db_obj.regions}
        for item in obj_in.regions:
            db_item = db_items.pop(item.name, None)
            if not db_item:
                region_mgr.create(obj_in=item, provider=db_obj)
                edit = True
            else:
                updated_data = region_mgr.update(
                    db_obj=db_item,
                    obj_in=item,
                    projects=db_obj.projects,
                    force=True,
                )
                if not edit and updated_data is not None:
                    edit = True
        for db_item in db_items.values():
            region_mgr.remove(db_obj=db_item)
            edit = True
        return edit


provider_mgr = CRUDProvider()
