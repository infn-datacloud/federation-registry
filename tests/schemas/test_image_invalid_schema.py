from typing import Any

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.image.models import Image
from fed_reg.image.schemas import (
    ImageBase,
    ImageBasePublic,
    ImageRead,
    ImageReadPublic,
)
from tests.create_dict import image_schema_dict


@parametrize_with_cases("key, value", has_tag="base_public")
def test_invalid_base_public(key: str, value: None) -> None:
    d = image_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        ImageBasePublic(**d)


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_base(key: str, value: Any) -> None:
    d = image_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        ImageBase(**d)


@parametrize_with_cases("key, value", has_tag="base_public")
def test_invalid_read_public(image_model: Image, key: str, value: str) -> None:
    image_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        ImageReadPublic.from_orm(image_model)


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_read(image_model: Image, key: str, value: str) -> None:
    image_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        ImageRead.from_orm(image_model)
