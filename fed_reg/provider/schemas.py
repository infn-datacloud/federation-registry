"""Pydantic models of the Resource Provider (openstack, kubernetes...)."""
from typing import Optional

from pydantic import EmailStr, Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.provider.constants import (
    DOC_EMAIL,
    DOC_NAME,
    DOC_SHARED,
    DOC_STAT,
    DOC_TYPE,
)
from fed_reg.provider.enum import ProviderStatus, ProviderType
from fed_reg.query import create_query_model


class ProviderBasePublic(BaseNode):
    """Model with Provider public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
    """

    name: str = Field(description=DOC_NAME)
    type: ProviderType = Field(description=DOC_TYPE)


class ProviderBase(ProviderBasePublic):
    """Model with Provider public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): list of maintainers emails.
    """

    status: ProviderStatus = Field(default=ProviderStatus.ACTIVE, description=DOC_STAT)
    is_public: bool = Field(default=False, description=DOC_SHARED)
    support_emails: list[EmailStr] = Field(default_factory=list, description=DOC_EMAIL)


class ProviderCreate(BaseNodeCreate, ProviderBase):
    """Model to create a Provider.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): list of maintainers emails.
    """


class ProviderUpdate(BaseNodeCreate, ProviderBase):
    """Model to update a Provider.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        name (str | None): Provider name.
        type (str | None): Provider type.
        status (str | None): Provider status.
        is_public (bool | None): Public or private Provider.
        support_email (list of str | None): list of maintainers emails.
    """

    name: Optional[str] = Field(default=None, description=DOC_NAME)
    type: Optional[ProviderType] = Field(default=None, description=DOC_TYPE)


class ProviderReadPublic(BaseNodeRead, BaseReadPublic, ProviderBasePublic):
    """Model, for non-authenticated users, to read Provider data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
    """


class ProviderRead(BaseNodeRead, BaseReadPrivate, ProviderBase):
    """Model, for authenticated users, to read Provider data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): list of maintainers emails.
    """


ProviderQuery = create_query_model("ProviderQuery", ProviderBase)
