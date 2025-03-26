import pytest
from fedreg.identity_provider.models import IdentityProvider
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import IdentityProviderCreateExtended
from fedreg.user_group.models import UserGroup
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.identity_provider.crud import identity_provider_mng
from tests.utils import random_lower_string, random_provider_type, random_url


@pytest.fixture
def stand_alone_provider_model() -> Provider:
    """Provider model."""
    return Provider(name=random_lower_string(), type=random_provider_type()).save()


@pytest.fixture
def provider_model() -> Provider:
    """Provider model."""
    return Provider(name=random_lower_string(), type=random_provider_type()).save()


@pytest.fixture
def identity_provider_model(provider_model: Provider) -> IdentityProvider:
    """Identity provider model.

    The parent identity provider is connected to the project's provider.
    """
    identity_provider = IdentityProvider(
        endpoint=str(random_url()), group_claim=random_lower_string()
    ).save()
    user_group = UserGroup(name=random_lower_string()).save()
    provider_model.identity_providers.connect(
        identity_provider,
        {"protocol": random_lower_string(), "idp_name": random_lower_string()},
    )
    identity_provider.user_groups.connect(user_group)
    return identity_provider


class CaseIdentityProvider:
    @case(tags="base")
    def case_identity_provider_create(self) -> IdentityProviderCreateExtended:
        """This user group points to the identity_provider_model."""
        return IdentityProviderCreateExtended(
            endpoint=random_url(), group_claim=random_lower_string()
        )

    @case(tags="with_rel")
    def case_identity_provider_create_with_rel(self) -> IdentityProviderCreateExtended:
        """This user group points to the identity_provider_model."""
        return IdentityProviderCreateExtended(
            endpoint=random_url(),
            group_claim=random_lower_string(),
            relationship={
                "protocol": random_lower_string(),
                "idp_name": random_lower_string(),
            },
        )

    @case(tags="user_groups")
    @parametrize(tot_groups=(1, 2))
    def case_identity_provider_create_with_groups(
        self, tot_groups: int
    ) -> IdentityProviderCreateExtended:
        """This user group points to the identity_provider_model."""
        user_groups = []
        for _ in range(tot_groups):
            user_group = {"name": random_lower_string()}
            user_groups.append(user_group)
        return IdentityProviderCreateExtended(
            endpoint=random_url(),
            group_claim=random_lower_string(),
            relationship={
                "protocol": random_lower_string(),
                "idp_name": random_lower_string(),
            },
            user_groups=user_groups,
        )


@parametrize_with_cases("item", cases=CaseIdentityProvider)
def test_create(item: IdentityProviderCreateExtended) -> None:
    """Create a new istance"""
    db_obj = identity_provider_mng.create(obj_in=item)
    assert db_obj is not None
    assert isinstance(db_obj, IdentityProvider)
    assert len(db_obj.user_groups) == len(item.user_groups)


@parametrize_with_cases("item", cases=CaseIdentityProvider, has_tag="with_rel")
def test_create_and_connect_to_provider(
    item: IdentityProviderCreateExtended, provider_model: Provider
) -> None:
    """Create a new istance"""
    db_obj = identity_provider_mng.create(obj_in=item, provider=provider_model)
    assert db_obj is not None
    assert isinstance(db_obj, IdentityProvider)
    assert len(db_obj.user_groups) == len(item.user_groups)
    assert db_obj.providers.is_connected(provider_model)
    rel = db_obj.providers.relationship(provider_model)
    assert rel is not None
    assert rel.protocol == item.relationship.protocol
    assert rel.idp_name == item.relationship.idp_name


@parametrize_with_cases("item", cases=CaseIdentityProvider, has_tag="base")
def test_create_already_exists(
    item: IdentityProviderCreateExtended, identity_provider_model: IdentityProvider
) -> None:
    """A user_group with the given uuid already exists"""
    item.endpoint = identity_provider_model.endpoint
    msg = f"Identity provider with endpoint {item.endpoint} already exists."
    with pytest.raises(AssertionError, match=msg):
        identity_provider_mng.create(obj_in=item)


@parametrize_with_cases("item", cases=CaseIdentityProvider)
def test_update(
    item: IdentityProviderCreateExtended, identity_provider_model: IdentityProvider
) -> None:
    """Completely update the user group attributes. Also override not set ones."""
    db_obj = identity_provider_mng.update(obj_in=item, db_obj=identity_provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, IdentityProvider)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.user_groups) == len(item.user_groups)


@parametrize_with_cases("item", cases=CaseIdentityProvider, has_tag="base")
def test_update_no_changes(
    item: IdentityProviderCreateExtended, identity_provider_model: IdentityProvider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.endpoint = identity_provider_model.endpoint
    item.group_claim = identity_provider_model.group_claim
    groups = []
    for user_group in identity_provider_model.user_groups:
        d = {"name": user_group.name}
        groups.append(d)
    item.user_groups = groups

    db_obj = identity_provider_mng.update(obj_in=item, db_obj=identity_provider_model)

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseIdentityProvider, has_tag="base")
def test_update_only_content(
    item: IdentityProviderCreateExtended, identity_provider_model: IdentityProvider
) -> None:
    """The new item is equal to the existing one. No changes."""
    groups = []
    for user_group in identity_provider_model.user_groups:
        d = {"name": user_group.name}
        groups.append(d)
    item.user_groups = groups

    db_obj = identity_provider_mng.update(obj_in=item, db_obj=identity_provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, IdentityProvider)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.user_groups) == len(item.user_groups)


@parametrize_with_cases("item", cases=CaseIdentityProvider, has_tag="base")
def test_update_only_user_groups(
    item: IdentityProviderCreateExtended, identity_provider_model: IdentityProvider
) -> None:
    """The new item is equal to the existing one. No changes."""
    item.endpoint = identity_provider_model.endpoint
    item.group_claim = identity_provider_model.group_claim

    db_obj = identity_provider_mng.update(obj_in=item, db_obj=identity_provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, IdentityProvider)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.user_groups) == len(item.user_groups)
