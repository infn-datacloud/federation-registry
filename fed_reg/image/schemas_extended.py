"""Pydantic models of the Virtual Machine Image owned by a Provider."""
from typing import List

from pydantic import Field

from fed_reg.image.constants import DOC_EXT_PROJ, DOC_EXT_SERV
from fed_reg.image.schemas import ImageRead, ImageReadPublic
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
        provider (ProviderRead): Provider hosting target region.
    """

    provider: ProviderRead = Field(description=DOC_EXT_PROV)


class RegionReadExtendedPublic(RegionReadPublic):
    """Model to extend the Region public data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        provider (ProviderReadPublic): Provider hosting target region.
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


class ImageReadExtended(ImageRead):
    """Model to extend the Image data read from the DB.

    Attributes:
    ----------
        uid (int): Image unique ID.
        description (str): Brief description.
        name (str): Image name in the Provider.
        uuid (str): Image unique ID in the Provider
        os_type (str | None): OS type.
        os_distro (str | None): OS distribution.
        os_version (str | None): Distribution version.
        architecture (str | None): OS architecture.
        kernel_id (str | None): Kernel version.
        cuda_support (str): Support for cuda enabled.
        gpu_driver (str): Support for GPUs drivers.
        is_public (bool): Public or private Image.
        tags (list of str): List of tags associated to this Image.
        projects (list of ProjectRead): Projects having access to this flavor. The list
            is populated only if the flavor is a private one.
        services (list of ComputeServiceReadExtended): Compute Services exploiting this
            flavor.
    """

    projects: List[ProjectRead] = Field(description=DOC_EXT_PROJ)
    services: List[ComputeServiceReadExtended] = Field(description=DOC_EXT_SERV)


class ImageReadExtendedPublic(ImageReadPublic):
    """Model to extend the Image public data read from the DB.

    Attributes:
    ----------
        uid (int): Image unique ID.
        description (str): Brief description.
        name (str): Image name in the Provider.
        uuid (str): Image unique ID in the Provider
        projects (list of ProjectReadPublic): Projects having access to this flavor. The
            list is populated only if the flavor is a private one.
        services (list of ComputeServiceReadExtendedPublic): Compute Services exploiting
            this flavor.
    """

    projects: List[ProjectReadPublic] = Field(description=DOC_EXT_PROJ)
    services: List[ComputeServiceReadExtendedPublic] = Field(description=DOC_EXT_SERV)
