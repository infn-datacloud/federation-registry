"""Module with Create, Read, Update and Delete operations for an SLA."""

from fedreg.project.models import Project
from fedreg.provider.schemas_extended import SLACreateExtended
from fedreg.sla.models import SLA
from fedreg.sla.schemas import SLACreate, SLARead, SLAReadPublic, SLAUpdate
from fedreg.sla.schemas_extended import SLAReadExtended, SLAReadExtendedPublic
from fedreg.user_group.models import UserGroup

from fed_reg.crud import CRUDBase


class CRUDSLA(
    CRUDBase[
        SLA,
        SLACreate,
        SLAUpdate,
        SLARead,
        SLAReadPublic,
        SLAReadExtended,
        SLAReadExtendedPublic,
    ]
):
    """SLA Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: SLACreate, project: Project, user_group: UserGroup
    ) -> SLA:
        """Create a new SLA.

        At first check an SLA pointing to the same document does not exist yet. If it
        does not exist, create it. In any case connect the SLA to the given user group
        and project. If the project already has an attached SLA, replace it.
        """
        db_obj = self.get(doc_uuid=obj_in.doc_uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
            db_obj.user_group.connect(user_group)
        else:
            raise ValueError(
                f"An SLA with document uuid {obj_in.doc_uuid} already exists"
            )
        old_sla = project.sla.single()
        if old_sla:
            project.sla.reconnect(old_sla, db_obj)
        else:
            db_obj.projects.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: SLA,
        obj_in: SLACreateExtended,
        provider_projects: list[Project],
    ) -> SLA | None:
        """Update SLA attributes and connected projects."""
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        edited_obj1 = self._update_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        edited_obj2 = super().update(db_obj=db_obj, obj_in=obj_in)
        return edited_obj2 if edited_obj2 is not None else edited_obj1

    def _update_project(
        self, *, db_obj: SLA, input_uuid: str, provider_projects: list[Project]
    ) -> SLA | None:
        """Update projects connections.

        To update projects, since the forced update happens when creating or updating a
        provider, we filter all the existing projects on this provider already connected
        to this SLA. It should be just one. If there is a project already connected we
        replace the old one with the new one, otherwise we immediately connect the new
        one.
        """
        edit = False
        new_project = next(
            filter(lambda x: x.uuid == input_uuid, provider_projects), None
        )
        assert new_project is not None, (
            f"Input project {input_uuid} not in the provider "
            f"projects: {[i.uuid for i in provider_projects]}"
        )
        # Detect if the SLA already has a linked project on this provider
        old_project = next(
            filter(lambda x: x in db_obj.projects, provider_projects), None
        )
        if not old_project:
            db_obj.projects.connect(new_project)
            edit = True
        elif old_project.uuid != new_project.uuid:
            db_obj.projects.reconnect(old_project, new_project)
            edit = True
        return db_obj.save() if edit else None


sla_mng = CRUDSLA(
    model=SLA,
    create_schema=SLACreate,
    update_schema=SLAUpdate,
    read_schema=SLARead,
    read_public_schema=SLAReadPublic,
    read_extended_schema=SLAReadExtended,
    read_extended_public_schema=SLAReadExtendedPublic,
)
