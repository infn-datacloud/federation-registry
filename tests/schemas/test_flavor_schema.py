from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.flavor.schemas import (
    FlavorBase,
    FlavorBasePublic,
    FlavorRead,
    FlavorReadPublic,
    FlavorUpdate,
    PrivateFlavorCreate,
    SharedFlavorCreate,
)
from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from tests.schemas.utils import flavor_schema_dict


def test_classes_inheritance() -> None:
    """Test pydantic schema inheritance."""
    assert issubclass(FlavorBasePublic, BaseNode)

    assert issubclass(FlavorBase, FlavorBasePublic)

    assert issubclass(FlavorUpdate, FlavorBase)
    assert issubclass(FlavorUpdate, BaseNodeCreate)

    assert issubclass(FlavorReadPublic, BaseNodeRead)
    assert issubclass(FlavorReadPublic, BaseReadPublic)
    assert issubclass(FlavorReadPublic, FlavorBasePublic)
    assert FlavorReadPublic.__config__.orm_mode

    assert issubclass(FlavorRead, BaseNodeRead)
    assert issubclass(FlavorRead, BaseReadPrivate)
    assert issubclass(FlavorRead, FlavorBase)
    assert FlavorRead.__config__.orm_mode

    assert issubclass(PrivateFlavorCreate, FlavorBase)
    assert issubclass(PrivateFlavorCreate, BaseNodeCreate)

    assert issubclass(SharedFlavorCreate, FlavorBase)
    assert issubclass(SharedFlavorCreate, BaseNodeCreate)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test FlavorBasePublic class' mandatory and optional attributes."""
    item = FlavorBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    flavor_cls: type[FlavorBase] | type[PrivateFlavorCreate] | type[SharedFlavorCreate],
    data: dict[str, Any],
) -> None:
    """Test Flavor class' mandatory and optional attributes.

    Execute this test on FlavorBase, PrivateFlavorCreate and SharedFlavorCreate.
    """
    item = flavor_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex
    assert item.disk == data.get("disk", 0)
    assert item.ram == data.get("ram", 0)
    assert item.vcpus == data.get("vcpus", 0)
    assert item.swap == data.get("swap", 0)
    assert item.ephemeral == data.get("ephemeral", 0)
    assert item.gpus == data.get("gpus", 0)
    assert item.infiniband == data.get("infiniband", False)
    assert item.gpu_model == data.get("gpu_model", None)
    assert item.gpu_vendor == data.get("gpu_vendor", None)
    assert item.local_storage == data.get("local_storage", None)

    if isinstance(item, PrivateFlavorCreate):
        assert not item.is_shared
    if isinstance(item, SharedFlavorCreate):
        assert item.is_shared


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test FlavorUpdate class' attribute values."""
    item = FlavorUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == (data.get("uuid").hex if data.get("uuid", None) else None)
    assert item.disk == data.get("disk", 0)
    assert item.ram == data.get("ram", 0)
    assert item.vcpus == data.get("vcpus", 0)
    assert item.swap == data.get("swap", 0)
    assert item.ephemeral == data.get("ephemeral", 0)
    assert item.gpus == data.get("gpus", 0)
    assert item.infiniband == data.get("infiniband", False)
    assert item.gpu_model == data.get("gpu_model", None)
    assert item.gpu_vendor == data.get("gpu_vendor", None)
    assert item.local_storage == data.get("local_storage", None)


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test FlavorReadPublic class' attribute values."""
    uid = uuid4()
    item = FlavorReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test FlavorRead class' attribute values.

    Consider also cases where we need to set the is_shared attribute (usually populated
    by the correct model).
    """
    uid = uuid4()
    item = FlavorRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == (data.get("uuid").hex if data.get("uuid") else None)
    assert item.disk == data.get("disk", 0)
    assert item.ram == data.get("ram", 0)
    assert item.vcpus == data.get("vcpus", 0)
    assert item.swap == data.get("swap", 0)
    assert item.ephemeral == data.get("ephemeral", 0)
    assert item.gpus == data.get("gpus", 0)
    assert item.infiniband == data.get("infiniband", False)
    assert item.gpu_model == data.get("gpu_model", None)
    assert item.gpu_vendor == data.get("gpu_vendor", None)
    assert item.local_storage == data.get("local_storage", None)
    assert item.is_shared == data.get("is_shared", None)


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Flavor | PrivateFlavor | SharedFlavor) -> None:
    """Use the from_orm function of FlavorReadPublic to read data from an ORM."""
    item = FlavorReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Flavor | PrivateFlavor | SharedFlavor) -> None:
    """Use the from_orm function of FlavorRead to read data from an ORM."""
    item = FlavorRead.from_orm(model)
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
    if isinstance(model, (PrivateFlavor, SharedFlavor)):
        assert item.is_shared == model.is_shared
    else:
        assert item.is_shared is None


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for FlavorBasePublic."""
    err_msg = rf"1 validation error for FlavorBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        FlavorBasePublic(**data)


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    flavor_cls: type[FlavorBase] | type[PrivateFlavorCreate] | type[SharedFlavorCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to FlavorBase, PrivateFlavorCreate and SharedFlavorCreate.
    """
    if attr in ("gpu_model", "gpu_vendor"):
        attr = "__root__"
    err_msg = rf"1 validation error for {flavor_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        flavor_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for FlavorUpdate."""
    if attr in ("gpu_model", "gpu_vendor"):
        attr = "__root__"
    err_msg = rf"1 validation error for FlavorUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        FlavorUpdate(**data)


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateFlavorCreate and SharedFlavorCreate."""
    err_msg = r"1 validation error for PrivateFlavorCreate\sis_shared"
    with pytest.raises(ValidationError, match=err_msg):
        PrivateFlavorCreate(**flavor_schema_dict(), is_shared=True)
    err_msg = r"1 validation error for SharedFlavorCreate\sis_shared"
    with pytest.raises(ValidationError, match=err_msg):
        SharedFlavorCreate(**flavor_schema_dict(), is_shared=False)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for FlavorReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for FlavorReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        FlavorReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for FlavorRead."""
    uid = uuid4()
    if attr in ("gpu_model", "gpu_vendor"):
        attr = "__root__"
    err_msg = rf"1 validation error for FlavorRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        FlavorRead(**data, uid=uid)
