from fed_reg.crud import CRUDInterface
from fed_reg.project.crud import CRUDProject, project_mgr


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDProject, CRUDInterface)

    assert isinstance(project_mgr, CRUDProject)
