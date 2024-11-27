from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.location.models import Location
from fed_reg.location.schemas import LocationBase, LocationCreate
from tests.schemas.utils import location_schema_dict, random_latitude, random_longitude
from tests.utils import random_lower_string


class CaseLocationSchema:
    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return location_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**location_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_latitude(self) -> dict[str, Any]:
        return {**location_schema_dict(), "latitude": random_latitude()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_longitude(self) -> dict[str, Any]:
        return {**location_schema_dict(), "longitude": random_longitude()}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_site(self) -> tuple[dict[str, Any], Literal["site"]]:
        d = location_schema_dict()
        d.pop("site")
        return d, "site"

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_country(self) -> tuple[dict[str, Any], Literal["country"]]:
        d = location_schema_dict()
        d.pop("country")
        return d, "country"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_country(self) -> tuple[dict[str, Any], Literal["country"]]:
        d = location_schema_dict()
        d["country"] = random_lower_string()
        return d, "country"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_under_min_latitude(self) -> tuple[dict[str, Any], Literal["latitude"]]:
        d = location_schema_dict()
        d["latitude"] = -91
        return d, "latitude"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_over_max_latitude(self) -> tuple[dict[str, Any], Literal["latitude"]]:
        d = location_schema_dict()
        d["latitude"] = 91
        return d, "latitude"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_under_min_longitude(self) -> tuple[dict[str, Any], Literal["longitude"]]:
        d = location_schema_dict()
        d["longitude"] = -181
        return d, "longitude"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_over_max_longitude(self) -> tuple[dict[str, Any], Literal["longitude"]]:
        d = location_schema_dict()
        d["longitude"] = 181
        return d, "longitude"

    @case(tags="class")
    def case_base_class(self) -> type[LocationBase]:
        return LocationBase

    @case(tags="class")
    def case_create_class(self) -> type[LocationCreate]:
        return LocationCreate


class CaseLocationModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseLocationSchema, has_tag=("dict", "valid", "base")
    )
    def case_location_model(self, data: dict[str, Any]) -> Location:
        return Location(**LocationBase(**data).dict()).save()
