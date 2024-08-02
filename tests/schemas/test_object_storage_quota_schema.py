from typing import Any
from uuid import uuid4

from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import ObjectStoreQuotaCreateExtended
from fed_reg.quota.enum import QuotaType
from fed_reg.quota.models import ObjectStoreQuota
from fed_reg.quota.schemas import (
    ObjectStoreQuotaBase,
    ObjectStoreQuotaRead,
    ObjectStoreQuotaReadPublic,
    ObjectStoreQuotaUpdate,
)


@parametrize_with_cases("key, value")
def test_base(key: str, value: Any) -> None:
    d = {key: value} if key else {}
    item = ObjectStoreQuotaBase(**d)
    assert item.per_user == d.get("per_user", False)
    assert item.type == QuotaType.OBJECT_STORE.value
    # TODO: understand attributes


@parametrize_with_cases("key, value", has_tag="base_public")
def test_read_public(
    object_store_quota_model: ObjectStoreQuota, key: str, value: str
) -> None:
    if key:
        object_store_quota_model.__setattr__(key, value)
    item = ObjectStoreQuotaReadPublic.from_orm(object_store_quota_model)

    assert item.uid
    assert item.uid == object_store_quota_model.uid
    assert item.description == object_store_quota_model.description
    assert item.per_user == object_store_quota_model.per_user


@parametrize_with_cases("key, value")
def test_read(object_store_quota_model: ObjectStoreQuota, key: str, value: Any) -> None:
    if key:
        object_store_quota_model.__setattr__(key, value)
    item = ObjectStoreQuotaRead.from_orm(object_store_quota_model)

    assert item.uid
    assert item.uid == object_store_quota_model.uid
    assert item.description == object_store_quota_model.description
    assert item.per_user == object_store_quota_model.per_user
    assert item.type == object_store_quota_model.type
    # TODO: Understand attributes


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = {key: value} if key else {}
    item = ObjectStoreQuotaUpdate(**d)
    assert item.type == QuotaType.OBJECT_STORE.value


def test_create_extended() -> None:
    d = {"project": uuid4()}
    item = ObjectStoreQuotaCreateExtended(**d)
    assert item.project == d["project"].hex


# TODO Test read extended classes
