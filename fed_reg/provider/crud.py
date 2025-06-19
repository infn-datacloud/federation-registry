"""Module with Create, Read, Update and Delete operations for a Provider."""

from fedreg.auth_method.models import AuthMethod
from fedreg.identity_provider.models import IdentityProvider
from fedreg.provider.models import Provider
from fedreg.provider.schemas import ProviderCreate, ProviderUpdate
from fedreg.provider.schemas_extended import (
    IdentityProviderCreateExtended,
    K8sAuthMethodCreate,
    OsAuthMethodCreate,
    ProjectCreate,
    ProviderCreateExtended,
    RegionCreateExtended,
    SLACreateExtended,
    UserGroupCreateExtended,
)
from fedreg.sla.models import SLA
from fedreg.user_group.models import UserGroup

from fed_reg.crud import CRUDBase
from fed_reg.identity_provider.crud import identity_provider_mgr
from fed_reg.project.crud import project_mgr
from fed_reg.region.crud import region_mgr
from fed_reg.sla.crud import sla_mgr
from fed_reg.user_group.crud import user_group_mgr


class CRUDProvider(CRUDBase[Provider, ProviderCreate, ProviderUpdate]):
    """Provider Create, Read, Update and Delete operations."""

    def create(self, *, obj_in: ProviderCreateExtended) -> Provider:
        """Create a new Provider.

        For each received project, identity provider and region, create the
        corresponding entity.
        """
        db_obj = self.get(name=obj_in.name, type=obj_in.type)
        assert db_obj is None, (
            f"Provider with name={obj_in.name} and type={obj_in.type} already exists."
        )
        db_obj = super().create(obj_in=obj_in)
        for item in obj_in.projects:
            project_mgr.create(obj_in=item, provider=db_obj)
        for idp in obj_in.identity_providers:
            db_idp = self.__create_or_connect_to_idp(
                input_identity_provider=idp, provider=db_obj
            )
            for user_group in idp.user_groups:
                self.__create_or_connect_sla(
                    input_sla=user_group.sla,
                    input_user_group_name=user_group.name,
                    input_idp_endpoint=idp.endpoint,
                    identity_provider=db_idp,
                    provider=db_obj,
                )
        for item in obj_in.regions:
            region_mgr.create(obj_in=item, provider=db_obj)
        return db_obj

    def update(
        self, *, db_obj: Provider, obj_in: ProviderCreateExtended
    ) -> Provider | None:
        """Update Provider attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects, identity providers and apply default values when
        explicit.
        """
        edit1 = self.__update_projects(db_obj=db_obj, input_projects=obj_in.projects)
        edit2 = self.__update_identity_providers(
            db_obj=db_obj, input_idps=obj_in.identity_providers
        )
        edit3 = self.__update_regions(db_obj=db_obj, input_regions=obj_in.regions)
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj.save() if edit1 or edit2 or edit3 or edit_content else None

    def update_idp_relationship(
        self,
        *,
        db_obj: IdentityProvider,
        obj_in: OsAuthMethodCreate | K8sAuthMethodCreate,
        provider: Provider,
    ) -> AuthMethod | None:
        """Update identity provider and resource provider connection attributes."""
        if db_obj.providers.is_connected(provider):
            rel = db_obj.providers.relationship(provider)
            if rel.procol != obj_in.protocol or rel.idp_name != obj_in.idp_name:
                return db_obj.providers.reconnect(provider, obj_in.dict())
            return None
        return db_obj.providers.connect(provider, obj_in.dict())

    def __create_or_connect_to_idp(
        self,
        *,
        input_identity_provider: IdentityProviderCreateExtended,
        provider: Provider,
    ) -> IdentityProvider:
        """Create identity provider and related user groups.

        If the identity provider already exists, connect to it.
        Create missing user groups.
        Create or connect SLAs to groups.
        """
        db_idp = identity_provider_mgr.get(endpoint=input_identity_provider.endpoint)
        if db_idp is None:
            return identity_provider_mgr.create(
                obj_in=input_identity_provider, provider=provider
            )
        provider.identity_providers.connect(
            db_idp, input_identity_provider.relationship.dict()
        )
        identity_provider_mgr.patch(db_obj=db_idp, obj_in=input_identity_provider)

        for user_group in input_identity_provider.user_groups:
            self.__create_or_patch_user_group(
                input_user_group=user_group, identity_provider=db_idp
            )
        return db_idp

    def __create_or_patch_user_group(
        self,
        *,
        input_user_group: UserGroupCreateExtended,
        identity_provider: IdentityProvider,
    ) -> UserGroup | None:
        """Create user group or, if already existing, patch and connect to it."""
        db_user_group = identity_provider.user_groups.get_or_none(
            name=input_user_group.name
        )
        if db_user_group is None:
            return user_group_mgr.create(
                obj_in=input_user_group, identity_provider=identity_provider
            )
        return user_group_mgr.patch(db_obj=db_user_group, obj_in=input_user_group)

    def __create_or_connect_sla(
        self,
        *,
        input_sla: SLACreateExtended,
        input_idp_endpoint: str,
        input_user_group_name: str,
        provider: Provider,
        identity_provider: IdentityProvider,
    ) -> SLA | None:
        """Create SLA if not existing, otherwise patch and connect to it."""
        # Here the user group must exists in the provider
        # since we have just created it
        db_user_group = identity_provider.user_groups.get(name=input_user_group_name)
        db_project = provider.projects.get_or_none(uuid=input_sla.project)
        assert db_project is not None, (
            f"Project {input_sla.project} does not belong to provider {provider.name}"
        )

        # Create or connect SLAs.
        db_sla = sla_mgr.get(doc_uuid=input_sla.doc_uuid)
        if db_sla is None:
            return sla_mgr.create(
                obj_in=input_sla, user_group=db_user_group, project=db_project
            )

        # SLA can exist.
        sla_user_group = db_sla.user_group.single()
        user_group_idp = sla_user_group.identity_provider.single()
        assert (
            sla_user_group.name == input_user_group_name
            and user_group_idp.endpoint == input_idp_endpoint
        ), (
            f"SLA with document uuid {db_sla.doc_uuid} already exists, but "
            f"it belongs to user group {sla_user_group} owned by identity "
            f"provider {user_group_idp} which differs from target user "
            f"group {input_user_group_name} owned by identity provider "
            f"{input_idp_endpoint}."
        )

        # When creating a provider can't be already connected.
        # When updating a provider, the target project can already have an SLA, the
        # existing SLA can be already attached to another project of this provider
        edit = False
        if not db_sla.projects.is_connected(db_project):
            db_sla = sla_mgr.reconnect_sla(sla=db_sla, project=db_project)
            edit = True
        updated_data = sla_mgr.patch(db_obj=db_sla, obj_in=input_sla)

        return db_sla if edit or updated_data is not None else None

    def __update_projects(
        self, *, db_obj: Provider, input_projects: list[ProjectCreate]
    ) -> bool:
        """Update provider linked projects.

        Connect new projects not already connect, leave untouched already linked ones
        and delete old ones no more connected to the flavor.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.projects}
        for item in input_projects:
            db_item = db_items.pop(item.uuid, None)
            if not db_item:
                project_mgr.create(obj_in=item, provider=db_obj)
                edit = True
            else:
                updated_data = project_mgr.update(db_obj=db_item, obj_in=item)
                edit = edit or updated_data is not None
        for db_item in db_items.values():
            project_mgr.remove(db_obj=db_item)
            edit = True
        return edit

    def __update_identity_providers(
        self, *, db_obj: Provider, input_idps: list[IdentityProviderCreateExtended]
    ) -> bool:
        """Update provider linked identity providers.

        Connect new identity providers not already connect, leave untouched already
        linked ones and delete/disconnect old ones no more connected to the provider.
        """
        edit = False
        db_items = {db_item.endpoint: db_item for db_item in db_obj.identity_providers}
        for item in input_idps:
            db_item = db_items.pop(item.endpoint, None)

            if db_item is None:
                db_item = self.__create_or_connect_to_idp(
                    input_identity_provider=item, provider=db_obj
                )
                edit = True

            else:
                # Update relationship data if needed
                rel = db_item.providers.relationship(db_obj)
                if rel.protocol != item.relationship.protocol:
                    rel.protocol = item.relationship.protocol
                    edit = True
                if rel.idp_name != item.relationship.idp_name:
                    rel.idp_name = item.relationship.idp_name
                    edit = True
                updated_data = identity_provider_mgr.patch(db_obj=db_item, obj_in=item)
                edit = edit or updated_data is not None
                for user_group in item.user_groups:
                    updated_data = self.__create_or_patch_user_group(
                        input_user_group=user_group, identity_provider=db_item
                    )
                    edit = edit or updated_data is not None

            for user_group in item.user_groups:
                edit = self.__create_or_connect_sla(
                    input_sla=user_group.sla,
                    input_user_group_name=user_group.name,
                    input_idp_endpoint=item.endpoint,
                    identity_provider=db_item,
                    provider=db_obj,
                )

        for db_item in db_items.values():
            db_obj.identity_providers.disconnect(db_item)
            edit = True

        return edit

    def __update_regions(
        self, *, db_obj: Provider, input_regions: list[RegionCreateExtended]
    ) -> bool:
        """Update provider linked regions.

        Connect new regions not already connect, leave untouched already linked ones and
        delete old ones no more connected to the provider.
        """
        edit = False
        db_items = {db_item.name: db_item for db_item in db_obj.regions}
        for item in input_regions:
            db_item = db_items.pop(item.name, None)
            if not db_item:
                region_mgr.create(obj_in=item, provider=db_obj)
                edit = True
            else:
                updated_data = region_mgr.update(
                    db_obj=db_item, obj_in=item, provider_projects=db_obj.projects
                )
                edit = edit or updated_data is not None
        for db_item in db_items.values():
            region_mgr.remove(db_obj=db_item)
            edit = True
        return edit


provider_mgr = CRUDProvider(
    model=Provider, create_schema=ProviderCreate, update_schema=ProviderUpdate
)
