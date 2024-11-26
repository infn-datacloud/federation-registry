from typing import Any
from uuid import uuid4

from pytest_cases import case

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from tests.utils import random_int, random_lower_string


class CaseNetworkDict:
    @case(tags=("attr", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return {"name": random_lower_string(), "uuid": uuid4().hex}

    @case(tags=("attr", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "description": random_lower_string(),
        }

    @case(tags=("attr", "valid"))
    def case_is_router_external(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "is_router_external": True,
        }

    @case(tags=("attr", "valid"))
    def case_is_default(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "is_default": True,
        }

    @case(tags=("attr", "valid"))
    def case_mtu(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "mtu": random_int(),
        }

    @case(tags=("attr", "valid"))
    def case_proxy_host(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "proxy_host": random_lower_string(),
        }

    @case(tags=("attr", "valid"))
    def case_proxy_user(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "proxy_user": random_lower_string(),
        }

    @case(tags=("attr", "valid"))
    def case_tags(self) -> dict[str, Any]:
        return {
            "name": random_lower_string(),
            "uuid": uuid4().hex,
            "tags": [random_lower_string()],
        }

    @case(tags=("attr", "invalid"))
    def case_missing_name(self) -> dict[str, Any]:
        return {"uuid": uuid4().hex}

    @case(tags=("attr", "invalid"))
    def case_missing_uuid(self) -> dict[str, Any]:
        return {"name": random_lower_string()}


class CaseNetworkModelClass:
    @case(tags="class")
    def case_network(self) -> type[Network]:
        return Network

    @case(tags=("class", "derived"))
    def case_private_network(self) -> type[PrivateNetwork]:
        return PrivateNetwork

    @case(tags=("class", "derived"))
    def case_shared_network(self) -> type[SharedNetwork]:
        return SharedNetwork


class CasenetworkModel:
    @case(tags="model")
    def case_network_model(self, network_model: Network) -> Network:
        return network_model

    @case(tags=("model", "private"))
    def case_private_network_model(
        self, private_network_model: PrivateNetwork
    ) -> PrivateNetwork:
        return private_network_model

    @case(tags=("model", "shared"))
    def case_shared_network_model(
        self, shared_network_model: SharedNetwork
    ) -> SharedNetwork:
        return shared_network_model
