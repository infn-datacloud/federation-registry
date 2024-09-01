from datetime import date, datetime
from uuid import uuid4

import pytest
from neo4j.time import Date, DateTime
from pytest_cases import case, parametrize_with_cases

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeQuery,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPrivateExtended,
    BaseReadPublic,
    BaseReadPublicExtended,
)
from tests.generics.utils import (
    TestEnum,
    TestModelChild,
    TestModelChildDataInRelation,
    TestModelChildExtended,
    TestModelChildMandatoryExtended,
    TestModelCreateInt,
    TestModelEnum,
    TestModelParent,
    TestModelParentDataInRelation,
    TestModelParentExtended,
    TestModelParentMandatoryExtended,
    TestModelReadDate,
    TestModelReadDateTime,
    TestModelUUID,
    TestORMChild,
    TestORMChildDataInRelation,
    TestORMChildMandatory,
    TestORMDate,
    TestORMDateTime,
    TestORMParent,
    TestORMParentDataInRelation,
    TestORMParentMandatory,
)
from tests.utils import random_date, random_datetime, random_int, random_lower_string


@pytest.fixture
def parent_model() -> TestORMParent:
    return TestORMParent().save()


@pytest.fixture
def parent_mandatory_model() -> TestORMParentMandatory:
    return TestORMParentMandatory().save()


@pytest.fixture
def parent_with_data_rel_model() -> TestORMParentDataInRelation:
    return TestORMParentDataInRelation().save()


@pytest.fixture
def child_model1() -> TestORMChild:
    return TestORMChild().save()


@pytest.fixture
def child_model2() -> TestORMChild:
    return TestORMChild().save()


@pytest.fixture
def child_mandatory_model1() -> TestORMChildMandatory:
    return TestORMChildMandatory().save()


@pytest.fixture
def child_mandatory_model2() -> TestORMChildMandatory:
    return TestORMChildMandatory().save()


@pytest.fixture
def child_with_data_rel_model() -> TestORMChildDataInRelation:
    return TestORMChildDataInRelation().save()


class CaseDates:
    @case(tags=["date"])
    def case_py_date(self) -> tuple[date, date]:
        d = random_date()
        return d, d

    @case(tags=["date"])
    def case_neo4j_date(self) -> tuple[date, date]:
        d = random_date()
        return Date(d.year, d.month, d.day), d

    @case(tags=["datetime"])
    def case_py_datetime(self) -> tuple[datetime, datetime]:
        d = random_datetime()
        return d, d

    @case(tags=["datetime"])
    def case_neo4j_datetime(self) -> tuple[datetime, datetime]:
        d = random_datetime()
        return DateTime(
            d.year, d.month, d.day, d.hour, d.minute, d.second, tzinfo=d.tzinfo
        ), d


class CaseReadDerived:
    def case_read_public(self) -> type[BaseReadPublic]:
        return BaseReadPublic

    def case_read_private(self) -> type[BaseReadPrivate]:
        return BaseReadPrivate

    def case_read_public_exteded(self) -> type[BaseReadPublicExtended]:
        return BaseReadPublicExtended

    def case_read_private_extended(self) -> type[BaseReadPrivateExtended]:
        return BaseReadPrivateExtended


def test_base_node() -> None:
    """Test BaseNode's attributes default values."""
    base_node = BaseNode()
    assert base_node.description is not None
    assert base_node.description == ""


def test_valid_description() -> None:
    """Set description value."""
    desc = random_lower_string()
    base_node = BaseNode(description=desc)
    assert base_node.description is not None
    assert base_node.description == desc


def test_not_none() -> None:
    """Test that description can't be None. It is always an empty string.

    This test validates the not_none validator.
    """
    base_node = BaseNode(description=None)
    assert base_node.description is not None
    assert base_node.description == ""


def test_get_str_from_uuid() -> None:
    """Test that uuids are converted to string thorugh the `hex` function.

    Only UUIDs are converted. Strings are unchanged.
    """
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


def test_create_schema() -> None:
    """Test validate assignment on BaseNodeCreate derived classes.

    Assigning a value of a wrong type raises a ValueError.
    """
    assert BaseNodeCreate.__config__.validate_assignment
    assert TestModelCreateInt.__config__.validate_assignment

    item = TestModelCreateInt(test_field=random_int())

    value = random_int()
    item.test_field = value
    assert item.test_field == value

    with pytest.raises(ValueError):
        item.test_field = random_lower_string()


def test_read_schema() -> None:
    """The BaseNodeRead class must have the uid attribute."""
    assert BaseNodeRead.__config__.validate_assignment
    assert BaseNodeRead.__config__.orm_mode

    s = random_lower_string()
    base_node = BaseNodeRead(uid=s)
    assert base_node.uid is not None
    assert base_node.uid == s

    with pytest.raises(ValueError):
        BaseNodeRead()


@parametrize_with_cases("input, output", cases=CaseDates, has_tag="date")
def test_cast_neo4j_date(input: date | Date, output: date) -> None:
    """Convert Neo4j dates to python dates"""
    item = TestORMDate(date_test=input)
    assert TestModelReadDate.__config__.validate_assignment
    assert TestModelReadDate.__config__.orm_mode
    item = TestModelReadDate.from_orm(item)
    assert item.date_test is not None
    assert item.date_test == output


