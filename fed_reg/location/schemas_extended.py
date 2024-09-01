"""Pydantic extended models of the site geographical Location."""


from pydantic import BaseModel, Field

from fed_reg.location.constants import DOC_EXT_REG
from fed_reg.location.schemas import (
    LocationBase,
    LocationBasePublic,
    LocationRead,
    LocationReadPublic,
)
from fed_reg.models import BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.region.schemas import RegionRead, RegionReadPublic


class LocationReadExtended(BaseReadPrivateExtended, LocationBase):
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

    regions: list[RegionRead] = Field(description=DOC_EXT_REG)


class LocationReadExtendedPublic(BaseReadPublicExtended, LocationBasePublic):
    """Model to extend the Location public data read from the DB.

    Attributes:
    ----------
        uid (int): Location unique ID.
        description (str): Brief description.
        site (str): Location unique name.
        regions (list of RegionReadPublic): Hosted regions.
    """

    regions: list[RegionReadPublic] = Field(description=DOC_EXT_REG)


class LocationReadSingle(BaseModel):
    __root__: (
        LocationReadExtended
        | LocationRead
        | LocationReadExtendedPublic
        | LocationReadPublic
    ) = Field(..., discriminator="schema_type")


class LocationReadMulti(BaseModel):
    __root__: list[LocationReadExtended] | list[LocationRead] | list[
        LocationReadExtendedPublic
    ] | list[LocationReadPublic] = Field(..., discriminator="schema_type")
