from typing import Any
from uuid import uuid4

from pytest_cases import case

from fed_reg.image.models import Image, PrivateImage, SharedImage
from tests.utils import random_lower_string


class CaseImageDict:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return {"name": random_lower_string(), "uuid": uuid4().hex}

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "description": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_os_type(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "os_type": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_os_distro(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "os_distro": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_os_version(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "os_version": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_architecture(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "architecture": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_kernel_id(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "kernel_id": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_cuda_support(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "cuda_support": True,
        }

    @case(tags=("dict", "valid"))
    def case_gpu_driver(self) -> dict[str, Any]:
        return {"name": random_lower_string(), "uuid": uuid4().hex, "gpu_driver": True}

    @case(tags=("dict", "valid"))
    def case_tags(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "tags": [random_lower_string()],
        }

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> dict[str, Any]:
        return {"uuid": uuid4().hex}

    @case(tags=("dict", "invalid"))
    def case_missing_uuid(self) -> dict[str, Any]:
        return {"name": random_lower_string()}


class CaseImageModelClass:
    @case(tags="class")
    def case_image(self) -> type[Image]:
        return Image

    @case(tags=("class", "derived"))
    def case_private_image(self) -> type[PrivateImage]:
        return PrivateImage

    @case(tags=("class", "derived"))
    def case_shared_image(self) -> type[SharedImage]:
        return SharedImage


class CaseImageModel:
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
