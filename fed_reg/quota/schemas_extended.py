"""Pydantic extended models of the Resource limitations for Projects on Services."""

from pydantic import BaseModel, Field

from fed_reg.models import BaseNodeRead, BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.project.schemas import ProjectRead, ProjectReadPublic
from fed_reg.provider.schemas import ProviderRead, ProviderReadPublic
from fed_reg.quota.constants import DOC_EXT_PROJ, DOC_EXT_SERV
from fed_reg.quota.schemas import (
    BlockStorageQuotaBase,
    BlockStorageQuotaBasePublic,
    BlockStorageQuotaRead,
    BlockStorageQuotaReadPublic,
    ComputeQuotaBase,
    ComputeQuotaBasePublic,
    ComputeQuotaRead,
    ComputeQuotaReadPublic,
    NetworkQuotaBase,
    NetworkQuotaBasePublic,
    NetworkQuotaRead,
    NetworkQuotaReadPublic,
)
from fed_reg.region.constants import DOC_EXT_PROV
from fed_reg.region.schemas import RegionRead, RegionReadPublic
from fed_reg.service.constants import DOC_EXT_REG
from fed_reg.service.schemas import (
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    NetworkServiceRead,
    NetworkServiceReadPublic,
)


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


class BlockStorageServiceReadExtended(BlockStorageServiceRead):
    """Model to extend the Block Storage Service data read from the DB.

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


class BlockStorageServiceReadExtendedPublic(BlockStorageServiceReadPublic):
    """Model to extend the Block Storage Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadExtendedPublic): Region hosting this service.
    """

    region: RegionReadExtendedPublic = Field(description=DOC_EXT_REG)


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


class NetworkServiceReadExtended(NetworkServiceRead):
    """Model to extend the Network Service data read from the DB.

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


class NetworkServiceReadExtendedPublic(NetworkServiceReadPublic):
    """Model to extend the Network Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadExtendedPublic): Region hosting this service.
    """

    region: RegionReadExtendedPublic = Field(description=DOC_EXT_REG)


class BlockStorageQuotaReadExtended(
    BaseNodeRead, BaseReadPrivateExtended, BlockStorageQuotaBase
):
    """Model to extend the Block Storage Quota data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        gigabytes (int | None): Number of max usable gigabytes (GiB).
        per_volume_gigabytes (int | None): Number of max usable gigabytes per volume
            (GiB).
        volumes (int | None): Number of max volumes a user group can create.
        project (ProjectRead): Target project.
        service (BlockStorageServiceReadExtended): Target block storage service.
    """

    project: ProjectRead = Field(description=DOC_EXT_PROJ)
    service: BlockStorageServiceReadExtended = Field(description=DOC_EXT_SERV)


class BlockStorageQuotaReadExtendedPublic(
    BaseNodeRead, BaseReadPublicExtended, BlockStorageQuotaBasePublic
):
    """Model to extend the Block Storage Quota public data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        project (ProjectReadPublic): Target project.
        service (BlockStorageServiceReadExtendedPublic): Target block storage service.
    """

    project: ProjectReadPublic = Field(description=DOC_EXT_PROJ)
    service: BlockStorageServiceReadExtendedPublic = Field(description=DOC_EXT_SERV)


class ComputeQuotaReadExtended(BaseNodeRead, BaseReadPrivateExtended, ComputeQuotaBase):
    """Model to extend the Compute Quota data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instance (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
        project (ProjectRead): Target project.
        service (ComputeServiceReadExtended): Target compute service.
    """

    project: ProjectRead = Field(description=DOC_EXT_PROJ)
    service: ComputeServiceReadExtended = Field(description=DOC_EXT_SERV)


class ComputeQuotaReadExtendedPublic(
    BaseNodeRead, BaseReadPublicExtended, ComputeQuotaBasePublic
):
    """Model to extend the Compute Quota public data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        project (ProjectReadPublic): Target project.
        service (ComputeServiceReadExtendedPublic): Target compute service.
    """

    project: ProjectReadPublic = Field(description=DOC_EXT_PROJ)
    service: ComputeServiceReadExtendedPublic = Field(description=DOC_EXT_SERV)


class NetworkQuotaReadExtended(BaseNodeRead, BaseReadPrivateExtended, NetworkQuotaBase):
    """Model to extend the Network Quota data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        public_ips (int | None): The number of floating IP addresses allowed for each
            project.
        networks (int | None): The number of networks allowed for each project.
        port (int | None): The number of ports allowed for each project.
        security_groups (int | None): The number of security groups allowed for each
            project.
        security_group_rules (int | None): The number of security group rules allowed
            for each project.
        project (ProjectRead): Target project.
        service (NetworkServiceReadExtended): Target network service.
    """

    project: ProjectRead = Field(description=DOC_EXT_PROJ)
    service: NetworkServiceReadExtended = Field(description=DOC_EXT_SERV)


class NetworkQuotaReadExtendedPublic(
    BaseNodeRead, BaseReadPublicExtended, NetworkQuotaBasePublic
):
    """Model to extend the Network Quota public data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        project (ProjectReadPublic): Target project.
        service (NetworkServiceReadExtendedPublic): Target network service.
    """

    project: ProjectReadPublic = Field(description=DOC_EXT_PROJ)
    service: NetworkServiceReadExtendedPublic = Field(description=DOC_EXT_SERV)


class BlockStorageQuotaReadSingle(BaseModel):
    __root__: (
        BlockStorageQuotaReadExtended
        | BlockStorageQuotaRead
        | BlockStorageQuotaReadExtendedPublic
        | BlockStorageQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class BlockStorageQuotaReadMulti(BaseModel):
    __root__: list[BlockStorageQuotaReadExtended] | list[BlockStorageQuotaRead] | list[
        BlockStorageQuotaReadExtendedPublic
    ] | list[BlockStorageQuotaReadPublic] = Field(..., discriminator="schema_type")


class ComputeQuotaReadSingle(BaseModel):
    __root__: (
        ComputeQuotaReadExtended
        | ComputeQuotaRead
        | ComputeQuotaReadExtendedPublic
        | ComputeQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class ComputeQuotaReadMulti(BaseModel):
    __root__: list[ComputeQuotaReadExtended] | list[ComputeQuotaRead] | list[
        ComputeQuotaReadExtendedPublic
    ] | list[ComputeQuotaReadPublic] = Field(..., discriminator="schema_type")


class NetworkQuotaReadSingle(BaseModel):
    __root__: (
        NetworkQuotaReadExtended
        | NetworkQuotaRead
        | NetworkQuotaReadExtendedPublic
        | NetworkQuotaReadPublic
    ) = Field(..., discriminator="schema_type")


class NetworkQuotaReadMulti(BaseModel):
    __root__: list[NetworkQuotaReadExtended] | list[NetworkQuotaRead] | list[
        NetworkQuotaReadExtendedPublic
    ] | list[NetworkQuotaReadPublic] = Field(..., discriminator="schema_type")
