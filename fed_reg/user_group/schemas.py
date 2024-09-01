"""Pydantic models of the User Group owned by an Identity Provider."""
from typing import Optional

from pydantic import Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model
from fed_reg.user_group.constants import DOC_NAME


class UserGroupBasePublic(BaseNode):
    """Model with User Group public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): User Group name in the Identity Provider.
    """

    name: str = Field(description=DOC_NAME)


class UserGroupBase(UserGroupBasePublic):
    """Model with User Group public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): User Group name in the Identity Provider.
    """


class UserGroupCreate(BaseNodeCreate, UserGroupBase):
    """Model to create a User Group.

    Class without id (which is populated by the database).
    Expected as input when performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): User Group name in the Identity Provider.
    """


class UserGroupUpdate(BaseNodeCreate, UserGroupBase):
    """Model to update a User Group.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        name (str | None): User Group name in the Identity Provider.
    """

    name: Optional[str] = Field(default=None, description=DOC_NAME)


class UserGroupReadPublic(BaseReadPublic, UserGroupBasePublic):
    """Model, for non-authenticated users, to read UserGroup data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): UserGroup unique ID.
        description (str): Brief description.
        name (str): UserGroup name in the Provider.
        uuid (str): UserGroup unique ID in the Provider
    """


class UserGroupRead(BaseReadPrivate, UserGroupBase):
    """Model, for authenticated users, to read UserGroup data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): User Group unique ID.
        description (str): Brief description.
        name (str): User Group name in the Identity Provider.
    """


UserGroupQuery = create_query_model("UserGroupQuery", UserGroupBase)
