from typing import Any

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
from tests.create_dict import flavor_schema_dict


def test_classes_inheritance():
    assert issubclass(FlavorBasePublic, BaseNode)

    assert issubclass(FlavorBase, FlavorBasePublic)

    assert issubclass(PrivateFlavorCreate, FlavorBase)
    assert issubclass(PrivateFlavorCreate, BaseNodeCreate)

    assert issubclass(SharedFlavorCreate, FlavorBase)
    assert issubclass(SharedFlavorCreate, BaseNodeCreate)

    assert issubclass(FlavorUpdate, FlavorBase)
    assert issubclass(FlavorUpdate, BaseNodeCreate)

    assert issubclass(FlavorReadPublic, BaseNodeRead)
    assert issubclass(FlavorReadPublic, BaseReadPublic)
    assert issubclass(FlavorReadPublic, FlavorBasePublic)

    assert issubclass(FlavorRead, BaseNodeRead)
    assert issubclass(FlavorRead, BaseReadPrivate)
    assert issubclass(FlavorRead, FlavorBase)


@parametrize_with_cases("key, value", has_tag="base_public")
def test_base_public(key: str, value: str) -> None:
    d = flavor_schema_dict()
    if key:
        d[key] = value
    item = FlavorBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = flavor_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = FlavorBase(**d)
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
    assert item.gpu_model == d.get("gpu_model")
    assert item.gpu_vendor == d.get("gpu_vendor")
    assert item.local_storage == d.get("local_storage")


@parametrize_with_cases("key, value", has_tag="base")
def test_create_private(key: str, value: Any) -> None:
    d = flavor_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = PrivateFlavorCreate(**d)
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
    assert item.gpu_model == d.get("gpu_model")
    assert item.gpu_vendor == d.get("gpu_vendor")
    assert item.local_storage == d.get("local_storage")
    assert item.is_public is False


@parametrize_with_cases("key, value", has_tag="base")
def test_create_shared(key: str, value: Any) -> None:
    d = flavor_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = SharedFlavorCreate(**d)
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
    assert item.gpu_model == d.get("gpu_model")
    assert item.gpu_vendor == d.get("gpu_vendor")
    assert item.local_storage == d.get("local_storage")
    assert item.is_public is True


def test_invalid_visibility() -> None:
    with pytest.raises(ValidationError):
        PrivateFlavorCreate(**flavor_schema_dict(), is_public=True)
    with pytest.raises(ValidationError):
        SharedFlavorCreate(**flavor_schema_dict(), is_public=False)


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = flavor_schema_dict()
    if key:
        d[key] = value
    item = FlavorUpdate(**d)
    assert item.name == d.get("name")
    assert item.uuid == (d.get("uuid").hex if d.get("uuid") else None)


@parametrize_with_cases("key, value", has_tag="base_public")
@parametrize_with_cases("flavor_model", has_tag="model")
def test_read_public(
    flavor_model: Flavor | PrivateFlavor | SharedFlavor, key: str, value: str
) -> None:
    if key:
        flavor_model.__setattr__(key, value)
    item = FlavorReadPublic.from_orm(flavor_model)

    assert item.uid
    assert item.uid == flavor_model.uid
    assert item.description == flavor_model.description
    assert item.name == flavor_model.name
    assert item.uuid == flavor_model.uuid


@parametrize_with_cases("key, value", has_tag="base")
@parametrize_with_cases("flavor_model", has_tag="model")
def test_read(
    flavor_model: Flavor | PrivateFlavor | SharedFlavor, key: str, value: Any
) -> None:
    if key:
        flavor_model.__setattr__(key, value)
        if key.startswith("gpu_"):
            flavor_model.__setattr__("gpus", 1)
    item = FlavorRead.from_orm(flavor_model)

    assert item.uid
    assert item.uid == flavor_model.uid
    assert item.description == flavor_model.description
    assert item.name == flavor_model.name
    assert item.uuid == flavor_model.uuid
    assert item.disk == flavor_model.disk
    assert item.ram == flavor_model.ram
    assert item.vcpus == flavor_model.vcpus
    assert item.swap == flavor_model.swap
    assert item.ephemeral == flavor_model.ephemeral
    assert item.gpus == flavor_model.gpus
    assert item.infiniband == flavor_model.infiniband
    assert item.gpu_model == flavor_model.gpu_model
    assert item.gpu_vendor == flavor_model.gpu_vendor
    assert item.local_storage == flavor_model.local_storage

    if isinstance(flavor_model, SharedFlavor):
        assert item.is_public is True
    elif isinstance(flavor_model, PrivateFlavor):
        assert item.is_public is False
    elif isinstance(flavor_model, Flavor):
        assert item.is_public is None
