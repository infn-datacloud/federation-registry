from fed_reg.crud import CRUDInterface
from fed_reg.user_group.crud import CRUDUserGroup, user_group_mgr


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDUserGroup, CRUDInterface)

    assert isinstance(user_group_mgr, CRUDUserGroup)
