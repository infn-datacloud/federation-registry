from typing import Literal
from uuid import uuid4

from pytest_cases import case, parametrize

from fed_reg.provider.schemas_extended import (
    ComputeQuotaCreateExtended,
    PrivateFlavorCreateExtended,
    PrivateImageCreateExtended,
    SharedFlavorCreateExtended,
    SharedImageCreateExtended,
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
    @parametrize(value=(i for i in ServiceType if i != ServiceType.COMPUTE))
    def case_type(self, value: ServiceType) -> tuple[Literal["type"], ServiceType]:
        return "type", value

    @case(tags=["create_extended"])
    def case_dup_quotas(
        self, compute_quota_create_ext_schema: ComputeQuotaCreateExtended
    ) -> tuple[Literal["quotas"], list[ComputeQuotaCreateExtended], str]:
        return (
            "quotas",
            [compute_quota_create_ext_schema, compute_quota_create_ext_schema],
            "Multiple quotas on same project",
        )

    @case(tags=["create_extended"])
    @parametrize(attr=("name", "uuid"))
    @parametrize(res=("flavors", "images"))
    def case_dup_res(
        self,
        shared_flavor_create_ext_schema: PrivateFlavorCreateExtended
        | SharedFlavorCreateExtended,
        shared_image_create_ext_schema: PrivateImageCreateExtended
        | SharedImageCreateExtended,
        attr: str,
        res: str,
    ) -> tuple[
        str,
        list[PrivateFlavorCreateExtended | SharedFlavorCreateExtended]
        | list[PrivateImageCreateExtended | SharedImageCreateExtended],
        str,
    ]:
        item = (
            shared_flavor_create_ext_schema
            if res == "flavors"
            else shared_image_create_ext_schema
        )
        item2 = item.copy()
        if attr == "name":
            item2.uuid = uuid4()
        else:
            item2.name = random_lower_string()
        return (
            res,
            [item, item2],
            f"There are multiple items with identical {attr}",
        )
