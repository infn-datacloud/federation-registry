import pytest
from fedreg.identity_provider.models import IdentityProvider
from fedreg.provider.schemas_extended import UserGroupCreateExtended
from fedreg.user_group.models import UserGroup
from pytest_cases import parametrize_with_cases

from fed_reg.user_group.crud import user_group_mgr
from tests.utils import random_lower_string, random_url


@pytest.fixture
def identity_provider_model() -> IdentityProvider:
    """Identity provider model."""
    identity_provider = IdentityProvider(
        endpoint=str(random_url()), group_claim=random_lower_string()
    ).save()
    return identity_provider


@pytest.fixture
def user_group_model(identity_provider_model: IdentityProvider) -> UserGroup:
    """User group model belonging to the same identity provider."""
    user_group = UserGroup(name=random_lower_string()).save()
    identity_provider_model.user_groups.connect(user_group)
    return user_group


class CaseUserGroup:
    def case_user_group_create(self) -> UserGroupCreateExtended:
        """This user group points to the identity_provider_model."""
        return UserGroupCreateExtended(name=random_lower_string())


@parametrize_with_cases("item", cases=CaseUserGroup)
def test_create(
    item: UserGroupCreateExtended, identity_provider_model: IdentityProvider
) -> None:
    """Create a new istance"""
    db_obj = user_group_mgr.create(
        obj_in=item, identity_provider=identity_provider_model
    )
    assert db_obj is not None
    assert isinstance(db_obj, UserGroup)
    assert db_obj.identity_provider.is_connected(identity_provider_model)


@parametrize_with_cases("item", cases=CaseUserGroup)
def test_create_already_exists(
    item: UserGroupCreateExtended, user_group_model: UserGroup
) -> None:
    """A user_group with the given uuid already exists"""
    identity_provider = user_group_model.identity_provider.single()

    item.name = user_group_model.name

    msg = (
        f"User group with name {item.name} already exists on identity provider "
        f"{identity_provider.endpoint}."
    )
    with pytest.raises(AssertionError, match=msg):
        user_group_mgr.create(obj_in=item, identity_provider=identity_provider)


@parametrize_with_cases("item", cases=CaseUserGroup)
def test_update(item: UserGroupCreateExtended, user_group_model: UserGroup) -> None:
    """Completely update the user group attributes. Also override not set ones."""
    db_obj = user_group_mgr.update(obj_in=item, db_obj=user_group_model)

    assert db_obj is not None
    assert isinstance(db_obj, UserGroup)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseUserGroup)
def test_update_no_changes(
    item: UserGroupCreateExtended, user_group_model: UserGroup
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.name = user_group_model.name

    db_obj = user_group_mgr.update(obj_in=item, db_obj=user_group_model)

    assert db_obj is None
