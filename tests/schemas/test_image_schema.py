import pytest
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.image.schemas import (
    ImageBase,
    ImageBasePublic,
    ImageRead,
    ImageReadPublic,
    ImageUpdate,
    PrivateImageCreate,
    SharedImageCreate,
)
from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from tests.models.utils import image_model_dict
from tests.schemas.utils import image_schema_dict


def test_classes_inheritance():
    """Test pydantic schema inheritance."""
    assert issubclass(ImageBasePublic, BaseNode)

    assert issubclass(ImageBase, ImageBasePublic)

    assert issubclass(ImageUpdate, ImageBase)
    assert issubclass(ImageUpdate, BaseNodeCreate)

    assert issubclass(ImageReadPublic, BaseNodeRead)
    assert issubclass(ImageReadPublic, BaseReadPublic)
    assert issubclass(ImageReadPublic, ImageBasePublic)
    assert ImageReadPublic.__config__.orm_mode

    assert issubclass(ImageRead, BaseNodeRead)
    assert issubclass(ImageRead, BaseReadPrivate)
    assert issubclass(ImageRead, ImageBase)
    assert ImageRead.__config__.orm_mode

    assert issubclass(PrivateImageCreate, ImageBase)
    assert issubclass(PrivateImageCreate, BaseNodeCreate)

    assert issubclass(SharedImageCreate, ImageBase)
    assert issubclass(SharedImageCreate, BaseNodeCreate)


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_base_public(attr: str) -> None:
    """Test ImageBasePublic class' attribute values."""
    d = image_schema_dict(attr)
    item = ImageBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_base(
    image_cls: type[ImageBase] | type[PrivateImageCreate] | type[SharedImageCreate],
    attr: str,
) -> None:
    """Test class' attribute values.

    Execute this test on ImageBase, PrivateImageCreate and SharedImageCreate.
    """
    d = image_schema_dict(attr)
    item = image_cls(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.os_type == (d.get("os_type").value if d.get("os_type") else None)
    assert item.os_distro == d.get("os_distro", None)
    assert item.os_version == d.get("os_version", None)
    assert item.architecture == d.get("architecture", None)
    assert item.kernel_id == d.get("kernel_id", None)
    assert item.cuda_support == d.get("cuda_support", False)
    assert item.gpu_driver == d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])


def test_create_private() -> None:
    """Test PrivateImageCreate class' attribute values."""
    item = PrivateImageCreate(**image_schema_dict())
    assert item.is_shared is False


def test_create_shared() -> None:
    """Test SharedImageCreate class' attribute values."""
    item = SharedImageCreate(**image_schema_dict())
    assert item.is_shared is True


@parametrize_with_cases("attr", has_tag=("attr", "update"))
def test_update(attr: str) -> None:
    """Test ImageUpdate class' attribute values."""
    d = image_schema_dict(attr)
    item = ImageUpdate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == d.get("uuid").hex
    assert item.os_type == (d.get("os_type").value if d.get("os_type", None) else None)
    assert item.os_distro == d.get("os_distro", None)
    assert item.os_version == d.get("os_version", None)
    assert item.architecture == d.get("architecture", None)
    assert item.kernel_id == d.get("kernel_id", None)
    assert item.cuda_support == d.get("cuda_support", False)
    assert item.gpu_driver == d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])


@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public(attr: str) -> None:
    """Test ImageReadPublic class' attribute values."""
    d = image_schema_dict(attr, read=True)
    item = ImageReadPublic(**d)
    assert item.schema_type == "public"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("attr", has_tag="attr")
def test_read(attr: str) -> None:
    """Test ImageRead class' attribute values.

    Consider also cases where we need to set the is_shared attribute (usually populated
    by the correct model).
    """
    d = image_schema_dict(attr, read=True)
    item = ImageRead(**d)
    assert item.schema_type == "private"
    assert item.uid == d.get("uid").hex
    assert item.description == d.get("description", "")
    assert item.name == d.get("name", None)
    assert item.uuid == (d.get("uuid").hex if d.get("uuid") else None)
    assert item.os_type == (d.get("os_type").value if d.get("os_type") else None)
    assert item.os_distro == d.get("os_distro", None)
    assert item.os_version == d.get("os_version", None)
    assert item.architecture == d.get("architecture", None)
    assert item.kernel_id == d.get("kernel_id", None)
    assert item.cuda_support == d.get("cuda_support", False)
    assert item.gpu_driver == d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])


@parametrize_with_cases("image_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base_public"))
def test_read_public_from_orm(
    image_cls: type[Image] | type[PrivateImage] | type[SharedImage], attr: str
) -> None:
    """Use the from_orm function of ImageReadPublic to read data from an ORM."""
    model = image_cls(**image_model_dict(attr)).save()
    item = ImageReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("image_cls", has_tag="model")
@parametrize_with_cases("attr", has_tag=("attr", "base"))
def test_read_from_orm(
    image_cls: type[Image] | type[PrivateImage] | type[SharedImage], attr: str
) -> None:
    """Use the from_orm function of ImageRead to read data from an ORM."""
    model = image_cls(**image_model_dict(attr)).save()
    item = ImageRead.from_orm(model)
    assert item.schema_type == "private"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid
    assert item.os_type == model.os_type
    assert item.os_distro == model.os_distro
    assert item.os_version == model.os_version
    assert item.architecture == model.architecture
    assert item.kernel_id == model.kernel_id
    assert item.cuda_support == model.cuda_support
    assert item.gpu_driver == model.gpu_driver
    assert item.tags == model.tags
    if isinstance(model, (PrivateImage, SharedImage)):
        assert item.is_shared == model.is_shared
    else:
        assert item.is_shared is None


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_base_public(attr: str) -> None:
    """Test invalid attributes for ImageBasePublic."""
    with pytest.raises(ValueError):
        ImageBasePublic(**image_schema_dict(attr, valid=False))


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_base(
    image_cls: type[ImageBase] | type[PrivateImageCreate] | type[SharedImageCreate],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to ImageBase, PrivateImageCreate and SharedImageCreate.
    """
    with pytest.raises(ValueError):
        image_cls(**image_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "update"))
def test_invalid_update(attr: str) -> None:
    """Test invalid attributes for ImageUpdate."""
    with pytest.raises(ValueError):
        ImageUpdate(**image_schema_dict(attr, valid=False))


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateImageCreate and SharedImageCreate."""
    with pytest.raises(ValidationError):
        PrivateImageCreate(**image_schema_dict(), is_shared=True)
    with pytest.raises(ValidationError):
        SharedImageCreate(**image_schema_dict(), is_shared=False)


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base_public"))
def test_invalid_read_public(attr: str) -> None:
    """Test invalid attributes for ImageReadPublic."""
    with pytest.raises(ValueError):
        ImageReadPublic(**image_schema_dict(attr, valid=False, read=True))


@parametrize_with_cases("attr", has_tag=("invalid_attr", "base"))
def test_invalid_read(attr: str) -> None:
    """Test invalid attributes for ImageRead."""
    with pytest.raises(ValueError):
        ImageRead(**image_schema_dict(attr, valid=False, read=True))
