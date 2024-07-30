from typing import Any

import pytest
from pydantic import ValidationError
from pytest_cases import parametrize_with_cases

from fed_reg.image.enum import ImageOS
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
from tests.create_dict import image_schema_dict


def test_classes_inheritance():
    assert issubclass(ImageBasePublic, BaseNode)

    assert issubclass(ImageBase, ImageBasePublic)

    assert issubclass(PrivateImageCreate, ImageBase)
    assert issubclass(PrivateImageCreate, BaseNodeCreate)

    assert issubclass(SharedImageCreate, ImageBase)
    assert issubclass(SharedImageCreate, BaseNodeCreate)

    assert issubclass(ImageUpdate, ImageBase)
    assert issubclass(ImageUpdate, BaseNodeCreate)

    assert issubclass(ImageReadPublic, BaseNodeRead)
    assert issubclass(ImageReadPublic, BaseReadPublic)
    assert issubclass(ImageReadPublic, ImageBasePublic)

    assert issubclass(ImageRead, BaseNodeRead)
    assert issubclass(ImageRead, BaseReadPrivate)
    assert issubclass(ImageRead, ImageBase)


@parametrize_with_cases("key, value", has_tag="base_public")
def test_base_public(key: str, value: str) -> None:
    d = image_schema_dict()
    if key:
        d[key] = value
    item = ImageBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex


@parametrize_with_cases("key, value", has_tag="base")
def test_base(key: str, value: Any) -> None:
    d = image_schema_dict()
    if key:
        d[key] = value
    item = ImageBase(**d)
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.os_type == (d.get("os_type").value if d.get("os_type") else None)
    assert item.os_distro == d.get("os_distro")
    assert item.os_version == d.get("os_version")
    assert item.architecture == d.get("architecture")
    assert item.kernel_id == d.get("kernel_id")
    assert item.cuda_support == d.get("cuda_support", False)
    assert item.gpu_driver == d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])


@parametrize_with_cases("key, value", has_tag="base")
def test_create_private(key: str, value: Any) -> None:
    d = image_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = PrivateImageCreate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.os_type == (d.get("os_type").value if d.get("os_type") else None)
    assert item.os_distro == d.get("os_distro")
    assert item.os_version == d.get("os_version")
    assert item.architecture == d.get("architecture")
    assert item.kernel_id == d.get("kernel_id")
    assert item.cuda_support == d.get("cuda_support", False)
    assert item.gpu_driver == d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])
    assert item.is_public is False


@parametrize_with_cases("key, value", has_tag="base")
def test_create_shared(key: str, value: Any) -> None:
    d = image_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    item = SharedImageCreate(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")
    assert item.uuid == d.get("uuid").hex
    assert item.os_type == (d.get("os_type").value if d.get("os_type") else None)
    assert item.os_distro == d.get("os_distro")
    assert item.os_version == d.get("os_version")
    assert item.architecture == d.get("architecture")
    assert item.kernel_id == d.get("kernel_id")
    assert item.cuda_support == d.get("cuda_support", False)
    assert item.gpu_driver == d.get("gpu_driver", False)
    assert item.tags == d.get("tags", [])
    assert item.is_public is True


def test_invalid_visibility() -> None:
    with pytest.raises(ValidationError):
        PrivateImageCreate(**image_schema_dict(), is_public=True)
    with pytest.raises(ValidationError):
        SharedImageCreate(**image_schema_dict(), is_public=False)


@parametrize_with_cases("key, value", has_tag="update")
def test_update(key: str, value: Any) -> None:
    d = image_schema_dict()
    if key:
        d[key] = value
    item = ImageUpdate(**d)
    assert item.name == d.get("name")
    assert item.uuid == (d.get("uuid").hex if d.get("uuid") else None)


@parametrize_with_cases("key, value", has_tag="base_public")
@parametrize_with_cases("image_model", has_tag="model")
def test_read_public(
    image_model: Image | PrivateImage | SharedImage, key: str, value: str
) -> None:
    if key:
        image_model.__setattr__(key, value)
    item = ImageReadPublic.from_orm(image_model)

    assert item.uid
    assert item.uid == image_model.uid
    assert item.description == image_model.description
    assert item.name == image_model.name
    assert item.uuid == image_model.uuid


@parametrize_with_cases("key, value", has_tag="base")
@parametrize_with_cases("image_model", has_tag="model")
def test_read(
    image_model: Image | PrivateImage | SharedImage, key: str, value: Any
) -> None:
    if key:
        if isinstance(value, ImageOS):
            value = value.value
        image_model.__setattr__(key, value)
    item = ImageRead.from_orm(image_model)

    assert item.uid
    assert item.uid == image_model.uid
    assert item.description == image_model.description
    assert item.name == image_model.name
    assert item.uuid == image_model.uuid
    assert item.os_type == image_model.os_type
    assert item.os_distro == image_model.os_distro
    assert item.os_version == image_model.os_version
    assert item.architecture == image_model.architecture
    assert item.kernel_id == image_model.kernel_id
    assert item.cuda_support == image_model.cuda_support
    assert item.gpu_driver == image_model.gpu_driver
    assert item.tags == image_model.tags

    if isinstance(image_model, SharedImage):
        assert item.is_public is True
    elif isinstance(image_model, PrivateImage):
        assert item.is_public is False
    elif isinstance(image_model, Image):
        assert item.is_public is None
