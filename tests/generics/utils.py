from datetime import date, datetime
from enum import Enum
from typing import Any

from neomodel import (
    DateProperty,
    DateTimeProperty,
    One,
    OneOrMore,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    ZeroOrMore,
    ZeroOrOne,
)
from pydantic import BaseModel, Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPrivateExtended,
    BaseReadPublic,
    BaseReadPublicExtended,
)
from tests.utils import (
    random_lower_string,
    random_non_negative_int,
    random_positive_int,
)


class TestEnum(Enum):
    __test__ = False
    VALUE_1 = "value_1"
    VALUE_2 = "value_2"


class TestModelBool(BaseNode):
    __test__ = False
    test_field: bool = Field(..., description="A test field for booleans")


class TestModelInt(BaseNode):
    __test__ = False
    test_field: int = Field(..., description="A test field for integers")


class TestModelFloat(BaseNode):
    __test__ = False
    test_field: float = Field(..., description="A test field for floats")


class TestModelStr(BaseNode):
    __test__ = False
    test_field: str = Field(..., description="A test field for strings")


class TestModelDate(BaseNode):
    __test__ = False
    test_field: date = Field(..., description="A test field for dates")


class TestModelDateTime(BaseNode):
    __test__ = False
    test_field: datetime = Field(..., description="A test field for datetimes")


class TestModelEnum(BaseNode):
    __test__ = False
    test_field: TestEnum = Field(..., description="A test field for enums")


class TestModelUUID(BaseNode):
    __test__ = False
    uuid: str = Field(default="", description="A test field for uuid")
    uuid_list: list[str] = Field(
        default_factory=list, description="A test field for list of uuids"
    )


class TestModelCreateInt(BaseNodeCreate):
    __test__ = False
    test_field: int = Field(..., description="A test field for integers")


class TestModelReadDate(BaseNodeRead):
    __test__ = False
    date_test: date = Field(..., description="A test field for dates")


class TestModelReadDateTime(BaseNodeRead):
    __test__ = False
    datetime_test: datetime = Field(..., description="A test field for dates")


class TestModelReadPrivate(BaseReadPrivate):
    __test__ = False


class TestModelReadPublic(BaseReadPublic):
    __test__ = False


class TestModelReadPrivateExtended(BaseReadPrivateExtended):
    __test__ = False


class TestModelReadPublicExtended(BaseReadPublicExtended):
    __test__ = False


class TestORMUID(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())


class TestORMDate(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    date_test = DateProperty()


class TestORMDateTime(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    date_test = DateTimeProperty()


class TestModelChild(BaseNodeRead):
    __test__ = False


class TestModelParent(BaseNodeRead):
    __test__ = False


class TestModelChildExtended(BaseNodeRead):
    __test__ = False
    parent: TestModelParent | None = Field(..., description="Optional parent node.")


class TestModelParentExtended(BaseNodeRead):
    __test__ = False
    children: list[TestModelChild] = Field(
        default_factory=list, description="Optional list of children nodes."
    )


class TestModelChildMandatoryExtended(BaseNodeRead):
    __test__ = False
    parent: TestModelParent = Field(..., description="Parent node.")


class TestModelParentMandatoryExtended(BaseNodeRead):
    __test__ = False
    children: list[TestModelChild] = Field(..., description="List of children nodes.")


class TestModelRelationship(BaseModel):
    __test__ = False
    test_field: str | None = Field(..., description="Generic test field.")

    class Config:
        orm_mode = True


class TestModelChildWithRelationship(BaseNodeRead):
    __test__ = False
    relationship: TestModelRelationship = Field(..., description="Relationship data.")


class TestModelParentDataInRelation(BaseNodeRead):
    __test__ = False
    children: list[TestModelChildWithRelationship] = Field(
        ..., description="List of children nodes."
    )


class TestModelParentdWithRelationship(BaseNodeRead):
    __test__ = False
    relationship: TestModelRelationship = Field(..., description="Relationship data.")


class TestModelChildDataInRelation(BaseNodeRead):
    __test__ = False
    parent: TestModelParentdWithRelationship = Field(..., description="Parent node.")


class TestORMChild(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    parent = RelationshipTo("TestORMParent", "HAS", cardinality=ZeroOrOne)


class TestORMParent(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    children = RelationshipFrom("TestORMChild", "HAS", cardinality=ZeroOrMore)


class TestORMChildMandatory(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    parent = RelationshipTo("TestORMParentMandatory", "HAS", cardinality=One)


class TestORMParentMandatory(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    children = RelationshipFrom("TestORMChildMandatory", "HAS", cardinality=OneOrMore)


class TestORMRelationship(StructuredRel):
    __test__ = False
    test_field = StringProperty()


class TestORMParentDataInRelation(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    children = RelationshipFrom(
        "TestORMChildDataInRelation",
        "HAS",
        cardinality=ZeroOrMore,
        model=TestORMRelationship,
    )


class TestORMChildDataInRelation(StructuredNode):
    __test__ = False
    uid = StringProperty(default=random_lower_string())
    parent = RelationshipTo(
        "TestORMParentDataInRelation",
        "HAS",
        cardinality=ZeroOrOne,
        model=TestORMRelationship,
    )


def schema_size_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("short", "with_conn"):
            data[k] = True
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def schema_size_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("short", "with_conn"):
            data[k] = None
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def schema_size_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("valid", True):
        return schema_size_valid_dict(d, *args)
    return schema_size_invalid_dict(d, *args)


def pagination_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("page",):
            data["size"] = random_positive_int()
            data[k] = random_non_negative_int()
        elif k in ("size",):
            data[k] = random_positive_int()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def pagination_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("page",):
            data["size"] = random_positive_int()
            data[k] = -1
        elif k in ("size_0",):
            data["size"] = 0
        elif k in ("negative_size",):
            data["size"] = -1
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def pagination_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("valid", True):
        return pagination_valid_dict(d, *args)
    return pagination_invalid_dict(d, *args)


def db_query_valid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("skip", "limit"):
            data[k] = random_non_negative_int()
        elif k in ("sort",):
            data[k] = random_lower_string()
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def db_query_invalid_dict(data: dict[str, Any], *args, **kwargs) -> dict[str, Any]:
    for k in args:
        if k in ("limit", "skip"):
            data[k] = -1
        else:
            raise AttributeError(f"attribute {k} not found in class definition")
    return data


def db_query_schema_dict(*args, **kwargs) -> dict[str, Any]:
    d = {}
    if kwargs.get("valid", True):
        return db_query_valid_dict(d, *args)
    return db_query_invalid_dict(d, *args)
