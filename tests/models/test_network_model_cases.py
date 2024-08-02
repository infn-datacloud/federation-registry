from pytest_cases import case, parametrize

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(
        value=(
            "description",
            "is_router_external",
            "is_default",
            "mtu",
            "proxy_host",
            "proxy_user",
            "tags",
        )
    )
    def case_optional(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_network(self) -> type[Network]:
        return Network

    @case(tags=("class", "derived"))
    def case_private_network(self) -> type[PrivateNetwork]:
        return PrivateNetwork

    @case(tags=("class", "derived"))
    def case_shared_network(self) -> type[SharedNetwork]:
        return SharedNetwork


class CaseModel:
    @case(tags="model")
    def case_network_model(self, network_model: Network) -> Network:
        return network_model

    @case(tags="model")
    def case_private_network_model(
        self, private_network_model: PrivateNetwork
    ) -> PrivateNetwork:
        return private_network_model

    @case(tags="model")
    def case_shared_network_model(
        self, shared_network_model: SharedNetwork
    ) -> SharedNetwork:
        return shared_network_model
