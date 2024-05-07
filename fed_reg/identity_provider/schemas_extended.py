"""Pydantic extended models of the Identity Provider."""
from typing import List

from pydantic import Field

from fed_reg.auth_method.schemas import AuthMethodRead
from fed_reg.identity_provider.constants import DOC_EXT_GROUP, DOC_EXT_PROV
from fed_reg.identity_provider.schemas import (
    IdentityProviderRead,
    IdentityProviderReadPublic,
)
from fed_reg.provider.constants import DOC_EXT_AUTH_METH
from fed_reg.provider.schemas import ProviderRead, ProviderReadPublic
from fed_reg.user_group.schemas import UserGroupRead, UserGroupReadPublic


class ProviderReadExtended(ProviderRead):
    """Model to extend the Provider data read from the DB.

    Attributes:
    ----------
        uid (int): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): List of maintainers emails.
        relationship (AuthMethodRead): Authentication method used to connect to the
            target identity provider.
    """

    relationship: AuthMethodRead = Field(description=DOC_EXT_AUTH_METH)


class ProviderReadExtendedPublic(ProviderReadPublic):
    """Model to extend the Identity Provider public data read from the DB.

    Attributes:
    ----------
        uid (int): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        relationship (AuthMethodRead): Authentication method used to connect to the
            target identity provider.
    """

    relationship: AuthMethodRead = Field(description=DOC_EXT_AUTH_METH)


class IdentityProviderReadExtended(IdentityProviderRead):
    """Model to extend the Identity Provider data read from the DB.

    Attributes:
    ----------
        uid (int): Identity Provider unique ID.
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        group_claim (str): value of the key from which retrieve
            the user group name from an authentication token.
        providers (list of ProviderReadExtended): Supported providers.
        user_groups (list of UserGroupRead): Owned user groups.
    """

    providers: List[ProviderReadExtended] = Field(description=DOC_EXT_PROV)
    user_groups: List[UserGroupRead] = Field(description=DOC_EXT_GROUP)


class IdentityProviderReadExtendedPublic(IdentityProviderReadPublic):
    """Model to extend the Identity Provider public data read from the DB.

    Attributes:
    ----------
        uid (int): Identity Provider unique ID.
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        providers (list of ProviderReadExtendedPublic): Supported providers.
        user_groups (list of UserGroupReadPublic): Owned user groups.
    """

    providers: List[ProviderReadExtendedPublic] = Field(description=DOC_EXT_PROV)
    user_groups: List[UserGroupReadPublic] = Field(description=DOC_EXT_GROUP)
