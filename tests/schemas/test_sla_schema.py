from typing import Any
from uuid import uuid4

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import (
    SLABase,
    SLABasePublic,
    SLACreate,
    SLARead,
    SLAReadPublic,
    SLAUpdate,
)


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(SLABasePublic, BaseNode)

    assert issubclass(SLABase, SLABasePublic)

    assert issubclass(SLAUpdate, SLABase)
    assert issubclass(SLAUpdate, BaseNodeCreate)

    assert issubclass(SLAReadPublic, BaseNodeRead)
    assert issubclass(SLAReadPublic, BaseReadPublic)
    assert issubclass(SLAReadPublic, SLABasePublic)
    assert SLAReadPublic.__config__.orm_mode

    assert issubclass(SLARead, BaseNodeRead)
    assert issubclass(SLARead, BaseReadPrivate)
    assert issubclass(SLARead, SLABase)
    assert SLARead.__config__.orm_mode

    assert issubclass(SLACreate, SLABase)
    assert issubclass(SLACreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test SLABasePublic class' attribute values."""
    item = SLABasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.doc_uuid == data.get("doc_uuid").hex


@parametrize_with_cases("sla_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    sla_cls: type[SLABase] | type[SLACreate],
    data: dict[str, Any],
) -> None:
    """Test class' attribute values.

    Execute this test on SLABase, PrivateSLACreate
    and SharedSLACreate.
    """
    item = sla_cls(**data)
    assert item.description == data.get("description", "")
    assert item.doc_uuid == data.get("doc_uuid").hex
    assert item.start_date == data.get("start_date")
    assert item.end_date == data.get("end_date")


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test SLAUpdate class' attribute values."""
    item = SLAUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.doc_uuid == (
        data.get("doc_uuid", None).hex if data.get("doc_uuid", None) else None
    )
    assert item.start_date == data.get("start_date", None)
    assert item.end_date == data.get("end_date", None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test SLAReadPublic class' attribute values."""
    uid = uuid4()
    item = SLAReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.doc_uuid == data.get("doc_uuid").hex


@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_read(data: dict[str, Any]) -> None:
    """Test SLARead class' attribute values."""
    uid = uuid4()
    item = SLARead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.doc_uuid == data.get("doc_uuid").hex
    assert item.start_date == data.get("start_date")
    assert item.end_date == data.get("end_date")


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: SLA) -> None:
    """Use the from_orm function of SLAReadPublic to read data from ORM."""
    item = SLAReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.doc_uuid == model.doc_uuid


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: SLA) -> None:
    """Use the from_orm function of SLARead to read data from an ORM."""
    item = SLARead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.doc_uuid == model.doc_uuid
    assert item.start_date == model.start_date
    assert item.end_date == model.end_date


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for SLABasePublic."""
    err_msg = rf"1 validation error for SLABasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        SLABasePublic(**data)


@parametrize_with_cases("sla_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    sla_cls: type[SLABase] | type[SLACreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to SLABase, PrivateSLACreate and
    SharedSLACreate.
    """
    err_msg = rf"1 validation error for {sla_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        sla_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for SLAUpdate."""
    err_msg = rf"1 validation error for SLAUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        SLAUpdate(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for SLAReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for SLAReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        SLAReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for SLARead."""
    uid = uuid4()
    err_msg = rf"1 validation error for SLARead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        SLARead(**data, uid=uid)
