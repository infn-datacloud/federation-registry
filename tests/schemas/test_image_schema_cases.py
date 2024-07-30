from typing import Literal, Optional

from pytest_cases import case, parametrize

from fed_reg.image.enum import ImageOS
from fed_reg.image.models import Image, PrivateImage, SharedImage
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags=["base_public", "base", "update"])
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags=["update"])
    @parametrize(attr=["name", "uuid"])
    def case_attr(self, attr: str) -> tuple[str, None]:
        return attr, None

    @case(tags=["base_public", "base"])
    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @case(tags=["base"])
    @parametrize(value=[True, False])
    @parametrize(attr=["cuda_support", "gpu_driver"])
    def case_boolean(self, attr: str, value: bool) -> tuple[str, bool]:
        return attr, value

    @case(tags=["base"])
    @parametrize(attr=["os_distro", "os_version", "architecture", "kernel_id"])
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()

    @case(tags=["base"])
    @parametrize(value=[i for i in ImageOS])
    def case_os_type(self, value: str) -> tuple[Literal["os_type"], ImageOS]:
        return "os_type", value

    @case(tags=["base"])
    @parametrize(len=(0, 1, 2))
    def case_tag_list(self, len: int) -> tuple[Literal["tags"], Optional[list[str]]]:
        return "tags", [random_lower_string() for _ in range(len)]

    @case(tags=["model"])
    def case_private_model(self, private_image_model: PrivateImage):
        return private_image_model

    @case(tags=["model"])
    def case_shared_model(self, shared_image_model: SharedImage):
        return shared_image_model

    @case(tags=["model"])
    def case_model(self, image_model: Image):
        return image_model
