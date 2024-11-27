from typing import Any, Literal

from pytest_cases import case

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from tests.models.utils import network_model_dict
from tests.utils import random_int, random_lower_string


class CaseNetworkModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return network_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_is_router_external(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "is_router_external": True,
        }

    @case(tags=("dict", "valid"))
    def case_is_default(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "is_default": True,
        }

    @case(tags=("dict", "valid"))
    def case_mtu(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "mtu": random_int(),
        }

    @case(tags=("dict", "valid"))
    def case_proxy_host(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "proxy_host": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_proxy_user(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "proxy_user": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_tags(self) -> dict[str, Any]:
        return {
            **network_model_dict(),
            "tags": [random_lower_string()],
        }

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = network_model_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid"))
    def case_missing_uuid(self) -> tuple[dict[str, Any], Literal["uuid"]]:
        d = network_model_dict()
        d.pop("uuid")
        return d, "uuid"

    @case(tags="class")
    def case_network(self) -> type[Network]:
        return Network

    @case(tags=("class", "derived"))
    def case_private_network(self) -> type[PrivateNetwork]:
        return PrivateNetwork

    @case(tags=("class", "derived"))
    def case_shared_network(self) -> type[SharedNetwork]:
        return SharedNetwork

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
