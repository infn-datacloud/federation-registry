from fed_reg.crud import CRUDInterface
from fed_reg.location.crud import CRUDLocation, location_mgr
from fed_reg.location.models import Location
from fed_reg.location.schemas import LocationCreate


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDLocation, CRUDInterface)

    assert isinstance(location_mgr, CRUDLocation)

    assert location_mgr.model == Location
    assert location_mgr.schema_create == LocationCreate
