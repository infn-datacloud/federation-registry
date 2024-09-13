from fed_reg.crud import CRUDInterface
from fed_reg.region.crud import CRUDRegion, region_mgr
from fed_reg.region.models import Region
from fed_reg.region.schemas import RegionCreate


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDRegion, CRUDInterface)

    assert isinstance(region_mgr, CRUDRegion)

    assert region_mgr.model == Region
    assert region_mgr.schema_create == RegionCreate
