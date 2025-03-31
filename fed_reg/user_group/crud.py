"""Module with Create, Read, Update and Delete operations for a User Group."""

from fedreg.identity_provider.models import IdentityProvider
from fedreg.provider.schemas_extended import UserGroupCreateExtended
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import UserGroupCreate, UserGroupUpdate

from fed_reg.crud import CRUDBase


class CRUDUserGroup(CRUDBase[UserGroup, UserGroupCreate, UserGroupUpdate]):
    """User Group Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: UserGroupCreateExtended, identity_provider: IdentityProvider
    ) -> UserGroup:
        """Create a new User Group.

        Connect the user group to the given identity provider. Within the provider
        projects, find the one pointed by the new user group's SLA. If this project
        already has an SLA, if this SLA has just one project delete it, otherwise,
        disconnect it from the target project. In any case create (or just update if
        already exists) the SLA.
        """
        db_obj = identity_provider.user_groups.get_or_none(name=obj_in.name)
        assert db_obj is None, (
            f"User group with name {obj_in.name} already exists on identity provider "
            f"{identity_provider.endpoint}."
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.identity_provider.connect(identity_provider)
        return db_obj


user_group_mgr = CRUDUserGroup(
    model=UserGroup, create_schema=UserGroupCreate, update_schema=UserGroupUpdate
)
