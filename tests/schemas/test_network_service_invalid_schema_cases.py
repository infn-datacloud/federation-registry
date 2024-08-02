from typing import Literal

from pytest_cases import case, parametrize

from fed_reg.provider.schemas_extended import (
    NetworkQuotaCreateExtended,
    PrivateNetworkCreateExtended,
    SharedNetworkCreateExtended,
)
from fed_reg.service.enum import ServiceType
from tests.utils import random_lower_string


class CaseInvalidAttr:
    @case(tags=["base"])
    @parametrize(attr=("endpoint", "name"))
    def case_none(self, attr: str) -> tuple[str, None]:
        return attr, None

    @case(tags=["base"])
    def case_endpoint(self) -> tuple[Literal["endpoint"], None]:
        return "endpoint", random_lower_string()

    @case(tags=["base"])
    @parametrize(value=(i for i in ServiceType if i != ServiceType.NETWORK))
    def case_type(self, value: ServiceType) -> tuple[Literal["type"], ServiceType]:
        return "type", value

    @case(tags=["create_extended"])
    def case_dup_quotas(
        self, network_quota_create_ext_schema: NetworkQuotaCreateExtended
    ) -> tuple[Literal["quotas"], list[NetworkQuotaCreateExtended], str]:
        return (
            "quotas",
            [network_quota_create_ext_schema, network_quota_create_ext_schema],
            "Multiple quotas on same project",
        )

    @case(tags=["create_extended"])
    def case_dup_networks(
        self,
        shared_network_create_ext_schema: PrivateNetworkCreateExtended
        | SharedNetworkCreateExtended,
    ) -> tuple[
        Literal["networks"],
        list[PrivateNetworkCreateExtended | SharedNetworkCreateExtended],
        str,
    ]:
        return (
            "networks",
            [shared_network_create_ext_schema, shared_network_create_ext_schema],
            "There are multiple items with identical uuid",
        )
