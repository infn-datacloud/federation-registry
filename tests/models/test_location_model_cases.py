from typing import Any

from pytest_cases import case

from tests.utils import random_float, random_lower_string


class CaseLocationDictAttr:
    @case(tags=("dict", "valid", "mandatory"))
    def case_mandatory(self) -> dict[str, Any]:
        return {"site": random_lower_string(), "country": random_lower_string()}

    @case(tags=("dict", "valid"))
    def case_description(self) -> dict[str, Any]:
        return {
            "site": random_lower_string(),
            "country": random_lower_string(),
            "description": random_lower_string(),
        }

    @case(tags=("dict", "valid"))
    def case_latitude(self) -> dict[str, Any]:
        return {
            "site": random_lower_string(),
            "country": random_lower_string(),
            "latitude": random_float(),
        }

    @case(tags=("dict", "valid"))
    def case_longitude(self) -> dict[str, Any]:
        return {
            "site": random_lower_string(),
            "country": random_lower_string(),
            "longitude": random_float(),
        }

    @case(tags=("dict", "invalid"))
    def case_missing_site(self) -> dict[str, Any]:
        return {"country": random_lower_string()}

    @case(tags=("dict", "invalid"))
    def case_missing_country(self) -> dict[str, Any]:
        return {"site": random_lower_string()}
