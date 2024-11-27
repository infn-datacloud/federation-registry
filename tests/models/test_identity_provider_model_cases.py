from typing import Any, Literal

from pytest_cases import case

from tests.models.utils import identity_provider_model_dict
from tests.utils import random_lower_string


class CaseIdentityProviderModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return identity_provider_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            **identity_provider_model_dict(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_endpoint(self) -> tuple[dict[str, Any], Literal["endpoint"]]:
        d = identity_provider_model_dict()
        d.pop("endpoint")
        return d, "endpoint"

    @case(tags=("dict", "invalid"))
    def case_missing_group_claim(self) -> tuple[dict[str, Any], Literal["group_claim"]]:
        d = identity_provider_model_dict()
        d.pop("group_claim")
        return d, "group_claim"
