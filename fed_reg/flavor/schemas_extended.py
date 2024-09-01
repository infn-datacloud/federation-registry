"""Pydantic extended models of the Virtual Machine Flavor owned by a Provider."""
from pydantic import BaseModel, Field

from fed_reg.flavor.constants import DOC_EXT_PROJ, DOC_EXT_SERV, DOC_SHARED
from fed_reg.flavor.schemas import (
    FlavorBase,
    FlavorBasePublic,
    FlavorRead,
    FlavorReadPublic,
)
from fed_reg.models import BaseNodeRead, BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.project.schemas import ProjectRead, ProjectReadPublic
from fed_reg.provider.schemas import ProviderRead, ProviderReadPublic
from fed_reg.region.constants import DOC_EXT_PROV
from fed_reg.region.schemas import RegionRead, RegionReadPublic
from fed_reg.service.constants import DOC_EXT_REG
from fed_reg.service.schemas import ComputeServiceRead, ComputeServiceReadPublic


class RegionReadExtended(RegionRead):
    """Model to extend the Region data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        provider (ProviderRead): Provider hosting this region.
    """

    provider: ProviderRead = Field(description=DOC_EXT_PROV)


class RegionReadExtendedPublic(RegionReadPublic):
    """Model to extend the Region public data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        provider (ProviderReadPublic): Provider hosting this region.
    """

    provider: ProviderReadPublic = Field(description=DOC_EXT_PROV)


class ComputeServiceReadExtended(ComputeServiceRead):
    """Model to extend the Compute Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        region (RegionReadExtended): Region hosting this service.
    """

    region: RegionReadExtended = Field(description=DOC_EXT_REG)


class ComputeServiceReadExtendedPublic(ComputeServiceReadPublic):
    """Model to extend the Compute Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadExtendedPublic): Region hosting this service.
    """

    region: RegionReadExtendedPublic = Field(description=DOC_EXT_REG)


class FlavorReadExtended(BaseNodeRead, BaseReadPrivateExtended, FlavorBase):
    """Model to extend the Flavor data read from the DB.

    Attributes:
    ----------
        uid (str): Flavor unique ID.
        description (str): Brief description.
        name (str): Flavor name in the Provider.
        uuid (str): Flavor unique ID in the Provider
        disk (int): Reserved disk size (GiB)
        is_shared (bool): Public or private Flavor.
        ram (int): Reserved RAM (MiB)
        vcpus (int): Number of Virtual CPUs.
        swap (int): Swap size (GiB).
        ephemeral (int): Ephemeral disk size (GiB).
        infiniband (bool): MPI - parallel multi-process enabled.
        gpus (int): Number of GPUs.
        gpu_model (str | None): GPU model name.
        gpu_vendor (str | None): Name of the GPU vendor.
        local_storage (str | None): Local storage presence.
        projects (list of ProjectRead): Projects having access to this flavor. The list
            is populated only if the flavor is a private one.
        services (list of ComputeServiceReadExtended): Compute Services exploiting this
            flavor.
    """

    is_shared: bool | None = Field(default=None, description=DOC_SHARED)

    projects: list[ProjectRead] = Field(default_factory=list, description=DOC_EXT_PROJ)
    services: list[ComputeServiceReadExtended] = Field(description=DOC_EXT_SERV)


class FlavorReadExtendedPublic(BaseNodeRead, BaseReadPublicExtended, FlavorBasePublic):
    """Model to extend the Flavor public data read from the DB.

    Attributes:
    ----------
        uid (str): Flavor unique ID.
        description (str): Brief description.
        name (str): Flavor name in the Provider.
        uuid (str): Flavor unique ID in the Provider
        projects (list of ProjectReadPublic): Projects having access to this flavor. The
            list is populated only if the flavor is a private one.
        services (list of ComputeServiceReadExtendedPublic): Compute Services exploiting
            this flavor.
    """

    projects: list[ProjectReadPublic] = Field(
        default_factory=list, description=DOC_EXT_PROJ
    )
    services: list[ComputeServiceReadExtendedPublic] = Field(description=DOC_EXT_SERV)


class FlavorReadSingle(BaseModel):
    __root__: (
        FlavorReadExtended | FlavorRead | FlavorReadExtendedPublic | FlavorReadPublic
    ) = Field(..., discriminator="schema_type")


class FlavorReadMulti(BaseModel):
    __root__: list[FlavorReadExtended] | list[FlavorRead] | list[
        FlavorReadExtendedPublic
    ] | list[FlavorReadPublic] = Field(..., discriminator="schema_type")
