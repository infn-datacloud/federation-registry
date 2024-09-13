from fed_reg.crud import CRUDInterface
from fed_reg.identity_provider.crud import CRUDIdentityProvider, identity_provider_mgr


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDIdentityProvider, CRUDInterface)

    assert isinstance(identity_provider_mgr, CRUDIdentityProvider)
