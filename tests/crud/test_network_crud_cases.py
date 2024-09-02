from random import randint
from typing import Literal

from pytest_cases import case, parametrize

from fed_reg.network.crud import (
    CRUDNetwork,
    CRUDPrivateNetwork,
    CRUDSharedNetwork,
    network_mgr,
    private_network_mgr,
    shared_network_mgr,
)
from fed_reg.network.models import PrivateNetwork, SharedNetwork
from tests.utils import random_lower_string


class CaseCreateKeyValues:
    @case(tags="create")
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags="create")
    @parametrize(attr=["mtu"])
    def case_integer(self, attr: str) -> tuple[str, int]:
        return attr, randint(0, 100)

    @case(tags="create")
    @parametrize(attr=("is_router_external", "is_default"))
    @parametrize(value=[True, False])
    def case_boolean(self, attr: str, value: bool) -> tuple[str, bool]:
        return attr, value

    @case(tags="create")
    @parametrize(attr=("description", "proxy_host", "proxy_user"))
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()

    @case(tags="create")
    @parametrize(len=(0, 1, 2))
    def case_tag_list(self, len: int) -> tuple[Literal["tags"], list[str] | None]:
        return "tags", [random_lower_string() for _ in range(len)]


class CaseGetNonDefaultKeyValues:
    @case(tags="get_single")
    @parametrize(attr=["mtu"])
    def case_integer(self, attr: str) -> tuple[str, int]:
        return attr, randint(1, 100)

    @case(tags="get_single")
    @parametrize(attr=("is_router_external", "is_default"))
    def case_boolean(self, attr: str) -> tuple[str, Literal[True]]:
        return attr, True

    @case(tags="get_single")
    @parametrize(attr=("description", "proxy_host", "proxy_user"))
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()

    @case(tags="get_single")
    @parametrize(len=(1, 2))
    def case_tag_list(self, len: int) -> tuple[Literal["tags"], list[str] | None]:
        return "tags", [random_lower_string() for _ in range(len)]


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
    def case_network_mgr(self) -> CRUDNetwork:
        return network_mgr

    @case(tags=("manager", "private"))
    def case_private_network_mgr(self) -> CRUDPrivateNetwork:
        return private_network_mgr

    @case(tags=("manager", "shared"))
    def case_shared_network_mgr(self) -> CRUDSharedNetwork:
        return shared_network_mgr


class CaseNetworkModel:
    @case(tags="model")
    def case_shared_network_model(
        self, shared_network_model: SharedNetwork
    ) -> SharedNetwork:
        return shared_network_model

    @case(tags="model")
    def case_private_network_model(
        self, private_network_model: PrivateNetwork
    ) -> PrivateNetwork:
        return private_network_model
