from pytest_cases import case, parametrize

from fed_reg.region.models import Region
from fed_reg.region.schemas import RegionBase, RegionCreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("name",))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("name",))
    def case_missing_mandatory(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[RegionBase]:
        return RegionBase

    @case(tags="class")
    def case_create_class(self) -> type[RegionCreate]:
        return RegionCreate


class CaseModel:
    @case(tags="model")
    def case_region(self) -> type[Region]:
        return Region
