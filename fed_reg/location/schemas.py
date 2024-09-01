"""Pydantic models of the site geographical Location."""
from typing import Any, Dict, Optional

from pycountry import countries
from pydantic import Field, validator

from fed_reg.location.constants import (
    DOC_CODE,
    DOC_COUNTRY,
    DOC_LATI,
    DOC_LONG,
    DOC_SITE,
)
from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model


class LocationBasePublic(BaseNode):
    """Model with Location public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        site (str): Location unique name.
        country (str): Country name.
    """

    site: str = Field(description=DOC_SITE)
    country: str = Field(description=DOC_COUNTRY)

    @validator("country")
    @classmethod
    def is_known_country(cls, v: str) -> str:
        """Validate country."""
        if v:
            assert v in [i.name for i in countries]
        return v


class LocationBase(LocationBasePublic):
    """Model with Location public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        site (str): Location unique name.
        country (str): Country name.
        latitude (float | None): Latitude coordinate.
        longitude (float | None): Longitude coordinate.
    """

    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description=DOC_LATI)
    longitude: Optional[float] = Field(
        default=None, ge=-180, le=180, description=DOC_LONG
    )


class LocationCreate(BaseNodeCreate, LocationBase):
    """Model to create a Location.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        site (str): Location unique name.
        country (str): Country name.
        latitude (float | None): Latitude coordinate.
        longitude (float | None): Longitude coordinate.
    """


class LocationUpdate(BaseNodeCreate, LocationBase):
    """Model to update a Location.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        site (str | None): Location unique name.
        country (str | None): Country name.
        latitude (float | None): Latitude coordinate.
        longitude (float | None): Longitude coordinate.
    """

    site: Optional[str] = Field(default=None, description=DOC_SITE)
    country: Optional[str] = Field(default=None, description=DOC_COUNTRY)


class LocationReadPublic(BaseReadPublic, LocationBasePublic):
    """Model, for non-authenticated users, to read Location data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Location unique ID.
        description (str): Brief description.
        site (str): Location unique name.
    """


class LocationRead(BaseReadPrivate, LocationBase):
    """Model, for authenticated users, to read Location data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.
    Add the *country_code* attribute.

    Attributes:
    ----------
        uid (int): Location unique ID.
        description (str): Brief description.
        site (str): Location unique name.
        country (str): Country name.
        country_code (str): Country code with 3 chars.
        latitude (float | None): Latitude coordinate.
        longitude (float | None): Longitude coordinate.
    """

    country_code: Optional[str] = Field(default=None, description=DOC_CODE)

    @validator("country_code", pre=True, always=True)
    @classmethod
    def get_country_code(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """From country retrieve country code."""
        if not v and values.get("country", None):
            matches = countries.search_fuzzy(values.get("country"))
            if len(matches) > 0:
                return matches[0].alpha_3
        return v


LocationQuery = create_query_model("LocationQuery", LocationBase)
