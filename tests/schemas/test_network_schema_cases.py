from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.network.schemas import (
    NetworkBase,
    PrivateNetworkCreate,
    SharedNetworkCreate,
)
from tests.schemas.utils import network_schema_dict
from tests.utils import random_lower_string, random_positive_int


class CaseNetworkSchema:
    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return network_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**network_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_is_router_external(self) -> dict[str, Any]:
        return {**network_schema_dict(), "is_router_external": True}

    @case(tags=("dict", "valid", "base", "update"))
    def case_is_default(self) -> dict[str, Any]:
        return {**network_schema_dict(), "is_default": True}

    @case(tags=("dict", "valid", "base", "update"))
    def case_mtu(self) -> dict[str, Any]:
        return {**network_schema_dict(), "mtu": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_proxy_host(self) -> dict[str, Any]:
        return {**network_schema_dict(), "proxy_host": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_proxy_user(self) -> dict[str, Any]:
        return {**network_schema_dict(), "proxy_user": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_tags(self) -> dict[str, Any]:
        return {**network_schema_dict(), "tags": [random_lower_string()]}

    @case(tags=("dict", "valid"))
    def case_is_shared(self) -> dict[str, Any]:
        return {**network_schema_dict(), "is_shared": True}

    @case(tags=("dict", "valid"))
    def case_is_private(self) -> dict[str, Any]:
        return {**network_schema_dict(), "is_shared": False}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = network_schema_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_uuid(self) -> tuple[dict[str, Any], Literal["uuid"]]:
        d = network_schema_dict()
        d.pop("uuid")
        return d, "uuid"

    @case(tags=("dict", "invalid", "base", "update"))
    def case_invalid_mtu(self) -> tuple[dict[str, Any], Literal["mtu"]]:
        d = network_schema_dict()
        d["mtu"] = -1
        return d, "mtu"

    @case(tags="class")
    def case_base_class(self) -> type[NetworkBase]:
        return NetworkBase

    @case(tags="class")
    def case_private_class(self) -> type[PrivateNetworkCreate]:
        return PrivateNetworkCreate

    @case(tags="class")
    def case_shared_class(self) -> type[SharedNetworkCreate]:
        return SharedNetworkCreate


class CaseNetworkModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseNetworkSchema, has_tag=("dict", "valid", "base")
    )
    def case_network_model(self, data: dict[str, Any]) -> Network:
        return Network(**NetworkBase(**data).dict()).save()

    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseNetworkSchema, has_tag=("dict", "valid", "base")
    )
    def case_private_network_class(self, data: dict[str, Any]) -> PrivateNetwork:
        return PrivateNetwork(**PrivateNetworkCreate(**data).dict()).save()

    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseNetworkSchema, has_tag=("dict", "valid", "base")
    )
    def case_shared_network_class(self, data: dict[str, Any]) -> SharedNetwork:
        return SharedNetwork(**SharedNetworkCreate(**data).dict()).save()
