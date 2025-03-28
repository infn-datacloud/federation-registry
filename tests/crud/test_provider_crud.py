from typing import Literal

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.provider.crud import provider_mgr
from fed_reg.provider.enum import ProviderStatus, ProviderType
from fed_reg.provider.models import Provider
from fed_reg.provider.schemas_extended import ProviderCreateExtended
from tests.create_dict import provider_model_dict
from tests.utils import random_lower_string


class CaseAttr:
    def case_uid(self) -> Literal["uid"]:
        return "uid"

    @case(tags=["not-uid", "not-enum"])
    @parametrize(value=["description", "name", "is_public", "support_emails"])
    def case_key(self, value: str) -> str:
        return value

    @case(tags=["not-uid", "enum"])
    @parametrize(value=["type", "status"])
    def case_enum_key(self, value: str) -> str:
        return value


class CaseProvider:
    @case(tags=["single"])
    @parametrize(full=[True, False])
    def case_single_provider(self, full: bool) -> Provider:
        d = provider_model_dict()
        if full:
            d["status"] = ProviderStatus.ACTIVE
            d["description"] = random_lower_string()
            d["support_emails"] = [random_lower_string()]
        return Provider(**d).save()

    @case(tags=["multi"])
    @parametrize(len=[1, 2])
    def case_providers_list(self, len: int) -> list[Provider]:
        providers = []
        for _ in range(len):
            providers.append(Provider(**provider_model_dict()).save())
        return providers

    @case(tags=["multi-single-match"])
    def case_providers_list_single_match(self) -> list[Provider]:
        providers = []
        statuses = [i for i in ProviderStatus]
        types = [i for i in ProviderType]
        for i in range(2):
            d = provider_model_dict()
            d["type"] = types[i]
            d["is_public"] = bool(i % 2)
            d["status"] = statuses[i]
            d["description"] = random_lower_string()
            d["support_emails"] = [random_lower_string()]
            providers.append(Provider(**d).save())
        return providers

    @case(tags=["multi-dup-matches"])
    def case_providers_list_dup_matches(self) -> list[Provider]:
        d = provider_model_dict()
        d["status"] = ProviderStatus.ACTIVE
        return [Provider(**d).save(), Provider(**d).save()]


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


@parametrize_with_cases("providers", cases=CaseProvider, has_tag=["multi"])
def test_read_multi(providers: Provider) -> None:
    items = provider_mgr.get_multi()
    assert len(items) == len(providers)
    for item in items:
        assert isinstance(item, Provider)


@parametrize_with_cases("providers", cases=CaseProvider, has_tag=["multi-single-match"])
@parametrize_with_cases("attr", cases=CaseAttr)
def test_read_multi_with_attr_single_match(
    providers: list[Provider], attr: str
) -> None:
    kwargs = {attr: providers[0].__getattribute__(attr)}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == 1
    assert items[0].uid == providers[0].uid


@parametrize_with_cases("providers", cases=CaseProvider, has_tag=["multi-dup-matches"])
@parametrize_with_cases("attr", cases=CaseAttr, has_tag=["not-uid"])
def test_read_multi_with_attr_dup_matches(providers: list[Provider], attr: str) -> None:
    kwargs = {attr: providers[0].__getattribute__(attr)}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == 2


@parametrize_with_cases("providers", cases=CaseProvider, has_tag=["multi-single-match"])
@parametrize_with_cases("attr", cases=CaseAttr, has_tag=["not-enum"])
def test_read_multi_sort(providers: list[Provider], attr: str) -> None:
    kwargs = {"sort": attr}
    items = provider_mgr.get_multi(**kwargs)
    assert len(items) == len(providers)
    sorted_providers = sorted(providers, key=lambda x: x.__getattribute__(attr))
    assert items[0].__getattribute__(attr) == sorted_providers[0].__getattribute__(attr)
    assert items[1].__getattribute__(attr) == sorted_providers[1].__getattribute__(attr)


@parametrize_with_cases("providers", cases=CaseProvider, has_tag=["multi-single-match"])
@parametrize_with_cases("attr", cases=CaseAttr, has_tag=["enum"])
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


@parametrize_with_cases("provider", cases=CaseProvider, has_tag=["single"])
@parametrize_with_cases("attr", cases=CaseAttr)
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
    with pytest.raises(AssertionError):
        provider_mgr.remove(db_obj=provider_model)


# TODO test update
