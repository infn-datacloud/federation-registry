from pytest_cases import case, parametrize


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("endpoint", "group_claim"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(value=("description",))
    def case_optional(self, value: str) -> str:
        return value
