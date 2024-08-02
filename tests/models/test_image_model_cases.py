from pytest_cases import case, parametrize

from fed_reg.image.models import Image, PrivateImage, SharedImage


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(
        value=(
            "description",
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


class CaseClass:
    @case(tags="class")
    def case_image(self) -> type[Image]:
        return Image

    @case(tags=("class", "derived"))
    def case_private_image(self) -> type[PrivateImage]:
        return PrivateImage

    @case(tags=("class", "derived"))
    def case_shared_image(self) -> type[SharedImage]:
        return SharedImage


class CaseModel:
    @case(tags="model")
    def case_image_model(self, image_model: Image) -> Image:
        return image_model

    @case(tags="model")
    def case_private_image_model(
        self, private_image_model: PrivateImage
    ) -> PrivateImage:
        return private_image_model

    @case(tags="model")
    def case_shared_image_model(self, shared_image_model: SharedImage) -> SharedImage:
        return shared_image_model
