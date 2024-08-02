from typing import Literal
from uuid import uuid4

from pytest_cases import case, parametrize

from fed_reg.provider.schemas_extended import (
    ComputeQuotaCreateExtended,
    ImageCreateExtended,
    PrivateFlavorCreateExtended,
    SharedFlavorCreateExtended,
)
from fed_reg.service.enum import ComputeServiceName
from tests.create_dict import flavor_schema_dict, image_schema_dict
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags=["base_public", "base", "update"])
    def case_none(self) -> tuple[None, None]:
        return None, None

    @case(tags=["update"])
    @parametrize(attr=("endpoint", "name"))
    def case_attr_is_none(self, attr: str) -> tuple[str, None]:
        return attr, None

    @case(tags=["base_public", "base"])
    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @case(tags=["base"])
    @parametrize(value=[i for i in ComputeServiceName])
    def case_name(self, value: int) -> tuple[Literal["name"], int]:
        return "name", value

    @case(tags=["create_extended"])
    @parametrize(len=(0, 1, 2, 3))
    def case_quotas(
        self, compute_quota_create_ext_schema: ComputeQuotaCreateExtended, len: int
    ) -> tuple[Literal["quotas"], list[ComputeQuotaCreateExtended]]:
        if len == 1:
            return "quotas", [compute_quota_create_ext_schema]
        elif len == 2:
            return "quotas", [
                compute_quota_create_ext_schema,
                ComputeQuotaCreateExtended(project=uuid4()),
            ]
        elif len == 3:
            # Same project, different users scope
            quota2 = compute_quota_create_ext_schema.copy()
            quota2.per_user = not quota2.per_user
            return "quotas", [compute_quota_create_ext_schema, quota2]
        else:
            return "quotas", []

    @case(tags=["create_extended"])
    @parametrize(len=(0, 1, 2))
    def case_flavors(
        self,
        flavor_create_ext_schema: PrivateFlavorCreateExtended
        | SharedFlavorCreateExtended,
        len: int,
    ) -> tuple[
        Literal["flavors"],
        list[PrivateFlavorCreateExtended | SharedFlavorCreateExtended],
    ]:
        if len == 1:
            return "flavors", [flavor_create_ext_schema]
        elif len == 2:
            return "flavors", [
                flavor_create_ext_schema,
                SharedFlavorCreateExtended(**flavor_schema_dict()),
            ]
        else:
            return "flavors", []

    @case(tags=["create_extended"])
    @parametrize(len=(0, 1, 2))
    def case_images(
        self, image_create_ext_schema: ImageCreateExtended, len: int
    ) -> tuple[Literal["images"], list[ImageCreateExtended]]:
        if len == 1:
            return "images", [image_create_ext_schema]
        elif len == 2:
            return "images", [
                image_create_ext_schema,
                ImageCreateExtended(**image_schema_dict()),
            ]
        else:
            return "images", []
