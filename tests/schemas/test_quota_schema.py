from typing import Literal

from pytest_cases import parametrize, parametrize_with_cases

from fed_reg.quota.schemas import QuotaBase
from tests.utils import random_lower_string


class CaseAttr:
    def case_none(self) -> tuple[None, None]:
        return None, None

    def case_desc(self) -> tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @parametrize(value=(True, False))
    def case_boolean(self, value: bool) -> tuple[Literal["per_user"], bool]:
        return "per_user", value

    @parametrize(value=(True, False))
    def case_usage(self, value: bool) -> tuple[Literal["usage"], bool]:
        return "usage", value


@parametrize_with_cases("key, value", cases=CaseAttr)
def test_base_public(key: str, value: str) -> None:
    d = {key: value} if key else {}
    item = QuotaBase(**d)
    assert item.description == d.get("description", "")
    assert item.per_user == d.get("per_user", False)
    assert item.usage == d.get("usage", False)
