from random import randint
from typing import Literal

from pytest_cases import case, parametrize

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags=["base_public", "base", "update"])
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags=["update"])
    @parametrize(attr=["name", "uuid"])
    def case_attr(self, attr: str) -> tuple[str, None]:
        return attr, None

    @case(tags=["base_public", "base"])
    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @case(tags=["base"])
    @parametrize(attr=["disk", "ram", "vcpus", "swap", "ephemeral", "gpus"])
    def case_integer(self, attr: str) -> tuple[str, int]:
        return attr, randint(0, 100)

    @case(tags=["base"])
    @parametrize(value=[True, False])
    @parametrize(attr=["infiniband"])
    def case_boolean(self, attr: str, value: bool) -> tuple[str, bool]:
        return attr, value

    @case(tags=["base"])
    @parametrize(attr=["gpu_model", "gpu_vendor", "local_storage"])
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()

    @case(tags=["model"])
    def case_private_model(self, private_flavor_model: PrivateFlavor):
        return private_flavor_model

    @case(tags=["model"])
    def case_shared_model(self, shared_flavor_model: SharedFlavor):
        return shared_flavor_model

    @case(tags=["model"])
    def case_model(self, flavor_model: Flavor):
        return flavor_model
