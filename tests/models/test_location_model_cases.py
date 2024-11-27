from typing import Any, Literal

from pytest_cases import case

from tests.models.utils import location_model_dict
from tests.utils import random_float, random_lower_string


class CaseLocationModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return location_model_dict()

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            **location_model_dict(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_latitude(self) -> dict[str, Any]:
        return {
            **location_model_dict(),
            "latitude": random_float(),
        }

    @case(tags=("dict", "valid"))
    def case_longitude(self) -> dict[str, Any]:
        return {
            **location_model_dict(),
            "longitude": random_float(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_site(self) -> tuple[dict[str, Any], Literal["site"]]:
        d = location_model_dict()
        d.pop("site")
        return d, "site"

    @case(tags=("dict", "invalid"))
    def case_missing_country(self) -> tuple[dict[str, Any], Literal["country"]]:
        d = location_model_dict()
        d.pop("country")
        return d, "country"
