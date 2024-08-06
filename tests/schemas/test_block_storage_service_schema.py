from typing import Any

from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    BlockStorageServiceCreateExtended,
)
from fed_reg.service.enum import BlockStorageServiceName, ServiceType
from fed_reg.service.models import BlockStorageService
from fed_reg.service.schemas import (
    BlockStorageServiceBase,
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    BlockStorageServiceUpdate,
)
from tests.schemas.utils import block_storage_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = block_storage_service_schema_dict()
    if key:
        d[key] = value
    item = BlockStorageServiceBase(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.BLOCK_STORAGE.value
    assert item.name == d.get("name").value


@parametrize_with_cases("key, value", has_tag="base_public")
def test_read_public(
    block_storage_service_model: BlockStorageService, key: str, value: str
) -> None:
    if key:
        block_storage_service_model.__setattr__(key, value)
    item = BlockStorageServiceReadPublic.from_orm(block_storage_service_model)

    assert item.uid
    assert item.uid == block_storage_service_model.uid
    assert item.description == block_storage_service_model.description
    assert item.endpoint == block_storage_service_model.endpoint


@parametrize_with_cases("key, value", has_tag="base")
def test_read(
    block_storage_service_model: BlockStorageService, key: str, value: Any
) -> None:
    if key:
        if isinstance(value, BlockStorageServiceName):
            value = value.value
        block_storage_service_model.__setattr__(key, value)
    item = BlockStorageServiceRead.from_orm(block_storage_service_model)

    assert item.uid
    assert item.uid == block_storage_service_model.uid
    assert item.description == block_storage_service_model.description
    assert item.endpoint == block_storage_service_model.endpoint
    assert item.type == block_storage_service_model.type
    assert item.name == block_storage_service_model.name


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = block_storage_service_schema_dict()
    if key:
        d[key] = value
    item = BlockStorageServiceUpdate(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.BLOCK_STORAGE.value
    assert item.name == (d.get("name").value if d.get("name") else None)


@parametrize_with_cases("quotas", has_tag="create_extended")
def test_create_extended(quotas: list[BlockStorageQuotaCreateExtended]) -> None:
    d = block_storage_service_schema_dict()
    d["quotas"] = quotas
    item = BlockStorageServiceCreateExtended(**d)
    assert item.quotas == quotas


# TODO Test read extended classes
