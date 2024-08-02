from pytest_cases import case, parametrize

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(
        value=(
            "description",
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


class CaseClass:
    @case(tags="class")
    def case_flavor(self) -> type[Flavor]:
        return Flavor

    @case(tags=("class", "derived"))
    def case_private_flavor(self) -> type[PrivateFlavor]:
        return PrivateFlavor

    @case(tags=("class", "derived"))
    def case_shared_flavor(self) -> type[SharedFlavor]:
        return SharedFlavor


class CaseModel:
    @case(tags="model")
    def case_flavor_model(self, flavor_model: Flavor) -> Flavor:
        return flavor_model

    @case(tags="model")
    def case_private_flavor_model(
        self, private_flavor_model: PrivateFlavor
    ) -> PrivateFlavor:
        return private_flavor_model

    @case(tags="model")
    def case_shared_flavor_model(
        self, shared_flavor_model: SharedFlavor
    ) -> SharedFlavor:
        return shared_flavor_model
