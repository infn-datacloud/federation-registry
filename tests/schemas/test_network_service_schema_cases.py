from typing import Literal
from uuid import uuid4

from pytest_cases import case, parametrize

from fed_reg.provider.schemas_extended import (
    NetworkQuotaCreateExtended,
    PrivateNetworkCreateExtended,
    SharedNetworkCreateExtended,
)
from fed_reg.service.enum import NetworkServiceName
from tests.schemas.utils import network_schema_dict
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags=["base_public", "base", "update"])
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags=["update"])
    @parametrize(attr=["endpoint", "name"])
    def case_attr_is_none(self, attr: str) -> tuple[str, None]:
        return attr, None

    @case(tags=["base_public", "base"])
    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @case(tags=["base"])
    @parametrize(value=[i for i in NetworkServiceName])
    def case_name(self, value: int) -> tuple[Literal["name"], int]:
        return "name", value

    @case(tags=["create_extended"])
    @parametrize(len=[0, 1, 2, 3])
    def case_quotas(
        self, network_quota_create_ext_schema: NetworkQuotaCreateExtended, len: int
    ) -> tuple[Literal["quotas"], list[NetworkQuotaCreateExtended]]:
        if len == 1:
            return "quotas", [network_quota_create_ext_schema]
        elif len == 2:
            return "quotas", [
                network_quota_create_ext_schema,
                NetworkQuotaCreateExtended(project=uuid4()),
            ]
        elif len == 3:
            # Same project, different users scope
            quota2 = network_quota_create_ext_schema.copy()
            quota2.per_user = not quota2.per_user
            return "quotas", [network_quota_create_ext_schema, quota2]
        else:
            return "quotas", []

    @case(tags=["create_extended"])
    @parametrize(len=[0, 1, 2])
    def case_networks(
        self,
        shared_network_create_ext_schema: PrivateNetworkCreateExtended
        | SharedNetworkCreateExtended,
        len: int,
    ) -> tuple[
        Literal["networks"],
        list[PrivateNetworkCreateExtended | SharedNetworkCreateExtended],
    ]:
        if len == 1:
            return "networks", [shared_network_create_ext_schema]
        elif len == 2:
            return "networks", [
                shared_network_create_ext_schema,
                SharedNetworkCreateExtended(**network_schema_dict()),
            ]
        else:
            return "networks", []
