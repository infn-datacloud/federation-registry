from datetime import date
from uuid import uuid4

import pytest
from neo4j.time import Date
from pytest_cases import parametrize_with_cases

from fed_reg.models import BaseNode, BaseNodeRead
from tests.schemas.utils import (
    TestEnum,
    TestModelEnum,
    TestModelReadDate,
    TestModelReadDateTime,
    TestModelUUID,
    TestORMDate,
    TestORMDateTime,
)
from tests.utils import random_lower_string


def test_default() -> None:
    """Test BaseNode's attributes default values."""
    base_node = BaseNode()
    assert base_node.description is not None
    assert base_node.description == ""


def test_valid_schema() -> None:
    """Set description value."""
    desc = random_lower_string()
    base_node = BaseNode(description=desc)
    assert base_node.description is not None
    assert base_node.description == desc


def test_not_none() -> None:
    """Test that description can't be None. It is always an empty string."""
    base_node = BaseNode(description=None)
    assert base_node.description is not None
    assert base_node.description == ""


def test_get_str_from_uuid() -> None:
    """Test that uuids are converted to string thorugh the `hex` function."""
    uuid1 = uuid4()
    uuid2 = uuid4()
    uuid1_str = uuid1.hex
    uuid2_str = uuid2.hex
    s = random_lower_string()

    # Test with a single uuid
    item = TestModelUUID(uuid=uuid1)
    assert item.uuid == uuid1_str

    # Test with a list of uuids
    item = TestModelUUID(uuid_list=[uuid1, uuid2])
    assert item.uuid_list == [uuid1_str, uuid2_str]

    # Test with a single non-uuid value
    item = TestModelUUID(uuid=s)
    assert item.uuid == s

    # Test with a list of mixed uuid and non-uuid values
    item = TestModelUUID(uuid_list=[uuid1, s, uuid2])
    assert item.uuid_list == [uuid1_str, s, uuid2_str]


def test_get_value_from_enums() -> None:
    """Test that enumerations are converted to strings."""
    model_instance = TestModelEnum(test_field=TestEnum.VALUE_1)
    assert model_instance.test_field == TestEnum.VALUE_1.value

    with pytest.raises(ValueError):
        TestModelEnum(test_field="VALUE_2")


def test_valid_read_schema() -> None:
    assert BaseNodeRead.__config__.orm_mode

    s = random_lower_string()
    base_node = BaseNodeRead(uid=s)
    assert base_node.uid is not None
    assert base_node.uid == s


def test_invalid_read_schema() -> None:
    with pytest.raises(ValueError):
        BaseNodeRead()


@parametrize_with_cases("input, output", has_tag="date")
def test_cast_neo4j_date(input: date | Date, output: date) -> None:
    item = TestORMDate(date_test=input)
    item = TestModelReadDate.from_orm(item)
    assert item.date_test is not None
    assert item.date_test == output


@parametrize_with_cases("input, output", has_tag="datetime")
def test_cast_neo4j_datetime(input: date | Date, output: date) -> None:
    item = TestORMDateTime(datetime_test=input)
    item = TestModelReadDateTime.from_orm(item)
    assert item.datetime_test is not None
    assert item.datetime_test == output


# TODO test relationships validators
