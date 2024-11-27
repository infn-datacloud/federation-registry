from typing import Any, Literal

from pytest_cases import case

from tests.models.utils import user_group_model_dict
from tests.utils import random_lower_string


class CaseUserGroupModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return user_group_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {**user_group_model_dict(), "description": random_lower_string()}

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = user_group_model_dict()
        d.pop("name")
        return d, "name"
