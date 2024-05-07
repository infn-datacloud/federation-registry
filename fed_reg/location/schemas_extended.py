"""Pydantic extended models of the site geographical Location."""
from typing import List

from pydantic import Field

from fed_reg.location.constants import DOC_EXT_REG
from fed_reg.location.schemas import LocationRead, LocationReadPublic
from fed_reg.region.schemas import RegionRead, RegionReadPublic


class LocationReadExtended(LocationRead):
    """Model to extend the Location data read from the DB.

    Attributes:
    ----------
        uid (int): Location unique ID.
        description (str): Brief description.
        site (str): Location unique name.
        country (str): Country name.
        country_code (str): Country code with 3 chars.
        latitude (float | None): Latitude coordinate.
        longitude (float | None): Longitude coordinate.
        regions (list of RegionRead): Hosted regions.
    """

    regions: List[RegionRead] = Field(description=DOC_EXT_REG)


class LocationReadExtendedPublic(LocationReadPublic):
    """Model to extend the Location public data read from the DB.

    Attributes:
    ----------
        uid (int): Location unique ID.
        description (str): Brief description.
        site (str): Location unique name.
        regions (list of RegionReadPublic): Hosted regions.
    """

    regions: List[RegionReadPublic] = Field(description=DOC_EXT_REG)
