import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.crud import CRUDInterface
from fed_reg.provider.crud import CRUDProvider, provider_mgr
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas import ProviderCreate
from fed_reg.provider.schemas_extended import ProviderCreateExtended


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDProvider, CRUDInterface)

    assert isinstance(provider_mgr, CRUDProvider)

    assert provider_mgr.model == Provider
    assert provider_mgr.schema_create == ProviderCreate


# TODO parametrize with possible extended cases
def test_create(provider_create_ext_schema: ProviderCreateExtended) -> None:
    item = provider_mgr.create(obj_in=provider_create_ext_schema)
    assert isinstance(item, Provider)
    assert item.uid is not None
    assert item.description == provider_create_ext_schema.description
    assert item.name == provider_create_ext_schema.name
    assert item.type == provider_create_ext_schema.type
    assert item.is_public == provider_create_ext_schema.is_public
    assert item.status == provider_create_ext_schema.status
    assert item.support_emails == provider_create_ext_schema.support_emails
    assert len(item.identity_providers) == len(
        provider_create_ext_schema.identity_providers
    )
    assert len(item.projects) == len(provider_create_ext_schema.projects)
    assert len(item.regions) == len(provider_create_ext_schema.regions)


@parametrize_with_cases("providers", has_tag="multi")
def test_read_multi(providers: Provider) -> None:
    items = provider_mgr.get_multi()
    assert len(items) == len(providers)
    for item in items:
        assert isinstance(item, Provider)


@parametrize_with_cases("providers", has_tag="multi-single-match")
@parametrize_with_cases("attr", has_tag="base")
def test_read_multi_with_attr_single_match(
    providers: list[Provider], attr: str
) -> None:
    kwargs = {attr: providers[0].__getattribute__(attr)}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == 1
    assert items[0].uid == providers[0].uid


@parametrize_with_cases("providers", has_tag="multi-dup-matches")
@parametrize_with_cases("attr", has_tag="not-uid")
def test_read_multi_with_attr_dup_matches(providers: list[Provider], attr: str) -> None:
    kwargs = {attr: providers[0].__getattribute__(attr)}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == 2


@parametrize_with_cases("providers", has_tag="multi-single-match")
@parametrize_with_cases("attr", has_tag="not-enum")
def test_read_multi_sort(providers: list[Provider], attr: str) -> None:
    kwargs = {"sort": attr}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == len(providers)
    sorted_providers = sorted(providers, key=lambda x: x.__getattribute__(attr))
    assert items[0].__getattribute__(attr) == sorted_providers[0].__getattribute__(attr)
    assert items[1].__getattribute__(attr) == sorted_providers[1].__getattribute__(attr)


@parametrize_with_cases("providers", has_tag="multi-single-match")
@parametrize_with_cases("attr", has_tag="enum")
def test_read_multi_sort_enums(providers: list[Provider], attr: str) -> None:
    kwargs = {"sort": attr}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == len(providers)
    sorted_providers = sorted(providers, key=lambda x: x.__getattribute__(attr).value)
    assert items[0].__getattribute__(attr) == str(
        sorted_providers[0].__getattribute__(attr)
    )
    assert items[1].__getattribute__(attr) == str(
        sorted_providers[1].__getattribute__(attr)
    )


# TODO add tests get multi with skip, limit


def test_read_empty_list() -> None:
    items = provider_mgr.get_multi()
    assert len(items) == 0


def test_read_single(provider_model: Provider) -> None:
    item = provider_mgr.get()
    assert isinstance(item, Provider)
    assert item.uid == provider_model.uid


@parametrize_with_cases("provider", has_tag="single")
@parametrize_with_cases("attr", has_tag="base")
def test_read_single_with_attr(provider: Provider, attr: str) -> None:
    kwargs = {attr: provider.__getattribute__(attr)}
    if kwargs[attr] is None:
        assert not provider_mgr.get(**kwargs)
    else:
        item = provider_mgr.get(**kwargs)
        assert item.uid == provider.uid


def test_read_none() -> None:
    assert not provider_mgr.get()


def test_delete(provider_model: Provider) -> None:
    assert provider_mgr.remove(db_obj=provider_model)
    assert provider_model.deleted


def test_delete_not_existing(provider_model: Provider) -> None:
    assert provider_mgr.remove(db_obj=provider_model)
    with pytest.raises(ValueError):
        provider_mgr.remove(db_obj=provider_model)


# TODO test update
