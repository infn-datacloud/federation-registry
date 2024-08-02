from pytest_cases import case, parametrize


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name", "type"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(value=("description", "status", "is_public", "support_emails"))
    def case_optional(self, value: str) -> str:
        return value
