import pytest
from neomodel import (
    CardinalityViolation,
    DoesNotExist,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize_with_cases

from fed_reg.auth_method.models import AuthMethod
from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.provider.models import Provider
from fed_reg.user_group.models import UserGroup
from tests.models.utils import (
    auth_method_model_dict,
    identity_provider_model_dict,
    provider_model_dict,
    user_group_model_dict,
)


@parametrize_with_cases("attr", has_tag="attr")
def test_identity_provider_attr(attr: str) -> None:
    """Test attribute values (default and set)."""
    d = identity_provider_model_dict(attr)
    item = IdentityProvider(**d)
    assert isinstance(item, IdentityProvider)
    assert item.uid is not None
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint")
    assert item.group_claim == d.get("group_claim")

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("attr", has_tag=("attr", "mandatory"))
def test_identity_provider_missing_mandatory_attr(attr: str) -> None:
    """Test IdentityProvider required attributes.

    Creating a model without required values raises a RequiredProperty error.
    """
    err_msg = f"property '{attr}' on objects of class {IdentityProvider.__name__}"
    d = identity_provider_model_dict()
    d.pop(attr)
    with pytest.raises(RequiredProperty, match=err_msg):
        IdentityProvider(**d).save()


def test_rel_def(identity_provider_model: IdentityProvider) -> None:
    """Test relationships definition."""
    assert isinstance(identity_provider_model.providers, RelationshipManager)
    assert identity_provider_model.providers.name
    assert identity_provider_model.providers.source
    assert isinstance(identity_provider_model.providers.source, IdentityProvider)
    assert identity_provider_model.providers.source.uid == identity_provider_model.uid
    assert identity_provider_model.providers.definition
    assert identity_provider_model.providers.definition["node_class"] == Provider

    assert isinstance(identity_provider_model.user_groups, RelationshipManager)
    assert identity_provider_model.user_groups.name
    assert identity_provider_model.user_groups.source
    assert isinstance(identity_provider_model.user_groups.source, IdentityProvider)
    assert identity_provider_model.user_groups.source.uid == identity_provider_model.uid
    assert identity_provider_model.user_groups.definition
    assert identity_provider_model.user_groups.definition["node_class"] == UserGroup


def test_required_rel(identity_provider_model: IdentityProvider) -> None:
    """Test Model required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        identity_provider_model.providers.all()
    with pytest.raises(CardinalityViolation):
        identity_provider_model.providers.single()


def test_single_linked_provider(
    identity_provider_model: IdentityProvider, provider_model: Provider
) -> None:
    """Verify `providers` relationship works correctly.

    Connect a single Provider to an IdentityProvider.
    """
    d = auth_method_model_dict()
    r = identity_provider_model.providers.connect(provider_model, d)
    assert isinstance(r, AuthMethod)
    assert r.idp_name == d["idp_name"]
    assert r.protocol == d["protocol"]

    assert len(identity_provider_model.providers.all()) == 1
    provider = identity_provider_model.providers.single()
    assert isinstance(provider, Provider)
    assert provider.uid == provider_model.uid


def test_multiple_linked_providers(identity_provider_model: IdentityProvider) -> None:
    """Verify `providers` relationship works correctly.

    Connect a multiple Provider to a IdentityProvider.
    """
    item = Provider(**provider_model_dict()).save()
    identity_provider_model.providers.connect(item, auth_method_model_dict())
    item = Provider(**provider_model_dict()).save()
    identity_provider_model.providers.connect(item, auth_method_model_dict())
    assert len(identity_provider_model.providers.all()) == 2


def test_optional_rel(identity_provider_model: IdentityProvider) -> None:
    """Test Model optional relationships."""
    assert len(identity_provider_model.user_groups.all()) == 0
    assert identity_provider_model.user_groups.single() is None


def test_single_linked_user_group(
    identity_provider_model: IdentityProvider, user_group_model: UserGroup
) -> None:
    """Verify `user_groups` relationship works correctly.

    Connect a single UserGroup to an IdentityProvider.
    """
    r = identity_provider_model.user_groups.connect(user_group_model)
    assert r is True

    assert len(identity_provider_model.user_groups.all()) == 1
    user_group = identity_provider_model.user_groups.single()
    assert isinstance(user_group, UserGroup)
    assert user_group.uid == user_group_model.uid


def test_multiple_linked_user_groups(identity_provider_model: IdentityProvider) -> None:
    """Verify `user_groups` relationship works correctly.

    Connect a multiple UserGroup to an IdentityProvider.
    """
    item = UserGroup(**user_group_model_dict()).save()
    identity_provider_model.user_groups.connect(item)
    item = UserGroup(**user_group_model_dict()).save()
    identity_provider_model.user_groups.connect(item)
    assert len(identity_provider_model.user_groups.all()) == 2


def test_pre_delete_hook(identity_provider_model: IdentityProvider) -> None:
    """Delete identity provider and all related user groups"""
    item1 = UserGroup(**user_group_model_dict()).save()
    identity_provider_model.user_groups.connect(item1)
    item2 = UserGroup(**user_group_model_dict()).save()
    identity_provider_model.user_groups.connect(item2)

    assert identity_provider_model.delete()
    assert identity_provider_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()
