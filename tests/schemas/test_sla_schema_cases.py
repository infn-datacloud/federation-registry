from pytest_cases import case, parametrize

from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import SLABase, SLACreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("doc_uuid",))
    def case_mandatory_public(self, value: str) -> str:
        return value

    @case(tags=("attr", "mandatory", "base", "update"))
    @parametrize(value=("start_date", "end_date"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("doc_uuid",))
    def case_missing_mandatory_public(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "read"))
    @parametrize(value=("start_date", "end_date"))
    def case_missing_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "read"))
    @parametrize(value=("inverted_dates",))
    def case_invalid_combination(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[SLABase]:
        return SLABase

    @case(tags="class")
    def case_create_class(self) -> type[SLACreate]:
        return SLACreate


class CaseModel:
    @case(tags="model")
    def case_sla(self) -> type[SLA]:
        return SLA
