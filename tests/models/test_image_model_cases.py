from typing import Any, Literal

from pytest_cases import case

from fed_reg.image.models import Image, PrivateImage, SharedImage
from tests.models.utils import image_model_dict
from tests.utils import random_lower_string


class CaseImageDict:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return image_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_os_type(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "os_type": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_os_distro(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "os_distro": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_os_version(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "os_version": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_architecture(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "architecture": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_kernel_id(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "kernel_id": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_cuda_support(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "cuda_support": True,
        }

    @case(tags=("dict", "valid"))
    def case_gpu_driver(self) -> dict[str, Any]:
        return {**image_model_dict(), "gpu_driver": True}

    @case(tags=("dict", "valid"))
    def case_tags(self) -> dict[str, Any]:
        return {
            **image_model_dict(),
            "tags": [random_lower_string()],
        }

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = image_model_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid"))
    def case_missing_uuid(self) -> tuple[dict[str, Any], Literal["uuid"]]:
        d = image_model_dict()
        d.pop("uuid")
        return d, "uuid"

    @case(tags="class")
    def case_image(self) -> type[Image]:
        return Image

    @case(tags=("class", "derived"))
    def case_private_image(self) -> type[PrivateImage]:
        return PrivateImage

    @case(tags=("class", "derived"))
    def case_shared_image(self) -> type[SharedImage]:
        return SharedImage

    @case(tags="model")
    def case_image_model(self, image_model: Image) -> Image:
        return image_model

    @case(tags=("model", "private"))
    def case_private_image_model(
        self, private_image_model: PrivateImage
    ) -> PrivateImage:
        return private_image_model

    @case(tags=("model", "shared"))
    def case_shared_image_model(self, shared_image_model: SharedImage) -> SharedImage:
        return shared_image_model
