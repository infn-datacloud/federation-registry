"""Pydantic models of the Region owned by a Provider."""
from pydantic import Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model
from fed_reg.region.constants import (
    DOC_BAND_IN,
    DOC_BAND_OUT,
    DOC_NAME,
    DOC_OVERBOOKING_CPU,
    DOC_OVERBOOKING_RAM,
)


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
        overbooking_cpu (float): CPU overbooking factor.
        overbooking_ram (float): RAM overbooking factor.
        bandwidth_in (float): Bandwidth in.
        bandwidth_out (float): Bandwidth out.
    """

    overbooking_cpu: float = Field(default=1.0, description=DOC_OVERBOOKING_CPU)
    overbooking_ram: float = Field(default=1.0, description=DOC_OVERBOOKING_RAM)
    bandwidth_in: float = Field(default=10.0, description=DOC_BAND_IN)
    bandwidth_out: float = Field(default=10.0, description=DOC_BAND_OUT)


class RegionCreate(BaseNodeCreate, RegionBase):
    """Model to create a Region.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Region name in the Provider.
        overbooking_cpu (float): CPU overbooking factor.
        overbooking_ram (float): RAM overbooking factor.
        bandwidth_in (float): Bandwidth in.
        bandwidth_out (float): Bandwidth out.
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
        overbooking_cpu (float | None): CPU overbooking factor.
        overbooking_ram (float | None): RAM overbooking factor.
        bandwidth_in (float | None): Bandwidth in.
        bandwidth_out (float | None): Bandwidth out.
    """

    name: str | None = Field(default=None, description=DOC_NAME)
    overbooking_cpu: float | None = Field(default=1.0, description=DOC_OVERBOOKING_CPU)
    overbooking_ram: float | None = Field(default=1.0, description=DOC_OVERBOOKING_RAM)
    bandwidth_in: float | None = Field(default=10.0, description=DOC_BAND_IN)
    bandwidth_out: float | None = Field(default=10.0, description=DOC_BAND_OUT)


class RegionReadPublic(BaseNodeRead, BaseReadPublic, RegionBasePublic):
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


class RegionRead(BaseNodeRead, BaseReadPrivate, RegionBase):
    """Model, for authenticated users, to read Region data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Region name in the Provider.
        overbooking_cpu (float): CPU overbooking factor.
        overbooking_ram (float): RAM overbooking factor.
        bandwidth_in (float): Bandwidth in.
        bandwidth_out (float): Bandwidth out.
    """


RegionQuery = create_query_model("RegionQuery", RegionBase)
