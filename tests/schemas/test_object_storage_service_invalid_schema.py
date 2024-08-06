from typing import Any

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    ObjectStoreQuotaCreateExtended,
    ObjectStoreServiceCreateExtended,
)
from fed_reg.service.models import ObjectStoreService
from fed_reg.service.schemas import ObjectStoreServiceBase, ObjectStoreServiceRead
from tests.schemas.utils import object_store_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_base(key: str, value: Any) -> None:
    d = object_store_service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        ObjectStoreServiceBase(**d)


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_read(
    object_store_service_model: ObjectStoreService, key: str, value: str
) -> None:
    object_store_service_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        ObjectStoreServiceRead.from_orm(object_store_service_model)


@parametrize_with_cases("quotas, msg", has_tag="create_extended")
def test_invalid_create_extended(
    quotas: list[ObjectStoreQuotaCreateExtended], msg: str
) -> None:
    d = object_store_service_schema_dict()
    d["quotas"] = quotas
    with pytest.raises(ValueError, match=msg):
        ObjectStoreServiceCreateExtended(**d)


# TODO Test read extended classes
