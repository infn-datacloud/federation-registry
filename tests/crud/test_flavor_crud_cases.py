from random import randint
from typing import Literal

from pytest_cases import case, parametrize

from fed_reg.flavor.crud import (
    CRUDFlavor,
    CRUDPrivateFlavor,
    CRUDSharedFlavor,
    flavor_mgr,
    private_flavor_mgr,
    shared_flavor_mgr,
)
from fed_reg.flavor.models import PrivateFlavor, SharedFlavor
from tests.utils import random_lower_string


class CaseCreateKeyValues:
    @case(tags="create")
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags="create")
    @parametrize(attr=["disk", "ram", "vcpus", "swap", "ephemeral", "gpus"])
    def case_integer(self, attr: str) -> tuple[str, int]:
        return attr, randint(0, 100)

    @case(tags="create")
    @parametrize(attr=["infiniband"])
    @parametrize(value=[True, False])
    def case_boolean(self, attr: str, value: bool) -> tuple[str, bool]:
        return attr, value

    @case(tags="create")
    @parametrize(attr=["description", "gpu_model", "gpu_vendor", "local_storage"])
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()


class CaseGetNonDefaultKeyValues:
    @case(tags="get_single")
    @parametrize(attr=["disk", "ram", "vcpus", "swap", "ephemeral", "gpus"])
    def case_integer(self, attr: str) -> tuple[str, int]:
        return attr, randint(1, 100)

    @case(tags="get_single")
    @parametrize(attr=["infiniband"])
    def case_boolean(self, attr: str) -> tuple[str, Literal[True]]:
        return attr, True

    @case(tags="get_single")
    @parametrize(attr=["description", "gpu_model", "gpu_vendor", "local_storage"])
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()


class CaseMandatoryKeys:
    @case(tags="mandatory")
    def case_uid(self) -> Literal["uid"]:
        return "uid"

    @case(tags="mandatory")
    def case_uuid(self) -> Literal["uuid"]:
        return "uuid"

    @case(tags="mandatory")
    def case_name(self) -> Literal["name"]:
        return "name"


class CaseManager:
    @case(tags=("manager", "shared", "private"))
    def case_flavor_mgr(self) -> CRUDFlavor:
        return flavor_mgr

    @case(tags=("manager", "private"))
    def case_private_flavor_mgr(self) -> CRUDPrivateFlavor:
        return private_flavor_mgr

    @case(tags=("manager", "shared"))
    def case_shared_flavor_mgr(self) -> CRUDSharedFlavor:
        return shared_flavor_mgr


class CaseFlavorModel:
    @case(tags="model")
    def case_shared_flavor_model(
        self, shared_flavor_model: SharedFlavor
    ) -> SharedFlavor:
        return shared_flavor_model

    @case(tags="model")
    def case_private_flavor_model(
        self, private_flavor_model: PrivateFlavor
    ) -> PrivateFlavor:
        return private_flavor_model
