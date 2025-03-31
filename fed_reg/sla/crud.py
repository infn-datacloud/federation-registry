"""Module with Create, Read, Update and Delete operations for an SLA."""

from fedreg.project.models import Project
from fedreg.provider.schemas_extended import SLACreateExtended
from fedreg.sla.models import SLA
from fedreg.sla.schemas import SLACreate, SLAUpdate
from fedreg.user_group.models import UserGroup

from fed_reg.crud import CRUDBase


class CRUDSLA(CRUDBase[SLA, SLACreate, SLAUpdate]):
    """SLA Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: SLACreateExtended, user_group: UserGroup, project: Project
    ) -> SLA:
        """Create a new SLA.

        At first check an SLA pointing to the same document does not exist yet. If it
        does not exist, create it. In any case connect the SLA to the given user group
        and project. If the project already has an attached SLA, replace it.
        """
        db_obj = self.get(doc_uuid=obj_in.doc_uuid)
        assert db_obj is None, (
            f"An SLA with document uuid {obj_in.doc_uuid} already exists"
        )

        db_obj = super().create(obj_in=obj_in)
        db_obj.user_group.connect(user_group)
        return self.reconnect_sla(sla=db_obj, project=project)

    def reconnect_sla(self, *, sla: SLA, project: Project) -> SLA:
        """Disconnect previous project's SLA and eventually delete it."""
        old_sla = project.sla.single()
        if old_sla is not None:
            if len(old_sla.projects) > 1:
                project.sla.disconnect(old_sla)
            else:
                self.remove(db_obj=old_sla)
        sla.projects.connect(project)
        return sla.save()

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
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj.save() if edited_obj1 or edit_content else None

    def _update_project(
        self, *, db_obj: SLA, input_uuid: str, provider_projects: list[Project]
    ) -> bool:
        """Update projects connections.

        To update projects, since the forced update happens when creating or updating a
        provider, we filter all the existing projects on this provider already connected
        to this SLA. It should be just one. If there is a project already connected we
        replace the old one with the new one, otherwise we immediately connect the new
        one.
        """
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
        if old_project is None:
            db_obj.projects.connect(new_project)
            return True
        elif old_project.uuid != new_project.uuid:
            db_obj.projects.reconnect(old_project, new_project)
            return True
        return False


sla_mgr = CRUDSLA(model=SLA, create_schema=SLACreate, update_schema=SLAUpdate)
