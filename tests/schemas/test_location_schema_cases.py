from pytest_cases import case, parametrize

from fed_reg.location.models import Location
from fed_reg.location.schemas import LocationBase, LocationCreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("site", "country"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base", "update"))
    @parametrize(value=("latitude", "longitude"))
    def case_optional(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("site", "country"))
    def case_missing_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "read_public", "read"))
    @parametrize(value=("uid",))
    def case_missing_uid(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("not_a_country",))
    def case_invalid_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "update", "read"))
    @parametrize(
        value=(
            "under_min_latitude",
            "under_min_longitude",
            "over_max_latitude",
            "over_max_longitude",
        )
    )
    def case_optional(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[LocationBase]:
        return LocationBase

    @case(tags="class")
    def case_create_class(self) -> type[LocationCreate]:
        return LocationCreate


class CaseModel:
    @case(tags="model")
    def case_location(self) -> type[Location]:
        return Location
