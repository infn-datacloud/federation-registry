from typing import Literal

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.pagination import Pagination, paginate
from tests.generics.utils import pagination_schema_dict


class CaseItems:
    @case(tags="empty")
    def case_no_items(self) -> list[int]:
        return []

    @case(tags=("not_empty", "single_item"))
    def case_single_item(self) -> list[int]:
        return [1]

    @case(tags=("not_empty", "multiple_items"))
    def case_multiple_items(self) -> list[int]:
        return [1, 2]


class CaseNoSize:
    def case_none(self) -> None:
        return None

    def case_0(self) -> Literal[0]:
        return 0


class CasePage:
    def case_0(self) -> Literal[0]:
        return 0

    def case_1(self) -> Literal[1]:
        return 1


class CasePaginationAttr:
    @case(tags="attr")
    @parametrize(value=["page", "size"])
    def case_valid_pagination(self, value: str) -> str:
        return value

    @case(tags="invalid_attr")
    @parametrize(value=["page", "size_0", "negative_size"])
    def case_invalid_pagination(self, value: str) -> str:
        return value


@parametrize_with_cases("attr", cases=CasePaginationAttr, has_tag="attr")
def test_valid_pagination_schema(attr: str) -> None:
    d = pagination_schema_dict(attr)
    item = Pagination(**d)
    assert item.page == d.get("page", 0)
    assert item.size == d.get("size", None)


def test_set_schema_page_to_0() -> None:
    item = Pagination(page=1)
    assert item.size is None
    assert item.page == 0


@parametrize_with_cases("attr", cases=CasePaginationAttr, has_tag="invalid_attr")
def test_invalid_pagination_schema(attr: str) -> None:
    with pytest.raises(ValueError):
        Pagination(**pagination_schema_dict(attr, valid=False))


@parametrize_with_cases("items", cases=CaseItems)
@parametrize_with_cases("page", cases=CasePage)
@parametrize_with_cases("size", cases=CaseNoSize)
def test_no_pagination(items: list[int], page: int, size: int) -> None:
    """Test when no pagination is applied.

    Assert that the input list (of any size) is unchanged when:
    - size is 0 or None
    - page is 0 or non zero but size is 0 or None
    """
    paginated_items = paginate(items=items, page=page, size=size)
    assert len(paginated_items) == len(items)


@parametrize_with_cases("items", cases=CaseItems, has_tag="empty")
@parametrize_with_cases("page", cases=CasePage)
def test_empty_list_unchanged(items: list[int], page: int) -> None:
    """Empty lists with size does not raise error and the list is unchanged."""
    paginated_items = paginate(items=items, page=page, size=1)
    assert len(paginated_items) == 0


@parametrize_with_cases("items", cases=CaseItems, has_tag="not_empty")
def test_not_empty_list_with_size(items: list[int]) -> None:
    """With non-empty lists, 'size' shows the first n items if page is 0."""
    paginated_items = paginate(items=items, page=0, size=1)
    assert len(paginated_items) == 1
    assert paginated_items[0] == items[0]


@parametrize_with_cases("items", cases=CaseItems, has_tag="multiple_items")
def test_not_empty_list_with_page(items: list[int]) -> None:
    """With non-empty lists, 'page' splits the list in n chunks.

    'size' shows the first 'size' items if page is 0.
    """
    paginated_items = paginate(items=items, page=1, size=1)
    assert len(paginated_items) == 1
    assert paginated_items[0] == items[1]


@parametrize_with_cases("items", cases=CaseItems, has_tag="single_item")
def test_empty_list_with_page(items: list[int]) -> None:
    """When querying items outside the list size returns and empty list.

    Does not raise error.
    """
    paginated_items = paginate(items=items, page=1, size=1)
    assert len(paginated_items) == 0
