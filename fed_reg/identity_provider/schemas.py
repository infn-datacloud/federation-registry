"""Pydantic models of the Identity Provider."""
from typing import Optional

from pydantic import AnyHttpUrl, Field

from fed_reg.identity_provider.constants import DOC_CLAIM, DOC_ENDP
from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model


class IdentityProviderBasePublic(BaseNode):
    """Model with Identity Provider public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
    """

    endpoint: AnyHttpUrl = Field(description=DOC_ENDP)


class IdentityProviderBase(IdentityProviderBasePublic):
    """Model with Identity Provider public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        group_claim (str): Value of the key from which retrieve the user group name from
            an authentication token.
    """

    group_claim: str = Field(description=DOC_CLAIM)


class IdentityProviderCreate(BaseNodeCreate, IdentityProviderBase):
    """Model to create an Identity Provider.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        group_claim (str): Value of the key from which retrieve the user group name from
            an authentication token.
    """


class IdentityProviderUpdate(BaseNodeCreate, IdentityProviderBase):
    """Model to update an Identity Provider.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        endpoint (str | None): URL of the Identity Provider.
        group_claim (str): Value of the key from which retrieve the user group name from
            an authentication token.
    """

    endpoint: Optional[AnyHttpUrl] = Field(default=None, description=DOC_ENDP)
    group_claim: Optional[str] = Field(default=None, description=DOC_CLAIM)


class IdentityProviderReadPublic(BaseReadPublic, IdentityProviderBasePublic):
    """Model, for non-authenticated users, to read IdentityProvider data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Identity Provider unique ID.
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
    """


class IdentityProviderRead(BaseReadPrivate, IdentityProviderBase):
    """Model, for authenticated users, to read IdentityProvider data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Identity Provider unique ID.
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        group_claim (str): Value of the key from which retrieve the user group name from
            an authentication token.
    """


IdentityProviderQuery = create_query_model(
    "IdentityProviderQuery", IdentityProviderBase
)
