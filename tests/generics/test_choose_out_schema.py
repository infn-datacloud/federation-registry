from typing import Literal

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.utils import choose_out_schema
from tests.generics.utils import (
    TestModelReadPrivate,
    TestModelReadPrivateExtended,
    TestModelReadPublic,
    TestModelReadPublicExtended,
    TestORMUID,
)


@pytest.fixture
def items():
    return [TestORMUID()]


class CaseShort:
    def case_shrunk(self) -> Literal[True]:
        return True

    def case_complete(self) -> Literal[False]:
        return False


@parametrize_with_cases("short", cases=CaseShort)
def test_choose_out_schema_no_auth_no_linked_items(
    items: list[TestORMUID], short: bool
) -> None:
    """When no auth is provided, the returned schema type is 'public'.

    No linked items have been requested. The short flag does not apply changes.
    """
    schema_items = choose_out_schema(
        schema_read_private=TestModelReadPrivate,
        schema_read_public=TestModelReadPublic,
        schema_read_private_extended=TestModelReadPrivateExtended,
        schema_read_public_extended=TestModelReadPublicExtended,
        items=items,
        auth=False,
        with_conn=False,
        short=short,
    )
    assert len(schema_items) == len(items)
    assert schema_items[0].uid == items[0].uid
    assert schema_items[0].schema_type == "public"


@parametrize_with_cases("short", cases=CaseShort)
def test_choose_out_schema_no_auth_with_linked_items(
    items: list[TestORMUID], short: bool
) -> None:
    """When no auth is provided, the returned schema type is 'public'.

    Linked items have been requested. The short flag does not apply changes.
    """
    schema_items = choose_out_schema(
        schema_read_private=TestModelReadPrivate,
        schema_read_public=TestModelReadPublic,
        schema_read_private_extended=TestModelReadPrivateExtended,
        schema_read_public_extended=TestModelReadPublicExtended,
        items=items,
        auth=False,
        with_conn=True,
        short=short,
    )
    assert len(schema_items) == len(items)
    assert schema_items[0].uid == items[0].uid
    assert schema_items[0].schema_type == "public_extended"


def test_choose_out_schema_with_auth_no_linked_items(items: list[TestORMUID]) -> None:
    """When auth is provided, the returned schema type is 'private'.

    No linked items have been requested.
    """
    schema_items = choose_out_schema(
        schema_read_private=TestModelReadPrivate,
        schema_read_public=TestModelReadPublic,
        schema_read_private_extended=TestModelReadPrivateExtended,
        schema_read_public_extended=TestModelReadPublicExtended,
        items=items,
        auth=True,
        with_conn=False,
        short=False,
    )
    assert len(schema_items) == len(items)
    assert schema_items[0].uid == items[0].uid
    assert schema_items[0].schema_type == "private"


def test_choose_out_schema_with_auth_with_linked_items(items: list[TestORMUID]) -> None:
    """When no auth is provided, the returned schema type is 'private_extended'.

    Linked items have been requested.
    """
    schema_items = choose_out_schema(
        schema_read_private=TestModelReadPrivate,
        schema_read_public=TestModelReadPublic,
        schema_read_private_extended=TestModelReadPrivateExtended,
        schema_read_public_extended=TestModelReadPublicExtended,
        items=items,
        auth=True,
        with_conn=True,
        short=False,
    )
    assert len(schema_items) == len(items)
    assert schema_items[0].uid == items[0].uid
    assert schema_items[0].schema_type == "private_extended"


def test_choose_out_schema_with_auth_no_linked_items_shrunk(
    items: list[TestORMUID],
) -> None:
    """When no auth is provided, the returned schema type is 'public'.

    No linked items have been requested.
    """
    schema_items = choose_out_schema(
        schema_read_private=TestModelReadPrivate,
        schema_read_public=TestModelReadPublic,
        schema_read_private_extended=TestModelReadPrivateExtended,
        schema_read_public_extended=TestModelReadPublicExtended,
        items=items,
        auth=True,
        with_conn=False,
        short=True,
    )
    assert len(schema_items) == len(items)
    assert schema_items[0].uid == items[0].uid
    assert schema_items[0].schema_type == "public"


def test_choose_out_schema_with_auth_with_linked_items_shrunk(
    items: list[TestORMUID],
) -> None:
    """When no auth is provided, the returned schema type is 'public_extended'.

    Linked items have been requested.
    """
    schema_items = choose_out_schema(
        schema_read_private=TestModelReadPrivate,
        schema_read_public=TestModelReadPublic,
        schema_read_private_extended=TestModelReadPrivateExtended,
        schema_read_public_extended=TestModelReadPublicExtended,
        items=items,
        auth=True,
        with_conn=True,
        short=True,
    )
    assert len(schema_items) == len(items)
    assert schema_items[0].uid == items[0].uid
    assert schema_items[0].schema_type == "public_extended"
