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
from tests.models.utils import sla_model_dict
from tests.schemas.utils import sla_schema_dict


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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test SLABasePublic class' attribute values."""
    d = sla_schema_dict(attr)
    item = SLABasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.doc_uuid == d.get("doc_uuid").hex


@parametrize_with_cases("sla_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    sla_cls: type[SLABase] | type[SLACreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on SLABase, PrivateSLACreate
    and SharedSLACreate.
    """
    d = sla_schema_dict(attr)
    item = sla_cls(**d)
    assert item.description == d.get("description", "")
    assert item.doc_uuid == d.get("doc_uuid").hex
    assert item.start_date == d.get("start_date")
    assert item.end_date == d.get("end_date")


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test SLAUpdate class' attribute values."""
    d = sla_schema_dict(attr)
    item = SLAUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.doc_uuid == (
        d.get("doc_uuid", None).hex if d.get("doc_uuid", None) else None
    )
    assert item.start_date == d.get("start_date", None)
    assert item.end_date == d.get("end_date", None)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test SLAReadPublic class' attribute values."""
    d = sla_schema_dict(attr, read=True)
    item = SLAReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.doc_uuid == d.get("doc_uuid").hex


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test SLARead class' attribute values."""
    d = sla_schema_dict(attr, read=True)
    item = SLARead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.doc_uuid == d.get("doc_uuid").hex
    assert item.start_date == d.get("start_date")
    assert item.end_date == d.get("end_date")


@parametrize_with_cases("sla_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(sla_cls: type[SLA], attr: str) -> None:
    """Use the from_orm function of SLAReadPublic to read data from ORM."""
    model = sla_cls(**sla_model_dict(attr)).save()
    item = SLAReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.doc_uuid == model.doc_uuid


@parametrize_with_cases("sla_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(sla_cls: type[SLA], attr: str) -> None:
    """Use the from_orm function of SLARead to read data from an ORM."""
    model = sla_cls(**sla_model_dict(attr)).save()
    item = SLARead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.doc_uuid == model.doc_uuid
    assert item.start_date == model.start_date
    assert item.end_date == model.end_date


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for SLABasePublic."""
    with pytest.raises(ValueError):
        SLABasePublic(**sla_schema_dict(attr, valid=False))


@parametrize_with_cases("sla_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    sla_cls: type[SLABase] | type[SLACreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to SLABase, PrivateSLACreate and
    SharedSLACreate.
    """
    with pytest.raises(ValueError):
        sla_cls(**sla_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for SLAUpdate."""
    with pytest.raises(ValueError):
        SLAUpdate(**sla_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for SLAReadPublic."""
    with pytest.raises(ValueError):
        SLAReadPublic(**sla_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for SLARead."""
    with pytest.raises(ValueError):
        SLARead(**sla_schema_dict(attr, valid=False, read=True))
