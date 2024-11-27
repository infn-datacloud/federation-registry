from typing import Any
from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    DoesNotExist,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize_with_cases

from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.sla.models import SLA
from fed_reg.user_group.models import UserGroup
from tests.models.utils import identity_provider_model_dict, sla_model_dict


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_user_group_attr(data: dict[str, Any]) -> None:
    """Test attribute values (default and set)."""
    item = UserGroup(**data)
    assert isinstance(item, UserGroup)
    assert item.uid is not None
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")

    saved = item.save()
    assert saved.element_id_property
    assert saved.uid == item.uid


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid"))
def test_user_group_missing_mandatory_attr(data: dict[str, Any], attr: str) -> None:
    """Test UserGroup required attributes.

    Creating a model without required values raises a RequiredProperty error.
    """
    err_msg = f"property '{attr}' on objects of class {UserGroup.__name__}"
    with pytest.raises(RequiredProperty, match=err_msg):
        UserGroup(**data).save()


def test_rel_def(user_group_model: UserGroup) -> None:
    """Test relationships definition."""
    assert isinstance(user_group_model.identity_provider, RelationshipManager)
    assert user_group_model.identity_provider.name
    assert user_group_model.identity_provider.source
    assert isinstance(user_group_model.identity_provider.source, UserGroup)
    assert user_group_model.identity_provider.source.uid == user_group_model.uid
    assert user_group_model.identity_provider.definition
    assert (
        user_group_model.identity_provider.definition["node_class"] == IdentityProvider
    )

    assert isinstance(user_group_model.slas, RelationshipManager)
    assert user_group_model.slas.name
    assert user_group_model.slas.source
    assert isinstance(user_group_model.slas.source, UserGroup)
    assert user_group_model.slas.source.uid == user_group_model.uid
    assert user_group_model.slas.definition
    assert user_group_model.slas.definition["node_class"] == SLA


def test_required_rel(user_group_model: UserGroup) -> None:
    """Test UserGroup required relationships.

    A model without required relationships can exist but when querying those values, it
    raises a CardinalityViolation error.
    """
    with pytest.raises(CardinalityViolation):
        user_group_model.identity_provider.all()
    with pytest.raises(CardinalityViolation):
        user_group_model.identity_provider.single()


def test_single_linked_identity_provider(
    user_group_model: UserGroup, identity_provider_model: IdentityProvider
) -> None:
    """Verify `identity_provider` relationship works correctly.

    Connect a single IdentityProvider to a UserGroup.
    """
    r = user_group_model.identity_provider.connect(identity_provider_model)
    assert r is True

    assert len(user_group_model.identity_provider.all()) == 1
    identity_provider = user_group_model.identity_provider.single()
    assert isinstance(identity_provider, IdentityProvider)
    assert identity_provider.uid == identity_provider_model.uid


def test_multiple_linked_identity_provider(user_group_model: UserGroup) -> None:
    """Verify `identity_provider` relationship works correctly.

    Trying to connect multiple IdentityProvider to a UserGroup raises an
    AttemptCardinalityViolation error.
    """
    item = IdentityProvider(**identity_provider_model_dict()).save()
    user_group_model.identity_provider.connect(item)
    item = IdentityProvider(**identity_provider_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        user_group_model.identity_provider.connect(item)

    with patch("neomodel.sync_.match.QueryBuilder._count", return_value=0):
        user_group_model.identity_provider.connect(item)
        with pytest.raises(CardinalityViolation):
            user_group_model.identity_provider.all()


def test_optional_rel(user_group_model: UserGroup) -> None:
    """Test UserGroup optional relationships."""
    assert len(user_group_model.slas.all()) == 0
    assert user_group_model.slas.single() is None


def test_single_linked_sla(user_group_model: UserGroup, sla_model: SLA) -> None:
    """Verify `slas` relationship works correctly.

    Connect a single SLA to a UserGroup.
    """
    r = user_group_model.slas.connect(sla_model)
    assert r is True

    assert len(user_group_model.slas.all()) == 1
    sla = user_group_model.slas.single()
    assert isinstance(sla, SLA)
    assert sla.uid == sla_model.uid


def test_multiple_linked_slas(user_group_model: UserGroup) -> None:
    """Verify `slas` relationship works correctly.

    Connect multiple SLA to a UserGroup.
    """
    item = SLA(**sla_model_dict()).save()
    user_group_model.slas.connect(item)
    item = SLA(**sla_model_dict()).save()
    user_group_model.slas.connect(item)
    assert len(user_group_model.slas.all()) == 2


def test_pre_delete_hook(user_group_model: UserGroup) -> None:
    """Delete user group and all related SLAs"""
    item1 = SLA(**sla_model_dict()).save()
    user_group_model.slas.connect(item1)
    item2 = SLA(**sla_model_dict()).save()
    user_group_model.slas.connect(item2)

    assert user_group_model.delete()
    assert user_group_model.deleted
    with pytest.raises(DoesNotExist):
        item1.refresh()
    with pytest.raises(DoesNotExist):
        item2.refresh()
