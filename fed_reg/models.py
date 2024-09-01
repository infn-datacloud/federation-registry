"""Core pydantic models."""
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from neo4j.time import Date, DateTime
from neomodel import One, OneOrMore, ZeroOrMore, ZeroOrOne
from pydantic import BaseModel, Field, fields, validator


class BaseNode(BaseModel):
    """Common attributes and validators for a schema of a generic neo4j Node.

    Add description field and a validator converting UUIDs to str.

    Attributes:
    ----------
        description (str): Brief item description
    """

    description: str = Field(default="", description="Brief item description")

    @validator("*", pre=True, always=True)
    @classmethod
    def get_str_from_uuid(cls, v: Any, field: fields.ModelField) -> Any:
        """Get hex attribute from UUID values."""
        if field.shape == fields.SHAPE_LIST and not isinstance(
            v, (OneOrMore, ZeroOrMore)
        ):
            return [i.hex if isinstance(i, UUID) else i for i in v]
        return v.hex if isinstance(v, UUID) else v

    @validator("*", always=True)
    @classmethod
    def get_value_from_enums(cls, v: Any) -> Any:
        """Get value from all the enumeration field values."""
        return v.value if isinstance(v, Enum) else v

    @validator("*", pre=True, always=True)
    @classmethod
    def not_none(cls, v: Any, field: fields.ModelField) -> Any:
        """Replace None with field's default.

        If the default value is not None but None is given, set the value equals to the
        field's default one.
        """
        if all((getattr(field, "default", None) is not None, v is None)):
            return field.default
        else:
            return v


class BaseNodeCreate(BaseModel):
    """Common validator when updating or creating a node in the DB.

    When dealing with enumerations retrieve the enum value.
    Always validate assignments.
    """

    class Config:
        """Sub class to validate assignments."""

        validate_assignment = True


class BaseNodeRead(BaseModel):
    """Common attributes and validators when reading nodes from the DB.

    Use ORM mode to read data from DB models.
    Add the uid attribute.
    Convert Neo4j datetime objects into python
    datetime ones.
    When dealing with relationships retrieve all connected items and show
    them as an object list. If a relationships has a model return a dict with the data
    stored in it.
    Always validate assignments.

    Attributes:
    ----------
        uid (str): Database item's unique identifier.
    """

    uid: str = Field(description="Database item's unique identifier.")

    @validator("*", pre=True)
    @classmethod
    def get_single_relation(cls, v: Any) -> Any:
        """From One or ZeroOrOne relationships get that single relationship."""
        if isinstance(v, (One, ZeroOrOne)):
            node = v.single()
            if v.definition.get("model") is None:
                return node
            else:
                item = node.__dict__
                item["relationship"] = v.relationship(node)
                return item
        else:
            return v

    @validator("*", pre=True)
    @classmethod
    def get_multi_relations(cls, v: Any) -> Any:
        """From OneOrMore or ZeroOrMore relationships get all relationships.

        If the relationship has a model, return a dict with the data stored in the
        relationship.
        """
        if isinstance(v, (OneOrMore, ZeroOrMore)):
            if v.definition.get("model") is None:
                return v.all()
            else:
                items = []
                for node in v.all():
                    item = node.__dict__
                    item["relationship"] = v.relationship(node)
                    items.append(item)
                return items
        return v

    @validator("*", pre=True)
    @classmethod
    def cast_neo4j_datetime(cls, v: Any) -> Any:
        """Cast neo4j datetime to python datetime."""
        return v.to_native() if isinstance(v, DateTime) else v

    @validator("*", pre=True)
    @classmethod
    def cast_neo4j_date(cls, v: Any) -> Any:
        """Cast neo4j date to python date."""
        return v.to_native() if isinstance(v, Date) else v

    class Config:
        """Sub class to validate assignments and enable orm mode."""

        validate_assignment = True
        orm_mode = True


class BaseReadPublic(BaseNodeRead):
    """Read schema used to discriminate schemas with public attributes."""

    schema_type: Literal["public"] = Field(
        default="public",
        description="Inner attribute to distinguish between schema types",
    )


class BaseReadPrivate(BaseNodeRead):
    """Read schema used to discriminate schemas with private attributes."""

    schema_type: Literal["private"] = Field(
        default="private",
        description="Inner attribute to distinguish between schema types",
    )


class BaseReadPublicExtended(BaseNodeRead):
    """Read schema used to discriminate schemas with public attr and relationships."""

    schema_type: Literal["public_extended"] = Field(
        default="public_extended",
        description="Inner attribute to distinguish between schema types",
    )


class BaseReadPrivateExtended(BaseNodeRead):
    """Read schema used to discriminate schemas with public attr and relationships."""

    schema_type: Literal["private_extended"] = Field(
        default="private_extended",
        description="Inner attribute to distinguish between schema types",
    )


class BaseNodeQuery(BaseModel):
    """Schema used to retrieve possible query parameters when performing GET operations.

    Always validate assignments.
    """

    class Config:
        """Sub class to validate assignments."""

        validate_assignment = True
