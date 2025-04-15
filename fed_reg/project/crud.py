"""Module with Create, Read, Update and Delete operations for a Project."""

from fedreg.project.models import Project
from fedreg.project.schemas import ProjectCreate, ProjectUpdate
from fedreg.provider.models import Provider

from fed_reg.crud import CRUDBase


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """Flavor Create, Read, Update and Delete operations."""

    def create(self, *, obj_in: ProjectCreate, provider: Provider) -> Project:
        """Create a new Project. Connect the project to the given provider."""
        db_obj = provider.projects.get_or_none(uuid=obj_in.uuid)
        assert db_obj is None, (
            f"A project with uuid {obj_in.uuid} belonging to provider "
            f"{provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.provider.connect(provider)
        return db_obj


project_mgr = CRUDProject(
    model=Project, create_schema=ProjectCreate, update_schema=ProjectUpdate
)
