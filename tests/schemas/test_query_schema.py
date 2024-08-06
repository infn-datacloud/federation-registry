import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.query import (
    DbQueryCommonParams,
    Pagination,
    SchemaSize,
    create_query_model,
)
from tests.schemas.utils import (
    TestModelBool,
    TestModelDate,
    TestModelDateTime,
    TestModelEnum,
    TestModelFloat,
    TestModelInt,
    TestModelStr,
    db_query_schema_dict,
    pagination_schema_dict,
    schema_size_schema_dict,
)
from tests.utils import random_lower_string


@parametrize_with_cases("attr", has_tag=("attr", "schema_size"))
def test_valid_schema(attr: str) -> None:
    d = schema_size_schema_dict(attr)
    item = SchemaSize(**d)
    assert item.short == d.get("short", False)
    assert item.with_conn == d.get("with_conn", False)


@parametrize_with_cases("attr", has_tag=("invalid_attr", "schema_size"))
def test_invalid_schema(attr: str) -> None:
    with pytest.raises(ValueError):
        SchemaSize(**schema_size_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("attr", "pagination"))
def test_valid_pagination(attr: str) -> None:
    d = pagination_schema_dict(attr)
    item = Pagination(**d)
    assert item.page == d.get("page", 0)
    assert item.size == d.get("size", None)


def test_set_page_to_0() -> None:
    item = Pagination(page=1)
    assert item.size is None
    assert item.page == 0


@parametrize_with_cases("attr", has_tag=("invalid_attr", "pagination"))
def test_invalid_pagination(attr: str) -> None:
    with pytest.raises(ValueError):
        Pagination(**pagination_schema_dict(attr, valid=False))


@parametrize_with_cases("attr", has_tag=("attr", "db_query"))
def test_valid_db_params(attr: str) -> None:
    d = db_query_schema_dict(attr)
    item = DbQueryCommonParams(**d)
    assert item.skip == d.get("skip", 0)
    assert item.limit == d.get("limit", None)
    assert item.sort == d.get("sort", None)


@parametrize_with_cases("input, output", has_tag=("attr", "sort"))
def test_parse_sort(input: str, output: str) -> None:
    item = DbQueryCommonParams(sort=input)
    assert item.sort is not None
    assert item.sort == output


@parametrize_with_cases("attr", has_tag=("invalid_attr", "db_query"))
def test_invalid_db_params(attr: str) -> None:
    with pytest.raises(ValueError):
        DbQueryCommonParams(**db_query_schema_dict(attr, valid=False))


def test_bool() -> None:
    cls = create_query_model(random_lower_string(), TestModelBool)
    item = cls()
    assert item.test_field is None


@parametrize_with_cases("model", has_tag=("model", "number"))
def test_numbers(model: type[TestModelInt] | type[TestModelFloat]) -> None:
    cls = create_query_model(random_lower_string(), model)
    item = cls()
    assert item.test_field is None
    assert item.test_field__lt is None
    assert item.test_field__gt is None
    assert item.test_field__lte is None
    assert item.test_field__gte is None
    assert item.test_field__ne is None


@parametrize_with_cases("model", has_tag=("model", "date"))
def test_dates(model: type[TestModelDate] | type[TestModelDateTime]) -> None:
    cls = create_query_model(random_lower_string(), model)
    item = cls()
    assert item.test_field__lt is None
    assert item.test_field__gt is None
    assert item.test_field__lte is None
    assert item.test_field__gte is None
    assert item.test_field__ne is None


@parametrize_with_cases("model", has_tag=("model", "str"))
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
