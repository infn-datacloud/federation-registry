from typing import Literal, Optional

import pytest
from pytest_cases import parametrize, parametrize_with_cases

from fed_reg.service.schemas import ServiceBase
from tests.schemas.utils import service_schema_dict
from tests.utils import random_lower_string


class CaseAttr:
    def case_none(self) -> tuple[None, None]:
        return None, None

    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()


class CaseInvalidAttr:
    @parametrize(value=(None, random_lower_string()))
    def case_endpoint(
        self, value: Optional[str]
    ) -> tuple[Literal["endpoint"], Optional[str]]:
        return "endpoint", value


@parametrize_with_cases("key, value", cases=CaseAttr)
def test_base_public(key: str, value: str) -> None:
    d = service_schema_dict()
    if key:
        d[key] = value
    item = ServiceBase(**d)
    assert item.description == d.get("description", "")
    assert item.endpoint == d.get("endpoint", False)


@parametrize_with_cases("key, value", cases=CaseInvalidAttr)
def test_invalid_base_public(key: str, value: Optional[str]) -> None:
    d = service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        ServiceBase(**d)
