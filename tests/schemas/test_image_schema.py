from typing import Any
from uuid import uuid4

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


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_base_public(data: dict[str, Any]) -> None:
    """Test ImageBasePublic class' mandatory and optional attributes."""
    item = ImageBasePublic(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("data", has_tag=("dict", "valid", "base"))
def test_base(
    image_cls: type[ImageBase] | type[PrivateImageCreate] | type[SharedImageCreate],
    data: dict[str, Any],
) -> None:
    """Test Image class' mandatory and optional attributes.

    Execute this test on ImageBase, PrivateImageCreate and SharedImageCreate.
    """
    item = image_cls(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex
    assert item.os_type == (data.get("os_type").value if data.get("os_type") else None)
    assert item.os_distro == data.get("os_distro", None)
    assert item.os_version == data.get("os_version", None)
    assert item.architecture == data.get("architecture", None)
    assert item.kernel_id == data.get("kernel_id", None)
    assert item.cuda_support == data.get("cuda_support", False)
    assert item.gpu_driver == data.get("gpu_driver", False)
    assert item.tags == data.get("tags", [])

    if isinstance(item, PrivateImageCreate):
        assert not item.is_shared
    if isinstance(item, SharedImageCreate):
        assert item.is_shared


@parametrize_with_cases("data", has_tag=("dict", "valid", "update"))
def test_update(data: dict[str, Any]) -> None:
    """Test ImageUpdate class' attribute values."""
    item = ImageUpdate(**data)
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == data.get("uuid").hex
    assert item.os_type == (
        data.get("os_type").value if data.get("os_type", None) else None
    )
    assert item.os_distro == data.get("os_distro", None)
    assert item.os_version == data.get("os_version", None)
    assert item.architecture == data.get("architecture", None)
    assert item.kernel_id == data.get("kernel_id", None)
    assert item.cuda_support == data.get("cuda_support", False)
    assert item.gpu_driver == data.get("gpu_driver", False)
    assert item.tags == data.get("tags", [])


@parametrize_with_cases("data", has_tag=("dict", "valid", "base_public"))
def test_read_public(data: dict[str, Any]) -> None:
    """Test ImageReadPublic class' attribute values."""
    uid = uuid4()
    item = ImageReadPublic(**data, uid=uid)
    assert item.schema_type == "public"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name")
    assert item.uuid == data.get("uuid").hex


@parametrize_with_cases("data", has_tag=("dict", "valid"))
def test_read(data: dict[str, Any]) -> None:
    """Test ImageRead class' attribute values.

    Consider also cases where we need to set the is_shared attribute (usually populated
    by the correct model).
    """
    uid = uuid4()
    item = ImageRead(**data, uid=uid)
    assert item.schema_type == "private"
    assert item.uid == uid.hex
    assert item.description == data.get("description", "")
    assert item.name == data.get("name", None)
    assert item.uuid == (data.get("uuid").hex if data.get("uuid") else None)
    assert item.os_type == (data.get("os_type").value if data.get("os_type") else None)
    assert item.os_distro == data.get("os_distro", None)
    assert item.os_version == data.get("os_version", None)
    assert item.architecture == data.get("architecture", None)
    assert item.kernel_id == data.get("kernel_id", None)
    assert item.cuda_support == data.get("cuda_support", False)
    assert item.gpu_driver == data.get("gpu_driver", False)
    assert item.tags == data.get("tags", [])


@parametrize_with_cases("model", has_tag="model")
def test_read_public_from_orm(model: Image | PrivateImage | SharedImage) -> None:
    """Use the from_orm function of ImageReadPublic to read data from an ORM."""
    item = ImageReadPublic.from_orm(model)
    assert item.schema_type == "public"
    assert item.uid == model.uid
    assert item.description == model.description
    assert item.name == model.name
    assert item.uuid == model.uuid


@parametrize_with_cases("model", has_tag="model")
def test_read_from_orm(model: Image | PrivateImage | SharedImage) -> None:
    """Use the from_orm function of ImageRead to read data from an ORM."""
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


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base_public"))
def test_invalid_base_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ImageBasePublic."""
    err_msg = rf"1 validation error for ImageBasePublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ImageBasePublic(**data)


@parametrize_with_cases("image_cls", has_tag="class")
@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "base"))
def test_invalid_base(
    image_cls: type[ImageBase] | type[PrivateImageCreate] | type[SharedImageCreate],
    data: dict[str, Any],
    attr: str,
) -> None:
    """Test invalid attributes for base and create.

    Apply to ImageBase, PrivateImageCreate and SharedImageCreate.
    """
    err_msg = rf"1 validation error for {image_cls.__name__}\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        image_cls(**data)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "update"))
def test_invalid_update(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ImageUpdate."""
    err_msg = rf"1 validation error for ImageUpdate\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ImageUpdate(**data)


def test_invalid_create_visibility() -> None:
    """Test invalid attributes for PrivateImageCreate and SharedImageCreate."""
    err_msg = r"1 validation error for PrivateImageCreate\sis_shared"
    with pytest.raises(ValidationError, match=err_msg):
        PrivateImageCreate(**image_schema_dict(), is_shared=True)
    err_msg = r"1 validation error for SharedImageCreate\sis_shared"
    with pytest.raises(ValidationError, match=err_msg):
        SharedImageCreate(**image_schema_dict(), is_shared=False)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read_public"))
def test_invalid_read_public(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ImageReadPublic."""
    uid = uuid4()
    err_msg = rf"1 validation error for ImageReadPublic\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ImageReadPublic(**data, uid=uid)


@parametrize_with_cases("data, attr", has_tag=("dict", "invalid", "read"))
def test_invalid_read(data: dict[str, Any], attr: str) -> None:
    """Test invalid attributes for ImageRead."""
    uid = uuid4()
    err_msg = rf"1 validation error for ImageRead\s{attr}"
    with pytest.raises(ValueError, match=err_msg):
        ImageRead(**data, uid=uid)
