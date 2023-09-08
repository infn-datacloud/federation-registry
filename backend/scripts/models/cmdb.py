from typing import List

from app.flavor.schemas import FlavorCreate
from app.image.schemas import ImageCreate
from app.project.schemas import ProjectCreate
from app.provider.schemas_extended import (
    AuthMethodCreate,
    IdentityProviderCreateExtended,
    ProviderCreateExtended,
    ProviderReadExtended,
)
from pydantic import UUID4, Field


class AuthMethod(AuthMethodCreate):
    pass


class IdentityProvider(IdentityProviderCreateExtended):
    pass


class Project(ProjectCreate):
    pass


class Flavor(FlavorCreate):
    projects: List[UUID4] = Field(
        default_factory=list,
        description="List of projects UUIDs which have access to this flavor",
    )


class Image(ImageCreate):
    projects: List[UUID4] = Field(
        default_factory=list,
        description="List of projects UUIDs which have access to this image",
    )


class Provider(ProviderCreateExtended):
    flavors: List[Flavor] = Field(default_factory=list, description="List of flavors")
    images: List[Image] = Field(default_factory=list, description="List of images")


class ProviderRead(ProviderReadExtended):
    pass