@parametrize_with_cases("input, output", cases=CaseDates, has_tag="datetime")
def test_cast_neo4j_datetime(input: date | Date, output: date) -> None:
    """Convert Neo4j datetimes to python datetimes"""
    item = TestORMDateTime(datetime_test=input)
    assert TestModelReadDateTime.__config__.validate_assignment
    assert TestModelReadDateTime.__config__.orm_mode
    item = TestModelReadDateTime.from_orm(item)
    assert item.datetime_test is not None
    assert item.datetime_test == output


def test_optional_relationships(
    parent_model: TestORMParent, child_model1: TestORMChild, child_model2: TestORMChild
):
    """Test parent child relationships in pydantic classes.

    Testing ZeroOrOne or ZeroOrMore relationships types.
    At first no relationships.
    Then both parent and child has one relationship.
    Then parent has 2 relationships.
    """
    parent = TestModelParentExtended.from_orm(parent_model)
    assert len(parent.children) == 0

    child = TestModelChildExtended.from_orm(child_model1)
    assert child.parent is None

    parent_model.children.connect(child_model1)

    parent = TestModelParentExtended.from_orm(parent_model)
    child = TestModelChild.from_orm(child_model1)
    assert len(parent.children) == 1
    assert parent.children[0] == child

    child = TestModelChildExtended.from_orm(child_model1)
    parent = TestModelParent.from_orm(parent_model)
    assert child.parent is not None
    assert child.parent == parent

    parent_model.children.connect(child_model2)

    parent = TestModelParentExtended.from_orm(parent_model)
    child = TestModelChild.from_orm(child_model2)
    assert len(parent.children) == 2
    assert parent.children[1] == child


def test_mandatory_relationships(
    parent_mandatory_model: TestORMParentMandatory,
    child_mandatory_model1: TestORMChildMandatory,
    child_mandatory_model2: TestORMChildMandatory,
):
    """Test parent child relationships in pydantic classes.

    Testing One or OneOrMore relationships types.
    Parent and children must have relationships.
    """
    parent_mandatory_model.children.connect(child_mandatory_model1)
    parent_mandatory_model.children.connect(child_mandatory_model2)

    parent = TestModelParentMandatoryExtended.from_orm(parent_mandatory_model)
    child1 = TestModelChild.from_orm(child_mandatory_model1)
    child2 = TestModelChild.from_orm(child_mandatory_model2)
    assert len(parent.children) == 2
    assert parent.children[0] == child1
    assert parent.children[1] == child2

    parent = TestModelParent.from_orm(parent_mandatory_model)
    child = TestModelChildMandatoryExtended.from_orm(child_mandatory_model1)
    assert child.parent is not None
    assert child.parent == parent
    child = TestModelChildMandatoryExtended.from_orm(child_mandatory_model2)
    assert child.parent is not None
    assert child.parent == parent


def test_relationships_with_data(
    parent_with_data_rel_model: TestORMParentDataInRelation,
    child_with_data_rel_model: TestORMChildDataInRelation,
):
    """Test parent child relationships in pydantic classes.

    Testing ZeroOrOne or ZeroOrMore relationships types.
    At first no relationships.
    Then both parent and child has one relationship.
    Then parent has 2 relationships.
    """
    s = random_lower_string()
    parent_with_data_rel_model.children.connect(
        child_with_data_rel_model, {"test_field": s}
    )

    parent = TestModelParentDataInRelation.from_orm(parent_with_data_rel_model)
    assert len(parent.children) == 1
    assert parent.children[0].relationship.test_field == s

    child = TestModelChildDataInRelation.from_orm(child_with_data_rel_model)
    assert child.parent is not None
    assert child.parent.relationship.test_field == s


@parametrize_with_cases("cls", cases=CaseReadDerived)
def test_derived_read(
    cls: type[BaseReadPrivate]
    | type[BaseReadPublic]
    | type[BaseReadPrivateExtended]
    | type[BaseReadPublicExtended],
) -> None:
    """Test BaseNodeRead derived classes inheritance."""
    assert issubclass(cls, BaseNodeRead)
    assert cls.__config__.orm_mode
    assert cls.__config__.validate_assignment

    s = random_lower_string()
    item = cls(uid=s)
    assert item.uid == s

    with pytest.raises(ValueError):
        cls()


def test_base_read_derived_attr() -> None:
    """Test BaseNodeRead derived classes attribute."""
    s = random_lower_string()
    item = BaseReadPublic(uid=s)
    assert item.schema_type == "public"

    item = BaseReadPrivate(uid=s)
    assert item.schema_type == "private"

    item = BaseReadPublicExtended(uid=s)
    assert item.schema_type == "public_extended"

    item = BaseReadPrivateExtended(uid=s)
    assert item.schema_type == "private_extended"


def test_query_schema() -> None:
    """Test validate assignment on BaseNodeQuery."""
    assert BaseNodeQuery.__config__.validate_assignment
