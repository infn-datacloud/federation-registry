from typing import Literal
from uuid import uuid4

from pytest_cases import case, parametrize

from fed_reg.provider.schemas_extended import BlockStorageQuotaCreateExtended
from fed_reg.service.enum import BlockStorageServiceName
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
    @parametrize(value=(i for i in BlockStorageServiceName))
    def case_name(self, value: int) -> tuple[Literal["name"], int]:
        return "name", value

    @case(tags=["create_extended"])
    @parametrize(len=(0, 1, 2, 3))
    def case_quotas(
        self,
        block_storage_quota_create_ext_schema: BlockStorageQuotaCreateExtended,
        len: int,
    ) -> list[BlockStorageQuotaCreateExtended]:
        if len == 1:
            return [block_storage_quota_create_ext_schema]
        elif len == 2:
            return [
                block_storage_quota_create_ext_schema,
                BlockStorageQuotaCreateExtended(project=uuid4()),
            ]
        elif len == 3:
            # Same project, different users scope
            quota2 = block_storage_quota_create_ext_schema.copy()
            quota2.per_user = not quota2.per_user
            return [block_storage_quota_create_ext_schema, quota2]
        else:
            return []
