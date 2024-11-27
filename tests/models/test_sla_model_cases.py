from typing import Any, Literal

from pytest_cases import case

from tests.models.utils import sla_model_dict
from tests.utils import random_lower_string


class CaseSLAModel:
    @case(tags=("dict", "valid"))
    def case_mandatory(self) -> dict[str, Any]:
        return sla_model_dict()

    @case(tags=("attr", "optional"))
    def case_description(self) -> dict[str, Any]:
        return {**sla_model_dict(), "description": random_lower_string()}

    @case(tags=("dict", "invalid"))
    def case_missing_doc_uuid(self) -> tuple[dict[str, Any], Literal["doc_uuid"]]:
        d = sla_model_dict()
        d.pop("doc_uuid")
        return d, "doc_uuid"

    @case(tags=("dict", "invalid"))
    def case_missing_start_date(self) -> tuple[dict[str, Any], Literal["start_date"]]:
        d = sla_model_dict()
        d.pop("start_date")
        return d, "start_date"

    @case(tags=("dict", "invalid"))
    def case_missing_end_date(self) -> tuple[dict[str, Any], Literal["end_date"]]:
        d = sla_model_dict()
        d.pop("end_date")
        return d, "end_date"
