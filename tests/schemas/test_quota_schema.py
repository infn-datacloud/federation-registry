import pytest
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.quota.models import PrivateQuota, Quota, SharedQuota
from fed_reg.quota.schemas import (
    PrivateQuotaCreate,
    QuotaBase,
    QuotaBasePublic,
    QuotaRead,
    QuotaReadPublic,
    QuotaUpdate,
    SharedQuotaCreate,
)
from tests.schemas.utils import quota_model_dict, quota_schema_dict


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(Quota, BaseNode)

    assert issubclass(QuotaBase, QuotaBasePublic)

    assert issubclass(QuotaUpdate, QuotaBase)
    assert issubclass(QuotaUpdate, BaseNodeCreate)

    assert issubclass(QuotaReadPublic, BaseNodeRead)
    assert issubclass(QuotaReadPublic, BaseReadPublic)
    assert issubclass(QuotaReadPublic, QuotaBasePublic)
    assert QuotaReadPublic.__config__.orm_mode

    assert issubclass(QuotaRead, BaseNodeRead)
    assert issubclass(QuotaRead, BaseReadPrivate)
    assert issubclass(QuotaRead, QuotaBase)
    assert QuotaRead.__config__.orm_mode

    assert issubclass(PrivateQuotaCreate, QuotaBase)
    assert issubclass(PrivateQuotaCreate, BaseNodeCreate)

    assert issubclass(SharedQuotaCreate, QuotaBase)
    assert issubclass(SharedQuotaCreate, BaseNodeCreate)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test QuotaBasePublic class' attribute values."""
    d = quota_schema_dict(attr)
    item = QuotaBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("quota_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    quota_cls: type[QuotaBase] | type[PrivateQuotaCreate] | type[SharedQuotaCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on QuotaBase, PrivateQuotaCreate and SharedQuotaCreate.
    """
    d = quota_schema_dict(attr)
    item = quota_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.disk == d.get("disk", 0)
    assert item.ram == d.get("ram", 0)
    assert item.vcpus == d.get("vcpus", 0)
    assert item.swap == d.get("swap", 0)
    assert item.ephemeral == d.get("ephemeral", 0)
    assert item.gpus == d.get("gpus", 0)
    assert item.infiniband == d.get("infiniband", False)
    assert item.gpu_model == d.get("gpu_model", None)
    assert item.gpu_vendor == d.get("gpu_vendor", None)
    assert item.local_storage == d.get("local_storage", None)


def test_create_private() -> None:
    """Test PrivateQuotaCreate class' attribute values."""
    item = PrivateQuotaCreate(**quota_schema_dict())
    assert item.is_public is False


def test_create_shared() -> None:
    """Test SharedQuotaCreate class' attribute values."""
    item = SharedQuotaCreate(**quota_schema_dict())
    assert item.is_public is True


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test QuotaUpdate class' attribute values."""
    d = quota_schema_dict(attr)
    item = QuotaUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == (d.get("uuid").hex if d.get("uuid", None) else None)
    assert item.disk == d.get("disk", 0)
    assert item.ram == d.get("ram", 0)
    assert item.vcpus == d.get("vcpus", 0)
    assert item.swap == d.get("swap", 0)
    assert item.ephemeral == d.get("ephemeral", 0)
    assert item.gpus == d.get("gpus", 0)
    assert item.infiniband == d.get("infiniband", False)
    assert item.gpu_model == d.get("gpu_model", None)
    assert item.gpu_vendor == d.get("gpu_vendor", None)
    assert item.local_storage == d.get("local_storage", None)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test QuotaReadPublic class' attribute values."""
    d = quota_schema_dict(attr, read=True)
    item = QuotaReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test QuotaRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = quota_schema_dict(attr, read=True)
    item = QuotaRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == (d.get("uuid").hex if d.get("uuid") else None)
    assert item.disk == d.get("disk", 0)
    assert item.ram == d.get("ram", 0)
    assert item.vcpus == d.get("vcpus", 0)
    assert item.swap == d.get("swap", 0)
    assert item.ephemeral == d.get("ephemeral", 0)
    assert item.gpus == d.get("gpus", 0)
    assert item.infiniband == d.get("infiniband", False)
    assert item.gpu_model == d.get("gpu_model", None)
    assert item.gpu_vendor == d.get("gpu_vendor", None)
    assert item.local_storage == d.get("local_storage", None)
    assert item.is_public == d.get("is_public", None)


@parametrize_with_cases("quota_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(
    quota_cls: type[Quota] | type[PrivateQuota] | type[SharedQuota], attr: str
) -> None:
    """Use the from_orm function of QuotaReadPublic to read data from an ORM."""
    model = quota_cls(**quota_model_dict(attr)).save()
    item = QuotaReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("quota_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(
    quota_cls: type[Quota] | type[PrivateQuota] | type[SharedQuota], attr: str
) -> None:
    """Use the from_orm function of QuotaRead to read data from an ORM."""
    model = quota_cls(**quota_model_dict(attr)).save()
    item = QuotaRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid
    assert item.disk == model.disk
    assert item.ram == model.ram
    assert item.vcpus == model.vcpus
    assert item.swap == model.swap
    assert item.ephemeral == model.ephemeral
    assert item.gpus == model.gpus
    assert item.infiniband == model.infiniband
    assert item.gpu_model == model.gpu_model
    assert item.gpu_vendor == model.gpu_vendor
    assert item.local_storage == model.local_storage
    if isinstance(model, (PrivateQuota, SharedQuota)):
        assert item.is_public == model.is_public
    else:
        assert item.is_public is None


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for QuotaBasePublic."""
    with pytest.raises(ValueError):
        QuotaBasePublic(**quota_schema_dict(attr, valid=False))


@parametrize_with_cases("quota_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    quota_cls: type[QuotaBase] | type[PrivateQuotaCreate] | type[SharedQuotaCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to QuotaBase, PrivateQuotaCreate and SharedQuotaCreate.
    """
    with pytest.raises(ValueError):
        quota_cls(**quota_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for QuotaUpdate."""
    with pytest.raises(ValueError):
        QuotaUpdate(**quota_schema_dict(attr, valid=False))


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateQuotaCreate and SharedQuotaCreate."""
    with pytest.raises(ValidationError):
        PrivateQuotaCreate(**quota_schema_dict(), is_public=True)
    with pytest.raises(ValidationError):
        SharedQuotaCreate(**quota_schema_dict(), is_public=False)


@parametrize_with_cases("attr", has_tag=("invalid_attr", "read_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for QuotaReadPublic."""
    with pytest.raises(ValueError):
        QuotaReadPublic(**quota_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "read"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for QuotaRead."""
    with pytest.raises(ValueError):
        QuotaRead(**quota_schema_dict(attr, valid=False, read=True))
