from fed_reg.crud import CRUDInterface
from fed_reg.project.crud import CRUDProject, project_mgr
from fed_reg.project.models import Project
from fed_reg.project.schemas import ProjectCreate


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDProject, CRUDInterface)

    assert isinstance(project_mgr, CRUDProject)

    assert project_mgr.model == Project
    assert project_mgr.schema_create == ProjectCreate
