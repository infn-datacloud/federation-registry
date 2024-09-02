import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.query import (
    DbQueryCommonParams,
    SchemaSize,
    create_query_model,
)
from tests.generics.utils import (
    TestModelBool,
    TestModelDate,
    TestModelDateTime,
    TestModelEnum,
    TestModelFloat,
    TestModelInt,
    TestModelStr,
    db_query_schema_dict,
    schema_size_schema_dict,
)
from tests.utils import random_lower_string


class CaseModel:
    @case(tags="str")
    def case_model_str(self) -> type[TestModelStr]:
        return TestModelStr

    @case(tags="str")
    def case_model_enum(self) -> type[TestModelEnum]:
        return TestModelEnum

    @case(tags="number")
    def case_model_int(self) -> type[TestModelInt]:
        return TestModelInt

    @case(tags="number")
    def case_model_float(self) -> type[TestModelFloat]:
        return TestModelFloat

    @case(tags="date")
    def case_model_date(self) -> type[TestModelDate]:
        return TestModelDate

    @case(tags="date")
    def case_model_datetime(self) -> type[TestModelDateTime]:
        return TestModelDateTime


class CaseAttr:
    @case(tags=("attr", "invalid_attr", "schema_size"))
    @parametrize(value=["short", "with_conn"])
    def case_schema_size(self, value: str) -> str:
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


@parametrize_with_cases("attr", cases=CaseAttr, has_tag=("attr", "schema_size"))
def test_valid_schema(attr: str) -> None:
    d = schema_size_schema_dict(attr)
    item = SchemaSize(**d)
    assert item.short == d.get("short", False)
    assert item.with_conn == d.get("with_conn", False)


@parametrize_with_cases("attr", cases=CaseAttr, has_tag=("invalid_attr", "schema_size"))
def test_invalid_schema(attr: str) -> None:
    with pytest.raises(ValueError):
        SchemaSize(**schema_size_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", cases=CaseAttr, has_tag=("attr", "db_query"))
def test_valid_db_params(attr: str) -> None:
    d = db_query_schema_dict(attr)
    item = DbQueryCommonParams(**d)
    assert item.skip == d.get("skip", 0)
    assert item.limit == d.get("limit", None)
    assert item.sort == d.get("sort", None)


@parametrize_with_cases("input, output", cases=CaseAttr, has_tag=("attr", "sort"))
def test_parse_sort(input: str, output: str) -> None:
    item = DbQueryCommonParams(sort=input)
    assert item.sort is not None
    assert item.sort == output


@parametrize_with_cases("attr", cases=CaseAttr, has_tag=("invalid_attr", "db_query"))
def test_invalid_db_params(attr: str) -> None:
    with pytest.raises(ValueError):
        DbQueryCommonParams(**db_query_schema_dict(attr, valid=False))


def test_bool() -> None:
    cls = create_query_model(random_lower_string(), TestModelBool)
    item = cls()
    assert item.test_field is None


@parametrize_with_cases("model", cases=CaseModel, has_tag="number")
def test_numbers(model: type[TestModelInt] | type[TestModelFloat]) -> None:
    cls = create_query_model(random_lower_string(), model)
    item = cls()
    assert item.test_field is None
    assert item.test_field__lt is None
    assert item.test_field__gt is None
    assert item.test_field__lte is None
    assert item.test_field__gte is None
    assert item.test_field__ne is None


@parametrize_with_cases("model", cases=CaseModel, has_tag="date")
def test_dates(model: type[TestModelDate] | type[TestModelDateTime]) -> None:
    cls = create_query_model(random_lower_string(), model)
    item = cls()
    assert item.test_field__lt is None
    assert item.test_field__gt is None
    assert item.test_field__lte is None
    assert item.test_field__gte is None
    assert item.test_field__ne is None


@parametrize_with_cases("model", cases=CaseModel, has_tag="str")
def test_str_enum(model: type[TestModelStr] | type[TestModelEnum]) -> None:
    cls = create_query_model(random_lower_string(), model)
    item = cls()
    assert item.test_field is None
    assert item.test_field__contains is None
    assert item.test_field__icontains is None
    assert item.test_field__startswith is None
    assert item.test_field__istartswith is None
    assert item.test_field__endswith is None
    assert item.test_field__iendswith is None
    assert item.test_field__regex is None
    assert item.test_field__iregex is None


# TODO test lists
# TODO test get_origin(v.type_)
# TODO test else case
