from pytest_cases import case, parametrize

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.flavor.schemas import FlavorBase, PrivateFlavorCreate, SharedFlavorCreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_base_public_optional(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base", "update"))
    @parametrize(
        value=(
            "disk",
            "ram",
            "vcpus",
            "swap",
            "ephemeral",
            "infiniband",
            "gpus",
            "gpu_model",
            "gpu_vendor",
            "local_storage",
        )
    )
    def case_optional(self, value: str) -> str:
        return value

    @case(tags=("attr", "create"))
    @parametrize(value=("is_shared", "is_private"))
    def case_visibility(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory_attr(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "update"))
    @parametrize(value=("disk", "ram", "vcpus", "swap", "ephemeral", "gpus"))
    def case_integer(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "update"))
    @parametrize(value=("gpu_model", "gpu_vendor"))
    def case_gpu_details(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[FlavorBase]:
        return FlavorBase

    @case(tags="class")
    def case_private_class(self) -> type[PrivateFlavorCreate]:
        return PrivateFlavorCreate

    @case(tags="class")
    def case_shared_class(self) -> type[SharedFlavorCreate]:
        return SharedFlavorCreate


class CaseModel:
    @case(tags="model")
    def case_private_flavor(self) -> type[PrivateFlavor]:
        return PrivateFlavor

    @case(tags="model")
    def case_shared_flavor(self) -> type[SharedFlavor]:
        return SharedFlavor

    @case(tags="model")
    def case_flavor(self) -> type[Flavor]:
        return Flavor
