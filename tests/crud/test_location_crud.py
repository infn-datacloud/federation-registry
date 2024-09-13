from fed_reg.crud import CRUDInterface
from fed_reg.location.crud import CRUDLocation, location_mgr


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDLocation, CRUDInterface)

    assert isinstance(location_mgr, CRUDLocation)
