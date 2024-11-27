from typing import Any, Literal

from pytest_cases import case

from tests.models.utils import provider_model_dict
from tests.utils import random_lower_string


class CaseProviderModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return provider_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            **provider_model_dict(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_status(self) -> dict[str, Any]:
        return {
            **provider_model_dict(),
            "status": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_is_public(self) -> dict[str, Any]:
        return {
            **provider_model_dict(),
            "is_public": True,
        }

    @case(tags=("dict", "valid"))
    def case_support_emails(self) -> dict[str, Any]:
        return {
            **provider_model_dict(),
            "support_emails": [random_lower_string()],
        }

    @case(tags=("dict", "invalid"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = provider_model_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid"))
    def case_missing_type(self) -> tuple[dict[str, Any], Literal["type"]]:
        d = provider_model_dict()
        d.pop("type")
        return d, "type"
