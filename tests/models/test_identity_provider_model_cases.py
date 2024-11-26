from typing import Any

from pytest_cases import case

from tests.utils import random_lower_string


class CaseIdentityProviderDict:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return {"endpoint": random_lower_string(), "group_claim": random_lower_string()}

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            "endpoint": random_lower_string(),
            "group_claim": random_lower_string(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_endpoint(self) -> dict[str, Any]:
        return {"group_claim": random_lower_string()}

    @case(tags=("dict", "invalid"))
    def case_missing_group_claim(self) -> dict[str, Any]:
        return {"endpoint": random_lower_string()}
