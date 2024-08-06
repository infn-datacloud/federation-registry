from pytest_cases import case, parametrize

from tests.schemas.utils import (
    TestModelDate,
    TestModelDateTime,
    TestModelEnum,
    TestModelFloat,
    TestModelInt,
    TestModelStr,
)


class CaseModel:
    @case(tags=("model", "str"))
    def case_model_str(self) -> type[TestModelStr]:
        return TestModelStr

    @case(tags=("model", "str"))
    def case_model_enum(self) -> type[TestModelEnum]:
        return TestModelEnum

    @case(tags=("model", "number"))
    def case_model_int(self) -> type[TestModelInt]:
        return TestModelInt

    @case(tags=("model", "number"))
    def case_model_float(self) -> type[TestModelFloat]:
        return TestModelFloat

    @case(tags=("model", "date"))
    def case_model_date(self) -> type[TestModelDate]:
        return TestModelDate

    @case(tags=("model", "date"))
    def case_model_datetime(self) -> type[TestModelDateTime]:
        return TestModelDateTime


class CaseAttr:
    @case(tags=("attr", "invalid_attr", "schema_size"))
    @parametrize(value=["short", "with_conn"])
    def case_schema_size(self, value: str) -> str:
        return value

    @case(tags=("attr", "pagination"))
    @parametrize(value=["page", "size"])
    def case_valid_pagination(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "pagination"))
    @parametrize(value=["page", "size_0", "negative_size"])
    def case_invalid_pagination(self, value: str) -> str:
        return value

    @case(tags=("attr", "db_query"))
    @parametrize(value=["limit", "skip", "sort"])
    def case_valid_db_query(self, value: str) -> str:
        return value

    @case(tags=("attr", "sort"))
    @parametrize(value=["test", "test_asc"])
    def case_sort_asc(self, value: str) -> tuple[str]:
        return value, "test"

    @case(tags=("attr", "sort"))
    @parametrize(value=["test_desc", "-test", "-test_desc"])
    def case_sort_desc(self, value: str) -> tuple[str]:
        return value, "-test"

    @case(tags=("invalid_attr", "db_query"))
    @parametrize(value=("limit", "skip"))
    def case_invalid_db_query(self, value: str) -> str:
        return value
