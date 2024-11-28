from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import SLABase, SLACreate
from tests.schemas.utils import sla_schema_dict
from tests.utils import random_lower_string


class CaseSLASchema:
    @case(tags=("dict", "valid", "base_public", "update"))
    def case_mandatory_public(self) -> dict[str, Any]:
        d = sla_schema_dict()
        d.pop("start_date")
        d.pop("end_date")
        return d

    @case(tags=("dict", "valid", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return sla_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**sla_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_doc_uuid(self) -> tuple[dict[str, Any], Literal["doc_uuid"]]:
        d = sla_schema_dict()
        d.pop("doc_uuid")
        return d, "doc_uuid"

    @case(tags=("dict", "invalid", "base", "read"))
    def case_missing_start_date(self) -> tuple[dict[str, Any], Literal["start_date"]]:
        d = sla_schema_dict()
        d.pop("start_date")
        return d, "start_date"

    @case(tags=("dict", "invalid", "base", "read"))
    def case_missing_end_date(self) -> tuple[dict[str, Any], Literal["end_date"]]:
        d = sla_schema_dict()
        d.pop("end_date")
        return d, "end_date"

    @case(tags=("dict", "invalid", "base", "read"))
    def case_invalid_date_combination(
        self,
    ) -> tuple[dict[str, Any], Literal["end_date"]]:
        d = sla_schema_dict()
        tmp = d.get("end_date")
        d["end_date"] = d["start_date"]
        d["start_date"] = tmp
        return d, "end_date"

    @case(tags="class")
    def case_base_class(self) -> type[SLABase]:
        return SLABase

    @case(tags="class")
    def case_create_class(self) -> type[SLACreate]:
        return SLACreate


class CaseSLAModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseSLASchema, has_tag=("dict", "valid", "base")
    )
    def case_sla_model(self, data: dict[str, Any]) -> SLA:
        return SLA(**SLABase(**data).dict()).save()
