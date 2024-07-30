from random import randint
from typing import Literal, Optional

from pytest_cases import case, parametrize

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
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
    @parametrize(attr=("mtu"))
    def case_integer(self, attr: str) -> tuple[str, int]:
        return attr, randint(0, 100)

    @case(tags=["base"])
    @parametrize(value=(True, False))
    @parametrize(attr=["is_router_external", "is_default"])
    def case_boolean(self, attr: str, value: bool) -> tuple[str, bool]:
        return attr, value

    @case(tags=["base"])
    @parametrize(attr=("proxy_host", "proxy_user"))
    def case_string(self, attr: str) -> tuple[str, str]:
        return attr, random_lower_string()

    @case(tags=["base"])
    @parametrize(len=(0, 1, 2))
    def case_tag_list(self, len: int) -> tuple[Literal["tags"], Optional[list[str]]]:
        return "tags", [random_lower_string() for _ in range(len)]

    @case(tags=["model"])
    def case_private_model(self, private_network_model: PrivateNetwork):
        return private_network_model

    @case(tags=["model"])
    def case_shared_model(self, shared_network_model: SharedNetwork):
        return shared_network_model

    @case(tags=["model"])
    def case_model(self, network_model: Network):
        return network_model
