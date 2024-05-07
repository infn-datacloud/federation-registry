from typing import Any, Literal
from uuid import uuid4

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.models import BaseNodeCreate, BaseNodeQuery, BaseNodeRead
from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    BlockStorageServiceCreateExtended,
)
from fed_reg.service.enum import BlockStorageServiceName, ServiceType
from fed_reg.service.models import BlockStorageService
from fed_reg.service.schemas import (
    BlockStorageServiceBase,
    BlockStorageServiceCreate,
    BlockStorageServiceQuery,
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    BlockStorageServiceUpdate,
    ServiceBase,
)
from tests.create_dict import block_storage_service_schema_dict
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags=["base_public", "base", "update"])
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags=["base_public", "base"])
    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @case(tags=["base"])
    @parametrize(value=[i for i in BlockStorageServiceName])
    def case_name(self, value: int) -> tuple[Literal["name"], int]:
        return "name", value

    @case(tags=["create_extended"])
    @parametrize(len=[0, 1, 2, 3])
    def case_quotas(
        self,
        block_storage_quota_create_ext_schema: BlockStorageQuotaCreateExtended,
        len: int,
    ) -> list[BlockStorageQuotaCreateExtended]:
        if len == 1:
            return [block_storage_quota_create_ext_schema]
        elif len == 2:
            return [
                block_storage_quota_create_ext_schema,
                BlockStorageQuotaCreateExtended(project=uuid4()),
            ]
        elif len == 3:
            # Same project, different users scope
            quota2 = block_storage_quota_create_ext_schema.copy()
            quota2.per_user = not quota2.per_user
            return [block_storage_quota_create_ext_schema, quota2]
        else:
            return []


class CaseInvalidAttr:
    @case(tags=["base", "update"])
    @parametrize(attr=["endpoint", "name"])
    def case_none(self, attr: str) -> tuple[str, None]:
        return attr, None

    @case(tags=["base"])
    def case_endpoint(self) -> tuple[Literal["endpoint"], None]:
        return "endpoint", random_lower_string()

    @case(tags=["base"])
    @parametrize(value=[i for i in ServiceType if i != ServiceType.BLOCK_STORAGE])
    def case_type(self, value: ServiceType) -> tuple[Literal["type"], ServiceType]:
        return "type", value

    @case(tags=["create_extended"])
    def case_dup_quotas(
        self, block_storage_quota_create_ext_schema: BlockStorageQuotaCreateExtended
    ) -> tuple[list[BlockStorageQuotaCreateExtended], str]:
        return [
            block_storage_quota_create_ext_schema,
            block_storage_quota_create_ext_schema,
        ], "Multiple quotas on same project"


@parametrize_with_cases("key, value", cases=CaseAttr, has_tag=["base"])
def test_base(key: str, value: Any) -> None:
    assert issubclass(BlockStorageServiceBase, ServiceBase)
    d = block_storage_service_schema_dict()
    if key:
        d[key] = value
    item = BlockStorageServiceBase(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.BLOCK_STORAGE.value
    assert item.name == d.get("name").value


@parametrize_with_cases("key, value", cases=CaseInvalidAttr, has_tag=["base"])
def test_invalid_base(key: str, value: Any) -> None:
    d = block_storage_service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        BlockStorageServiceBase(**d)


def test_create() -> None:
    assert issubclass(BlockStorageServiceCreate, BaseNodeCreate)
    assert issubclass(BlockStorageServiceCreate, BlockStorageServiceBase)


@parametrize_with_cases(
    "key, value", cases=[CaseInvalidAttr, CaseAttr], has_tag=["update"]
)
def test_update(key: str, value: Any) -> None:
    assert issubclass(BlockStorageServiceUpdate, BaseNodeCreate)
    assert issubclass(BlockStorageServiceUpdate, BlockStorageServiceBase)
    d = block_storage_service_schema_dict()
    if key:
        d[key] = value
    item = BlockStorageServiceUpdate(**d)
    assert item.endpoint == d.get("endpoint")
    assert item.type == ServiceType.BLOCK_STORAGE.value
    assert item.name == (d.get("name").value if d.get("name") else None)


def test_query() -> None:
    assert issubclass(BlockStorageServiceQuery, BaseNodeQuery)


@parametrize_with_cases("quotas", cases=CaseAttr, has_tag=["create_extended"])
def test_create_extended(quotas: list[BlockStorageQuotaCreateExtended]) -> None:
    assert issubclass(BlockStorageServiceCreateExtended, BlockStorageServiceCreate)
    d = block_storage_service_schema_dict()
    d["quotas"] = quotas
    item = BlockStorageServiceCreateExtended(**d)
    assert item.quotas == quotas


@parametrize_with_cases(
    "quotas, msg", cases=CaseInvalidAttr, has_tag=["create_extended"]
)
def test_invalid_create_extended(
    quotas: list[BlockStorageQuotaCreateExtended], msg: str
) -> None:
    d = block_storage_service_schema_dict()
    d["quotas"] = quotas
    with pytest.raises(ValueError, match=msg):
        BlockStorageServiceCreateExtended(**d)


@parametrize_with_cases("key, value", cases=CaseAttr, has_tag=["base_public"])
def test_read_public(
    block_storage_service_model: BlockStorageService, key: str, value: str
) -> None:
    assert issubclass(BlockStorageServiceReadPublic, ServiceBase)
    assert issubclass(BlockStorageServiceReadPublic, BaseNodeRead)
    assert BlockStorageServiceReadPublic.__config__.orm_mode

    if key:
        block_storage_service_model.__setattr__(key, value)
    item = BlockStorageServiceReadPublic.from_orm(block_storage_service_model)

    assert item.uid
    assert item.uid == block_storage_service_model.uid
    assert item.description == block_storage_service_model.description
    assert item.endpoint == block_storage_service_model.endpoint


@parametrize_with_cases("key, value", cases=CaseAttr, has_tag=["base"])
def test_read(
    block_storage_service_model: BlockStorageService, key: str, value: Any
) -> None:
    assert issubclass(BlockStorageServiceRead, BlockStorageServiceBase)
    assert issubclass(BlockStorageServiceRead, BaseNodeRead)
    assert BlockStorageServiceRead.__config__.orm_mode

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


@parametrize_with_cases("key, value", cases=CaseInvalidAttr, has_tag=["base"])
def test_invalid_read(
    block_storage_service_model: BlockStorageService, key: str, value: str
) -> None:
    block_storage_service_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        BlockStorageServiceRead.from_orm(block_storage_service_model)


# TODO Test read extended classes
