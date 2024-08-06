from pytest_cases import case, parametrize

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.network.schemas import (
    NetworkBase,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)


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
    @parametrize(value=("mtu",))
    def case_optional(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[NetworkBase]:
        return NetworkBase

    @case(tags="class")
    def case_private_class(self) -> type[PrivateNetworkCreate]:
        return PrivateNetworkCreate

    @case(tags="class")
    def case_shared_class(self) -> type[SharedNetworkCreate]:
        return SharedNetworkCreate


class CaseModel:
    @case(tags="model")
    def case_private_network(self) -> type[PrivateNetwork]:
        return PrivateNetwork

    @case(tags="model")
    def case_shared_network(self) -> type[SharedNetwork]:
        return SharedNetwork

    @case(tags="model")
    def case_network(self) -> type[Network]:
        return Network
