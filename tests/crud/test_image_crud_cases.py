from typing import Literal

from pytest_cases import case, parametrize

from fed_reg.image.crud import (
    CRUDImage,
    CRUDPrivateImage,
    CRUDSharedImage,
    image_mgr,
    private_image_mgr,
    shared_image_mgr,
)
from fed_reg.image.enum import ImageOS
from fed_reg.image.models import PrivateImage, SharedImage
from tests.utils import random_lower_string


class CaseCreateKeyValues:
    @case(tags="create")
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags="create")
    @parametrize(value=[i for i in ImageOS])
    def case_os_type(self, value: str) -> tuple[Literal["os_type"], ImageOS]:
        return "os_type", value

    @case(tags="create")
    @parametrize(len=(0, 1, 2))
    def case_tag_list(self, len: int) -> tuple[Literal["tags"], list[str] | None]:
        return "tags", [random_lower_string() for _ in range(len)]

    @case(tags="create")
    @parametrize(attr=["cuda_support", "gpu_driver"])
    @parametrize(value=[True, False])
    def case_boolean(self, attr: str, value: bool) -> tuple[str, bool]:
        return attr, value

    @case(tags="create")
    @parametrize(
        attr=["description", "os_distro", "os_version", "architecture", "kernel_id"]
    )
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()


class CaseGetNonDefaultKeyValues:
    @case(tags="get_single")
    @parametrize(attr=["cuda_support", "gpu_driver"])
    def case_boolean(self, attr: str) -> tuple[str, Literal[True]]:
        return attr, True

    @case(tags="get_single")
    @parametrize(
        attr=["description", "os_distro", "os_version", "architecture", "kernel_id"]
    )
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()

    @case(tags="get_single")
    @parametrize(value=[i for i in ImageOS])
    def case_os_type(self, value: str) -> tuple[Literal["os_type"], ImageOS]:
        return "os_type", value

    @case(tags="get_single")
    @parametrize(len=(1, 2))
    def case_tag_list(self, len: int) -> tuple[Literal["tags"], list[str] | None]:
        return "tags", [random_lower_string() for _ in range(len)]


class CaseMandatoryKeys:
    @case(tags="mandatory")
    def case_uid(self) -> Literal["uid"]:
        return "uid"

    @case(tags="mandatory")
    def case_uuid(self) -> Literal["uuid"]:
        return "uuid"

    @case(tags="mandatory")
    def case_name(self) -> Literal["name"]:
        return "name"


class CaseManager:
    @case(tags=("manager", "shared", "private"))
    def case_image_mgr(self) -> CRUDImage:
        return image_mgr

    @case(tags=("manager", "private"))
    def case_private_image_mgr(self) -> CRUDPrivateImage:
        return private_image_mgr

    @case(tags=("manager", "shared"))
    def case_shared_image_mgr(self) -> CRUDSharedImage:
        return shared_image_mgr


class CaseImageModel:
    @case(tags="model")
    def case_shared_image_model(self, shared_image_model: SharedImage) -> SharedImage:
        return shared_image_model

    @case(tags="model")
    def case_private_image_model(
        self, private_image_model: PrivateImage
    ) -> PrivateImage:
        return private_image_model
