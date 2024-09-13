from fed_reg.crud import CRUDInterface
from fed_reg.identity_provider.crud import CRUDIdentityProvider, identity_provider_mgr
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.identity_provider.schemas import IdentityProviderCreate


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDIdentityProvider, CRUDInterface)

    assert isinstance(identity_provider_mgr, CRUDIdentityProvider)

    assert identity_provider_mgr.model == IdentityProvider
    assert identity_provider_mgr.schema_create == IdentityProviderCreate
