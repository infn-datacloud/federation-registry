"""Module with Create, Read, Update and Delete operations for a Project."""
from fed_reg.crud import CRUDInterface
from fed_reg.project.models import Project
from fed_reg.project.schemas import ProjectCreate, ProjectUpdate
from fed_reg.provider.models import Provider


class CRUDProject(CRUDInterface[Project, ProjectCreate, ProjectUpdate]):
    """Flavor Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[Project]:
        return Project

    @property
    def schema_create(self) -> type[ProjectCreate]:
        return ProjectCreate

    def create(self, *, obj_in: ProjectCreate, provider: Provider) -> Project:
        """Create a new Project.

        Connect the project to the given provider.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.provider.connect(provider)
        return db_obj


project_mgr = CRUDProject()
