"""Pydantic extended models of the Region owned by a Provider."""
from typing import Optional

from pydantic import BaseModel, Field

from fed_reg.location.schemas import LocationRead, LocationReadPublic
from fed_reg.models import BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.provider.schemas import ProviderRead, ProviderReadPublic
from fed_reg.region.constants import DOC_EXT_LOC, DOC_EXT_PROV, DOC_EXT_SERV
from fed_reg.region.schemas import RegionRead, RegionReadPublic
from fed_reg.service.schemas import (
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    IdentityServiceRead,
    IdentityServiceReadPublic,
    NetworkServiceRead,
    NetworkServiceReadPublic,
)


class RegionReadExtended(RegionRead, BaseReadPrivateExtended):
    """Model to extend the Region data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        provider (ProviderRead): Provider hosting this region.
        location (LocationRead | None): Location hosting this region.
        services (list of Service): Supplied services (block-storage, compute,
            identity and network type).
    """

    location: Optional[LocationRead] = Field(default=None, description=DOC_EXT_LOC)
    provider: ProviderRead = Field(description=DOC_EXT_PROV)
    services: list[
        BlockStorageServiceRead
        | ComputeServiceRead
        | IdentityServiceRead
        | NetworkServiceRead
    ] = Field(description=DOC_EXT_SERV)


class RegionReadExtendedPublic(RegionReadPublic, BaseReadPublicExtended):
    """Model to extend the Region public data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        provider (ProviderReadPublic): Provider hosting this region.
        location (LocationReadPublic | None): Location hosting this region.
        services (list of ServicePublic): Supplied services (block-storage, compute,
            identity and network type).
    """

    location: Optional[LocationReadPublic] = Field(
        default=None, description=DOC_EXT_LOC
    )
    provider: ProviderReadPublic = Field(description=DOC_EXT_PROV)
    services: list[
        BlockStorageServiceReadPublic
        | ComputeServiceReadPublic
        | IdentityServiceReadPublic
        | NetworkServiceReadPublic
    ] = Field(description=DOC_EXT_SERV)


class RegionReadSingle(BaseModel):
    __root__: (
        RegionReadExtended | RegionRead | RegionReadExtendedPublic | RegionReadPublic
    ) = Field(..., discriminator="schema_type")


class RegionReadMulti(BaseModel):
    __root__: list[RegionReadExtended] | list[RegionRead] | list[
        RegionReadExtendedPublic
    ] | list[RegionReadPublic] = Field(..., discriminator="schema_type")
