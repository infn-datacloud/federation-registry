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
from tests.models.utils import flavor_model_dict
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


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test FlavorBasePublic class' attribute values."""
    d = flavor_schema_dict(attr)
    item = FlavorBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    flavor_cls: type[FlavorBase] | type[PrivateFlavorCreate] | type[SharedFlavorCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on FlavorBase, PrivateFlavorCreate and SharedFlavorCreate.
    """
    d = flavor_schema_dict(attr)
    item = flavor_cls(**d)
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
    """Test PrivateFlavorCreate class' attribute values."""
    item = PrivateFlavorCreate(**flavor_schema_dict())
    assert item.is_public is False


def test_create_shared() -> None:
    """Test SharedFlavorCreate class' attribute values."""
    item = SharedFlavorCreate(**flavor_schema_dict())
    assert item.is_public is True


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test FlavorUpdate class' attribute values."""
    d = flavor_schema_dict(attr)
    item = FlavorUpdate(**d)
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
    """Test FlavorReadPublic class' attribute values."""
    d = flavor_schema_dict(attr, read=True)
    item = FlavorReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test FlavorRead class' attribute values.

    Consider also cases where we need to set the is_public attribute (usually populated
    by the correct model).
    """
    d = flavor_schema_dict(attr, read=True)
    item = FlavorRead(**d)
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


@parametrize_with_cases("flavor_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(
    flavor_cls: type[Flavor] | type[PrivateFlavor] | type[SharedFlavor], attr: str
) -> None:
    """Use the from_orm function of FlavorReadPublic to read data from an ORM."""
    model = flavor_cls(**flavor_model_dict(attr)).save()
    item = FlavorReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("flavor_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(
    flavor_cls: type[Flavor] | type[PrivateFlavor] | type[SharedFlavor], attr: str
) -> None:
    """Use the from_orm function of FlavorRead to read data from an ORM."""
    model = flavor_cls(**flavor_model_dict(attr)).save()
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
        assert item.is_public == model.is_public
    else:
        assert item.is_public is None


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for FlavorBasePublic."""
    with pytest.raises(ValueError):
        FlavorBasePublic(**flavor_schema_dict(attr, valid=False))


@parametrize_with_cases("flavor_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    flavor_cls: type[FlavorBase] | type[PrivateFlavorCreate] | type[SharedFlavorCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to FlavorBase, PrivateFlavorCreate and SharedFlavorCreate.
    """
    with pytest.raises(ValueError):
        flavor_cls(**flavor_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for FlavorUpdate."""
    with pytest.raises(ValueError):
        FlavorUpdate(**flavor_schema_dict(attr, valid=False))


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateFlavorCreate and SharedFlavorCreate."""
    with pytest.raises(ValidationError):
        PrivateFlavorCreate(**flavor_schema_dict(), is_public=True)
    with pytest.raises(ValidationError):
        SharedFlavorCreate(**flavor_schema_dict(), is_public=False)


@parametrize_with_cases("attr", has_tag=("invalid_attr", "read_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for FlavorReadPublic."""
    with pytest.raises(ValueError):
        FlavorReadPublic(**flavor_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "read"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for FlavorRead."""
    with pytest.raises(ValueError):
        FlavorRead(**flavor_schema_dict(attr, valid=False, read=True))
