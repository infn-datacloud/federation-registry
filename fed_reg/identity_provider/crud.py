"""Module with Create, Read, Update and Delete operations for an Identity Provider."""
from typing import List, Optional, Union

from fed_reg.crud import CRUDBase
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.identity_provider.schemas import (
    IdentityProviderCreate,
    IdentityProviderRead,
    IdentityProviderReadPublic,
    IdentityProviderUpdate,
)
from fed_reg.identity_provider.schemas_extended import (
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
)
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas_extended import IdentityProviderCreateExtended
from fed_reg.user_group.crud import user_group_mng


class CRUDIdentityProvider(
    CRUDBase[
        IdentityProvider,
        IdentityProviderCreate,
        IdentityProviderUpdate,
        IdentityProviderRead,
        IdentityProviderReadPublic,
        IdentityProviderReadExtended,
        IdentityProviderReadExtendedPublic,
    ]
):
    """Identity Provider Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: IdentityProviderCreateExtended, provider: Provider
    ) -> IdentityProvider:
        """Create a new Identity Provider.

        At first check that an identity provider with
        the given endpoint does not already exist. If it does not exist create it.
        Otherwise do nothing. In any case connect the identity provider to the given
        provider. For any received user group, check the identity provider is not
        already connect to it (when dealing with a new identity provider, all user
        groups will be new user groups). If the identity provider is already connected
        to that user group, update it and its relationships. Otherwise create that new
        user group.

        Attention: Do not delete no more connected user groups since this
        operation is executed when creating a new provider. So, if some user group
        is not received, it does not mean that this identity provider does not
        support them, but that the specific provider is not interested to that
        user groups.
        """
        db_obj = self.get(endpoint=obj_in.endpoint)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)

        db_obj.providers.connect(provider, obj_in.relationship.dict())

        for item in obj_in.user_groups:
            db_user_group = db_obj.user_groups.get_or_none(name=item.name)
            if db_user_group:
                user_group_mng.update(
                    db_obj=db_user_group,
                    obj_in=item,
                    projects=provider.projects,
                    force=True,
                )
            else:
                user_group_mng.create(
                    obj_in=item, identity_provider=db_obj, projects=provider.projects
                )

        return db_obj

    def remove(self, *, db_obj: IdentityProvider) -> bool:
        """Delete an existing identity provider and all its relationships.

        At first delete its user groups. Finally delete the identity provider.
        """
        for item in db_obj.user_groups:
            user_group_mng.remove(db_obj=item)
        return super().remove(db_obj=db_obj)

    def update(
        self,
        *,
        db_obj: IdentityProvider,
        obj_in: Union[IdentityProviderUpdate, IdentityProviderCreateExtended],
        projects: Optional[List[Project]] = None,
        provider: Optional[Provider] = None,
        force: bool = False,
    ) -> Optional[IdentityProvider]:
        """Update Identity Provider attributes.

        By default do not update relationships or default values. If force is True,
        update linked user groups and apply default values when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            edit = self.__update_user_groups(
                db_obj=db_obj, obj_in=obj_in, provider_projects=projects
            )
            if provider is not None:
                rel = db_obj.providers.relationship(provider)
                if (
                    rel.protocol != obj_in.relationship.protocol
                    or rel.idp_name != obj_in.relationship.idp_name
                ):
                    db_obj.providers.replace(provider, obj_in.relationship.dict())
                    edit = True

        if isinstance(obj_in, IdentityProviderCreateExtended):
            obj_in = IdentityProviderUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_user_groups(
        self,
        *,
        obj_in: IdentityProviderCreateExtended,
        db_obj: IdentityProvider,
        provider_projects: List[Project],
    ) -> bool:
        """Update identity provider linked user groups.

        Connect new user group not already connect, leave untouched already linked ones
        and delete old ones no more connected to the identity provider.
        """
        edit = False
        db_items = {db_item.name: db_item for db_item in db_obj.user_groups}
        for item in obj_in.user_groups:
            db_item = db_items.pop(item.name, None)
            if not db_item:
                user_group_mng.create(
                    obj_in=item, identity_provider=db_obj, projects=provider_projects
                )
                edit = True
            else:
                updated_data = user_group_mng.update(
                    db_obj=db_item, obj_in=item, projects=provider_projects, force=True
                )
                if not edit and updated_data is not None:
                    edit = True
        for db_item in db_items.values():
            user_group_mng.remove(db_obj=db_item)
            edit = True
        return edit


identity_provider_mng = CRUDIdentityProvider(
    model=IdentityProvider,
    create_schema=IdentityProviderCreate,
    read_schema=IdentityProviderRead,
    read_public_schema=IdentityProviderReadPublic,
    read_extended_schema=IdentityProviderReadExtended,
    read_extended_public_schema=IdentityProviderReadExtendedPublic,
)
