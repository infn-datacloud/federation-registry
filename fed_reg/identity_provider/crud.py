"""Module with Create, Read, Update and Delete operations for an Identity Provider."""

from fedreg.identity_provider.models import IdentityProvider
from fedreg.identity_provider.schemas import (
    IdentityProviderCreate,
    IdentityProviderRead,
    IdentityProviderReadPublic,
    IdentityProviderUpdate,
)
from fedreg.identity_provider.schemas_extended import (
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
)
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import IdentityProviderCreateExtended

from fed_reg.crud import CRUDBase
from fed_reg.user_group.crud import user_group_mgr


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
        self,
        *,
        obj_in: IdentityProviderCreateExtended,
        provider: Provider | None = None,
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
        assert db_obj is None, (
            f"Identity provider with endpoint {obj_in.endpoint} already exists."
        )
        db_obj = super().create(obj_in=obj_in)

        if provider is not None:
            db_obj.providers.connect(provider, obj_in.relationship.dict())

        for item in obj_in.user_groups:
            user_group_mgr.create(obj_in=item, identity_provider=db_obj)

        return db_obj

    def update(
        self, *, db_obj: IdentityProvider, obj_in: IdentityProviderCreateExtended
    ) -> IdentityProvider | None:
        """Update Identity Provider attributes.

        By default do not update relationships or default values. If force is True,
        update linked user groups and apply default values when explicit.
        """
        edit = self.__update_user_groups(db_obj=db_obj, obj_in=obj_in)
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj.save() if edit or edit_content else None

    def __update_user_groups(
        self, *, obj_in: IdentityProviderCreateExtended, db_obj: IdentityProvider
    ) -> bool:
        """Update identity provider linked user groups.

        Connect new user group not already connect, leave untouched already linked ones
        and delete the ones not involved in this provider and with no more SLAs.
        """
        edit = False
        db_items = {db_item.name: db_item for db_item in db_obj.user_groups}
        for item in obj_in.user_groups:
            db_item = db_items.pop(item.name, None)
            if not db_item:
                user_group_mgr.create(obj_in=item, identity_provider=db_obj)
                edit = True
            else:
                updated_data = user_group_mgr.update(db_obj=db_item, obj_in=item)
                edit = edit or updated_data is not None
        # Remove identity provider's user groups without SLAs
        for db_item in db_items.values():
            if len(db_item.slas) == 0:
                user_group_mgr.remove(db_obj=db_item)
                edit = True
        return edit


identity_provider_mgr = CRUDIdentityProvider(
    model=IdentityProvider,
    create_schema=IdentityProviderCreate,
    update_schema=IdentityProviderUpdate,
    read_schema=IdentityProviderRead,
    read_public_schema=IdentityProviderReadPublic,
    read_extended_schema=IdentityProviderReadExtended,
    read_extended_public_schema=IdentityProviderReadExtendedPublic,
)
