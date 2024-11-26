from typing import Any
from uuid import uuid4

from pytest_cases import case

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from tests.utils import random_int, random_lower_string


class CaseFlavorDict:
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
    def case_disk(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "disk": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_ram(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "ram": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_vcpus(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "vcpus": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_swap(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "swap": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_ephemeral(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "ephemeral": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_gpus(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "gpus": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_gpu_model(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "gpu_model": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_gpu_vendor(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "gpu_vendor": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_infiniband(self) -> dict[str, Any]:
        return {"name": random_lower_string(), "uuid": uuid4().hex, "infiniband": True}

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> dict[str, Any]:
        return {"uuid": uuid4().hex}

    @case(tags=("dict", "invalid"))
    def case_missing_uuid(self) -> dict[str, Any]:
        return {"name": random_lower_string()}


class CaseFlavorModelClass:
    @case(tags="class")
    def case_flavor(self) -> type[Flavor]:
        return Flavor

    @case(tags=("class", "derived"))
    def case_private_flavor(self) -> type[PrivateFlavor]:
        return PrivateFlavor

    @case(tags=("class", "derived"))
    def case_shared_flavor(self) -> type[SharedFlavor]:
        return SharedFlavor


class CaseFlavorModel:
    @case(tags="model")
    def case_flavor_model(self, flavor_model: Flavor) -> Flavor:
        return flavor_model

    @case(tags=("model", "private"))
    def case_private_flavor_model(
        self, private_flavor_model: PrivateFlavor
    ) -> PrivateFlavor:
        return private_flavor_model

    @case(tags=("model", "shared"))
    def case_shared_flavor_model(
        self, shared_flavor_model: SharedFlavor
    ) -> SharedFlavor:
        return shared_flavor_model
