from typing import List

from app.flavor.schemas import FlavorRead, FlavorReadPublic
from app.project.schemas import ProjectRead, ProjectReadPublic
from app.provider.schemas import ProviderRead, ProviderReadPublic
from pydantic import Field


class FlavorReadExtended(FlavorRead):
    """Model to extend the Flavor data read from the DB with the lists of
    related items for authenticated users."""

    projects: List[ProjectRead] = Field(
        default_factory=list,
        description="List of projects with access to this Flavor.",
    )
    provider: ProviderRead = Field(description="Provider owning this Flavor.")


class FlavorReadExtendedPublic(FlavorReadPublic):
    """Model to extend the Flavor data read from the DB with the lists of
    related items for non-authenticated users."""

    projects: List[ProjectReadPublic] = Field(
        default_factory=list,
        description="List of projects with access to this Flavor.",
    )
    provider: ProviderReadPublic = Field(description="Provider owning this Flavor.")
