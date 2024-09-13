from fed_reg.crud import CRUDInterface
from fed_reg.region.crud import CRUDRegion, region_mgr


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDRegion, CRUDInterface)

    assert isinstance(region_mgr, CRUDRegion)
