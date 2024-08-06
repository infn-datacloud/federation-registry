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
    def case_description(self, value: str) -> str:
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

    @case(tags=("invalid_attr", "base", "update", "read"))
    @parametrize(
        value=(
            "disk",
            "ram",
            "vcpus",
            "swap",
            "ephemeral",
            "gpus",
            "gpu_model",
            "gpu_vendor",
        )
    )
    def case_optional(self, value: str) -> str:
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
