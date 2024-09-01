"""Pydantic models of the Project owned by a Provider."""
from typing import Optional

from pydantic import Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.project.constants import DOC_NAME, DOC_UUID
from fed_reg.query import create_query_model


class ProjectBasePublic(BaseNode):
    """Model with Project public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Project name in the Provider.
        uuid (str): Project unique ID in the Provider
    """

    name: str = Field(description=DOC_NAME)
    uuid: str = Field(description=DOC_UUID)


class ProjectBase(ProjectBasePublic):
    """Model with Project public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Project name in the Provider.
        uuid (str): Project unique ID in the Provider
    """


class ProjectCreate(BaseNodeCreate, ProjectBase):
    """Model to create a Project.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Project name in the Provider.
        uuid (str): Project unique ID in the Provider
    """


class ProjectUpdate(BaseNodeCreate, ProjectBase):
    """Model to update a Project.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        name (str | None): Project name in the Provider.
        uuid (str | None): Project unique ID in the Provider
    """

    name: Optional[str] = Field(default=None, description=DOC_NAME)
    uuid: Optional[str] = Field(default=None, description=DOC_UUID)


class ProjectReadPublic(BaseReadPublic, ProjectBasePublic):
    """Model, for non-authenticated users, to read Project data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Project unique ID.
        description (str): Brief description.
        name (str): Project name in the Provider.
        uuid (str): Project unique ID in the Provider
    """


class ProjectRead(BaseReadPrivate, ProjectBase):
    """Model, for authenticated users, to read Project data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (uuid): AssociatedProject unique ID.
        description (str): Brief description.
        name (str): Project name in the Provider.
        uuid (str): Project unique ID in the Provider
    """


ProjectQuery = create_query_model("ProjectQuery", ProjectBase)
