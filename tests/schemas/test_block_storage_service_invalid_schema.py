from typing import Any

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    BlockStorageServiceCreateExtended,
)
from fed_reg.service.models import BlockStorageService
from fed_reg.service.schemas import BlockStorageServiceBase, BlockStorageServiceRead
from tests.schemas.utils import block_storage_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_base(key: str, value: Any) -> None:
    d = block_storage_service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        BlockStorageServiceBase(**d)


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_read(
    block_storage_service_model: BlockStorageService, key: str, value: str
) -> None:
    block_storage_service_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        BlockStorageServiceRead.from_orm(block_storage_service_model)


@parametrize_with_cases("quotas, msg", has_tag="create_extended")
def test_invalid_create_extended(
    quotas: list[BlockStorageQuotaCreateExtended], msg: str
) -> None:
    d = block_storage_service_schema_dict()
    d["quotas"] = quotas
    with pytest.raises(ValueError, match=msg):
        BlockStorageServiceCreateExtended(**d)
