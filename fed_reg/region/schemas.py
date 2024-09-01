"""Pydantic models of the Region owned by a Provider."""
from typing import Optional

from pydantic import Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model
from fed_reg.region.constants import DOC_NAME


class RegionBasePublic(BaseNode):
    """Model with Region public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Region name in the Provider.
    """

    name: str = Field(description=DOC_NAME)


class RegionBase(RegionBasePublic):
    """Model with Region public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Region name in the Provider.
    """


class RegionCreate(BaseNodeCreate, RegionBase):
    """Model to create a Region.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Region name in the Provider.
    """


class RegionUpdate(BaseNodeCreate, RegionBase):
    """Model to update a Region.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        name (str | None): Region name in the Provider.
    """

    name: Optional[str] = Field(default=None, description=DOC_NAME)


class RegionReadPublic(BaseReadPublic, RegionBasePublic):
    """Model, for non-authenticated users, to read Region data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Region unique ID.
        description (str): Brief description.
        name (str): Region name in the Provider.
    """


class RegionRead(BaseReadPrivate, RegionBase):
    """Model, for authenticated users, to read Region data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Region name in the Provider.
    """


RegionQuery = create_query_model("RegionQuery", RegionBase)
