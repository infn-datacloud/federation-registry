"""Module with Create, Read, Update and Delete operations for a User Group."""
from typing import Optional

from fedreg.identity_provider.models import IdentityProvider
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import UserGroupCreateExtended
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import (
    UserGroupCreate,
    UserGroupRead,
    UserGroupReadPublic,
    UserGroupUpdate,
)
from fedreg.user_group.schemas_extended import (
    UserGroupReadExtended,
    UserGroupReadExtendedPublic,
)

from fed_reg.crud import CRUDBase
from fed_reg.sla.crud import sla_mng


class CRUDUserGroup(
    CRUDBase[
        UserGroup,
        UserGroupCreate,
        UserGroupUpdate,
        UserGroupRead,
        UserGroupReadPublic,
        UserGroupReadExtended,
        UserGroupReadExtendedPublic,
    ]
):
    """User Group Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: UserGroupCreateExtended,
        identity_provider: IdentityProvider,
        projects: Optional[list[Project]] = None,
    ) -> UserGroup:
        """Create a new User Group.

        Connect the user group to the given identity provider. Within the provider
        projects, find the one pointed by the new user group's SLA. If this project
        already has an SLA, if this SLA has just one project delete it, otherwise,
        disconnect it from the target project. In any case create (or just update if
        already exists) the SLA.
        """
        if projects is None:
            projects = []
        db_obj = super().create(obj_in=obj_in)
        db_obj.identity_provider.connect(identity_provider)
        db_project = next(
            filter(lambda x: x.uuid == obj_in.sla.project, projects), None
        )
        if db_project:
            db_sla = db_project.sla.single()
            if db_sla is not None:
                if len(db_sla.projects) == 1:
                    sla_mng.remove(db_obj=db_sla)
            sla_mng.create(obj_in=obj_in.sla, user_group=db_obj, project=db_project)
        return db_obj

    def remove(self, *, db_obj: UserGroup) -> bool:
        """Delete an existing user group and all its relationships.

        At first delete its SLAs. Finally delete the user group.
        """
        for item in db_obj.slas:
            sla_mng.remove(db_obj=item)
        return super().remove(db_obj=db_obj)

    def update(
        self,
        *,
        db_obj: UserGroup,
        obj_in: UserGroupUpdate | UserGroupCreateExtended,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[UserGroup]:
        """Update User Group attributes.

        By default do not update relationships or default values. If force is True,
        update linked SLAs and apply default values when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            edit = self.__update_slas(
                db_obj=db_obj, obj_in=obj_in, provider_projects=projects
            )

        if isinstance(obj_in, UserGroupCreateExtended):
            obj_in = UserGroupUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_slas(
        self,
        *,
        obj_in: UserGroupCreateExtended,
        db_obj: UserGroup,
        provider_projects: list[Project],
    ) -> bool:
        """Update user group linked SLAs.

        Connect new SLA not already connect, leave untouched already linked ones. Delete
        old ones no more connected to the user group and pointing only to a project in
        this provider. If there are SLAs pointing to a project in this provider but also
        to projects of other providers, disconnect them.
        """
        edit = False
        db_project = next(
            filter(lambda x: x.uuid in obj_in.sla.project, provider_projects), None
        )
        db_sla_target_provider = next(
            filter(
                lambda x: any(p in provider_projects for p in x.projects), db_obj.slas
            ),
            None,
        )

        # An SLA pointing to this provider already exists and it's document uuid
        # differs from the new one: Disconnect or delete it.
        if db_sla_target_provider:
            if db_sla_target_provider.doc_uuid != obj_in.sla.doc_uuid:
                if len(db_sla_target_provider.projects) == 1:
                    sla_mng.remove(db_obj=db_sla_target_provider)
                sla_mng.create(obj_in=obj_in.sla, project=db_project, user_group=db_obj)
                edit = True
            else:
                updated_data = sla_mng.update(
                    db_obj=db_sla_target_provider,
                    obj_in=obj_in.sla,
                    projects=provider_projects,
                    force=True,
                )
                if updated_data:
                    edit = True
        else:
            sla_mng.create(obj_in=obj_in.sla, project=db_project, user_group=db_obj)
            edit = True
        return edit


user_group_mng = CRUDUserGroup(
    model=UserGroup,
    create_schema=UserGroupCreate,
    read_schema=UserGroupRead,
    read_public_schema=UserGroupReadPublic,
    read_extended_schema=UserGroupReadExtended,
    read_extended_public_schema=UserGroupReadExtendedPublic,
)
