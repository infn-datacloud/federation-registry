from fed_reg.crud import CRUDInterface
from fed_reg.sla.crud import CRUDSLA, sla_mgr
from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import SLACreate


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDSLA, CRUDInterface)

    assert isinstance(sla_mgr, CRUDSLA)
    assert sla_mgr.model == SLA
    assert sla_mgr.schema_create == SLACreate
