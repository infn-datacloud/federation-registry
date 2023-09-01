from typing import List

from app.identity_provider.schemas import (
    IdentityProviderRead,
    IdentityProviderReadPublic,
)
from app.project.schemas import ProjectRead, ProjectReadPublic
from app.project.schemas_extended import QuotaReadExtended
from app.provider.schemas import ProviderRead, ProviderReadPublic
from app.sla.schemas import SLARead, SLAReadPublic
from app.user_group.schemas import UserGroupRead, UserGroupReadPublic
from pydantic import Field


class ProjectReadExtended(ProjectRead):
    """Model to extend the Project data read from the DB with the lists of
    related items."""

    provider: ProviderRead = Field(description="Provider owning this project")
    quotas: List[QuotaReadExtended] = Field(
        default_factory=list,
        description="List of quotas owned by this Project.",
    )


class ProjectReadExtendedPublic(ProjectReadPublic):
    """Model to extend the Project data read from the DB with the lists of
    related items."""

    provider: ProviderReadPublic = Field(description="Provider owning this project")
    quotas: List[QuotaReadExtended] = Field(
        default_factory=list,
        description="List of quotas owned by this Project.",
    )


class UserGroupReadExtended(UserGroupRead):
    """Model to extend the User Group data read from the DB with the lists of
    related items."""

    identity_provider: IdentityProviderRead = Field(
        description="Identity Provider owning this User Group."
    )


class UserGroupReadExtendedPublic(UserGroupReadPublic):
    """Model to extend the User Group data read from the DB with the lists of
    related items."""

    identity_provider: IdentityProviderReadPublic = Field(
        description="Identity Provider owning this User Group."
    )


class SLAReadExtended(SLARead):
    """Model to extend the SLA data read from the DB with the lists of related
    items for authenticated users."""

    project: ProjectReadExtended = Field(description="Involved Project.")
    user_group: UserGroupReadExtended = Field(description="Involved User Group.")


class SLAReadExtendedPublic(SLAReadPublic):
    """Model to extend the SLA data read from the DB with the lists of related
    items for non-authenticated users."""

    project: ProjectReadExtendedPublic = Field(description="Involved Project.")
    user_group: UserGroupReadExtendedPublic = Field(description="Involved User Group.")
