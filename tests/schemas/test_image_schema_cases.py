from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.image.schemas import ImageBase, PrivateImageCreate, SharedImageCreate
from tests.schemas.utils import image_schema_dict, random_image_os_type
from tests.utils import random_lower_string


class CaseImageSchema:
    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return image_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**image_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_os_type(self) -> dict[str, Any]:
        return {**image_schema_dict(), "os_type": random_image_os_type()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_os_distro(self) -> dict[str, Any]:
        return {**image_schema_dict(), "os_distro": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_os_version(self) -> dict[str, Any]:
        return {**image_schema_dict(), "os_version": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_architecture(self) -> dict[str, Any]:
        return {**image_schema_dict(), "architecture": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_kernel_id(self) -> dict[str, Any]:
        return {**image_schema_dict(), "kernel_id": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_cuda_support(self) -> dict[str, Any]:
        return {**image_schema_dict(), "cuda_support": True}

    @case(tags=("dict", "valid", "base", "update"))
    def case_gpu_driver(self) -> dict[str, Any]:
        return {**image_schema_dict(), "gpu_driver": True}

    @case(tags=("dict", "valid", "base", "update"))
    def case_tags(self) -> dict[str, Any]:
        return {**image_schema_dict(), "tags": [random_lower_string()]}

    @case(tags=("dict", "valid"))
    def case_is_shared(self) -> dict[str, Any]:
        return {**image_schema_dict(), "is_shared": True}

    @case(tags=("dict", "valid"))
    def case_is_private(self) -> dict[str, Any]:
        return {**image_schema_dict(), "is_shared": False}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = image_schema_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_uuid(self) -> tuple[dict[str, Any], Literal["uuid"]]:
        d = image_schema_dict()
        d.pop("uuid")
        return d, "uuid"

    @case(tags="class")
    def case_base_class(self) -> type[ImageBase]:
        return ImageBase

    @case(tags="class")
    def case_private_class(self) -> type[PrivateImageCreate]:
        return PrivateImageCreate

    @case(tags="class")
    def case_shared_class(self) -> type[SharedImageCreate]:
        return SharedImageCreate


class CaseImageModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseImageSchema, has_tag=("dict", "valid", "base")
    )
    def case_image_model(self, data: dict[str, Any]) -> Image:
        return Image(**ImageBase(**data).dict()).save()

    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseImageSchema, has_tag=("dict", "valid", "base")
    )
    def case_private_image_class(self, data: dict[str, Any]) -> PrivateImage:
        return PrivateImage(**PrivateImageCreate(**data).dict()).save()

    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseImageSchema, has_tag=("dict", "valid", "base")
    )
    def case_shared_image_class(self, data: dict[str, Any]) -> SharedImage:
        return SharedImage(**SharedImageCreate(**data).dict()).save()
