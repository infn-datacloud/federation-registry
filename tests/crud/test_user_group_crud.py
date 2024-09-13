from fed_reg.crud import CRUDInterface
from fed_reg.user_group.crud import CRUDUserGroup, user_group_mgr
from fed_reg.user_group.models import UserGroup
from fed_reg.user_group.schemas import UserGroupCreate


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDUserGroup, CRUDInterface)

    assert isinstance(user_group_mgr, CRUDUserGroup)

    assert user_group_mgr.model == UserGroup
    assert user_group_mgr.schema_create == UserGroupCreate
