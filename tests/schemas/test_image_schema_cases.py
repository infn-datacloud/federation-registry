from pytest_cases import case, parametrize

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.image.schemas import ImageBase, PrivateImageCreate, SharedImageCreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base", "update"))
    @parametrize(
        value=(
            "os_type",
            "os_distro",
            "os_version",
            "architecture",
            "kernel_id",
            "cuda_support",
            "gpu_driver",
            "tags",
        )
    )
    def case_optional(self, value: str) -> str:
        return value

    @case(tags=("attr", "read"))
    @parametrize(value=("is_shared", "is_private"))
    def case_visibility(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("name", "uuid"))
    def case_missing_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "read_public", "read"))
    @parametrize(value=("uid",))
    def case_missing_uid(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[ImageBase]:
        return ImageBase

    @case(tags="class")
    def case_private_class(self) -> type[PrivateImageCreate]:
        return PrivateImageCreate

    @case(tags="class")
    def case_shared_class(self) -> type[SharedImageCreate]:
        return SharedImageCreate


class CaseModel:
    @case(tags="model")
    def case_private_image(self) -> type[PrivateImage]:
        return PrivateImage

    @case(tags="model")
    def case_shared_image(self) -> type[SharedImage]:
        return SharedImage

    @case(tags="model")
    def case_image(self) -> type[Image]:
        return Image
