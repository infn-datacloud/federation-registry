from pytest_cases import case

from tests.utils import random_lower_string


class CaseIdentityProviderDict:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> str:
        return {"endpoint": random_lower_string(), "group_claim": random_lower_string()}

    @case(tags=("dict", "valid"))
    def case_optional(self) -> str:
        return {
            "endpoint": random_lower_string(),
            "group_claim": random_lower_string(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_endpoint(self) -> str:
        return {"group_claim": random_lower_string()}

    @case(tags=("dict", "invalid"))
    def case_missing_group_claim(self) -> str:
        return {"endpoint": random_lower_string()}
