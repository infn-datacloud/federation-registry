from fed_reg.crud import CRUDInterface
from fed_reg.sla.crud import CRUDSLA, sla_mgr


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDSLA, CRUDInterface)

    assert isinstance(sla_mgr, CRUDSLA)
