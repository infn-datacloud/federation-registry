"""Pydantic extended models of the Project owned by a Provider."""
from typing import List, Optional, Union

from pydantic import Field

from fed_reg.flavor.schemas import FlavorRead, FlavorReadPublic
from fed_reg.identity_provider.schemas import (
    IdentityProviderRead,
    IdentityProviderReadPublic,
)
from fed_reg.image.schemas import ImageRead, ImageReadPublic
from fed_reg.network.schemas import NetworkRead, NetworkReadPublic
from fed_reg.project.constants import (
    DOC_EXT_FLAV,
    DOC_EXT_IMAG,
    DOC_EXT_NETW,
    DOC_EXT_PROV,
    DOC_EXT_QUOTA,
    DOC_EXT_SLA,
)
from fed_reg.project.models import Project
from fed_reg.project.schemas import ProjectRead, ProjectReadPublic
from fed_reg.provider.schemas import ProviderRead, ProviderReadPublic
from fed_reg.quota.constants import DOC_EXT_SERV
from fed_reg.quota.schemas import (
    BlockStorageQuotaRead,
    BlockStorageQuotaReadPublic,
    ComputeQuotaRead,
    ComputeQuotaReadPublic,
    NetworkQuotaRead,
    NetworkQuotaReadPublic,
)
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
from fed_reg.sla.constants import DOC_EXT_GROUP
from fed_reg.sla.schemas import SLARead, SLAReadPublic
from fed_reg.user_group.constants import DOC_EXT_IDP
from fed_reg.user_group.schemas import UserGroupRead, UserGroupReadPublic


class BlockStorageServiceReadExtended(BlockStorageServiceRead):
    """Model to extend the Block Storage Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        region (RegionRead): Region hosting this service.
    """

    region: RegionRead = Field(description=DOC_EXT_REG)


class BlockStorageServiceReadExtendedPublic(BlockStorageServiceReadPublic):
    """Model to extend the Block Storage Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadPublic): Region hosting this service.
    """

    region: RegionReadPublic = Field(description=DOC_EXT_REG)


class ComputeServiceReadExtended(ComputeServiceRead):
    """Model to extend the Compute Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        region (RegionRead): Region hosting this service.
    """

    region: RegionRead = Field(description=DOC_EXT_REG)


class ComputeServiceReadExtendedPublic(ComputeServiceReadPublic):
    """Model to extend the Compute Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadPublic): Region hosting this service.
    """

    region: RegionReadPublic = Field(description=DOC_EXT_REG)


class NetworkServiceReadExtended(NetworkServiceRead):
    """Model to extend the Network Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        region (RegionRead): Region hosting this service.
    """

    region: RegionRead = Field(description=DOC_EXT_REG)


class NetworkServiceReadExtendedPublic(NetworkServiceReadPublic):
    """Model to extend the Network Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadPublic): Region hosting this service.
    """

    region: RegionReadPublic = Field(description=DOC_EXT_REG)


class BlockStorageQuotaReadExtended(BlockStorageQuotaRead):
    """Model to extend the Block Storage Quota data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        gigabytes (int | None): Number of max usable gigabytes (GiB).
        per_volume_gigabytes (int | None): Number of max usable gigabytes per volume
            (GiB).
        volumes (int | None): Number of max volumes a user group can create.
        service (BlockStorageServiceReadExtended): Target service. Same type of quota.
    """

    service: BlockStorageServiceReadExtended = Field(description=DOC_EXT_SERV)


class BlockStorageQuotaReadExtendedPublic(BlockStorageQuotaReadPublic):
    """Model to extend the Block Storage Quota public data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        service (BlockStorageServiceReadExtendedPublic): Target service. Same type of
            quota.
    """

    service: BlockStorageServiceReadExtendedPublic = Field(description=DOC_EXT_SERV)


class ComputeQuotaReadExtended(ComputeQuotaRead):
    """Model to extend the Compute Quota data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        cores (int | None): Number of max usable cores.
        instance (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
        service (ComputeServiceReadExtended): Target service. Same type of quota.
    """

    service: ComputeServiceReadExtended = Field(description=DOC_EXT_SERV)


class ComputeQuotaReadExtendedPublic(ComputeQuotaReadPublic):
    """Model to extend the Compute Quota public data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        service (ComputeServiceReadExtendedPublic): Target service. Same type of quota.
    """

    service: ComputeServiceReadExtendedPublic = Field(description=DOC_EXT_SERV)


class NetworkQuotaReadExtended(NetworkQuotaRead):
    """Model to extend the Network Quota data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        public_ips (int | None): The number of floating IP addresses allowed for each
            project.
        networks (int | None): The number of networks allowed for each project.
        port (int | None): The number of ports allowed for each project.
        security_groups (int | None): The number of security groups allowed for each
            project.
        security_group_rules (int | None): The number of security group rules allowed
            for each project.
        service (NetworkServiceReadExtended): Target service. Same type of quota.
    """

    service: NetworkServiceReadExtended = Field(description=DOC_EXT_SERV)


class NetworkQuotaReadExtendedPublic(NetworkQuotaReadPublic):
    """Model to extend the Network Quota public data read from the DB.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        service (NetworkServiceReadExtendedPublic): Target service. Same type of quota.
    """

    service: NetworkServiceReadExtendedPublic = Field(description=DOC_EXT_SERV)


class UserGroupReadExtended(UserGroupRead):
    """Model to extend the User Group data read from the DB.

    Attributes:
    ----------
        uid (int): User Group unique ID.
        description (str): Brief description.
        name (str): User Group name.
        identity_provider (IdentityProviderRead): Identity provider owning this user
            group.
    """

    identity_provider: IdentityProviderRead = Field(description=DOC_EXT_IDP)


class UserGroupReadExtendedPublic(UserGroupReadPublic):
    """Model to extend the User Group public data read from the DB.

    Attributes:
    ----------
        uid (int): User Group unique ID.
        description (str): Brief description.
        name (str): User Group name.
        identity_provider (IdentityProviderReadPublic): Identity provider owning this
            user group.
    """

    identity_provider: IdentityProviderReadPublic = Field(description=DOC_EXT_IDP)


class SLAReadExtended(SLARead):
    """Model to extend the SLA data read from the DB.

    Attributes:
    ----------
        uid (int): SLA unique ID.
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
        user_group (UserGroupReadExtended): Target user group.
    """

    user_group: UserGroupReadExtended = Field(description=DOC_EXT_GROUP)


class SLAReadExtendedPublic(SLAReadPublic):
    """Model to extend the SLA public data read from the DB.

    Attributes:
    ----------
        uid (int): SLA unique ID.
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
        user_group (UserGroupReadExtendedPublic): Target user group.
    """

    user_group: UserGroupReadExtendedPublic = Field(description=DOC_EXT_GROUP)


class ProjectReadExtended(ProjectRead):
    """Model to extend the Project data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedProject unique ID.
        description (str): Brief description.
        name (str): Name of the project in the Provider.
        uuid (uuid): Project Unique ID in the Provider.
        provider (ProviderRead): Provider owning this project.
        sla (SLAReadExtended | None): SLA pointing to this project.
        flavors (list of FlavorRead): Private and public accessible flavors.
        images (list of ImageRead): Private and public accessible images.
        networks (list of NetworkRead): Private and public accessible networks.
        quotas (list of Quota): List of owned quotas pointing to the corresponding
            service (block-storage, compute and network type).
    """

    flavors: List[FlavorRead] = Field(description=DOC_EXT_FLAV)
    images: List[ImageRead] = Field(description=DOC_EXT_IMAG)
    networks: List[NetworkRead] = Field(description=DOC_EXT_NETW)
    provider: ProviderRead = Field(description=DOC_EXT_PROV)
    quotas: List[
        Union[
            ComputeQuotaReadExtended,
            BlockStorageQuotaReadExtended,
            NetworkQuotaReadExtended,
        ]
    ] = Field(description=DOC_EXT_QUOTA)
    sla: Optional[SLAReadExtended] = Field(default=None, description=DOC_EXT_SLA)

    @classmethod
    def from_orm(cls, obj: Project) -> "ProjectReadExtended":
        """Method to merge public and private flavors, images and networks.

        `obj` is the orm model instance.
        """
        obj.flavors = obj.public_flavors() + obj.private_flavors.all()
        obj.images = obj.public_images() + obj.private_images.all()
        obj.networks = obj.public_networks() + obj.private_networks.all()
        return super().from_orm(obj)


class ProjectReadExtendedPublic(ProjectReadPublic):
    """Model to extend the Project public data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedProject unique ID.
        description (str): Brief description.
        name (str): Name of the project in the Provider.
        uuid (uuid): Project Unique ID in the Provider.
        provider (ProviderReadPublic): Provider owning this project.
        sla (SLAReadExtendedPublic | None): SLA pointing to this project.
        flavors (list of FlavorReadPublic): Private and public accessible flavors.
        images (list of ImageReadPublic): Private and public accessible images.
        networks (list of NetworkReadPublic): Private and public accessible networks.
        quotas (list of QuotaPublic): List of owned quotas pointing to the corresponding
            service (block-storage, compute and network type).
    """

    flavors: List[FlavorReadPublic] = Field(description=DOC_EXT_FLAV)
    images: List[ImageReadPublic] = Field(description=DOC_EXT_IMAG)
    networks: List[NetworkReadPublic] = Field(description=DOC_EXT_NETW)
    provider: ProviderReadPublic = Field(description=DOC_EXT_PROV)
    quotas: List[
        Union[
            ComputeQuotaReadExtendedPublic,
            BlockStorageQuotaReadExtendedPublic,
            NetworkQuotaReadExtendedPublic,
        ]
    ] = Field(description=DOC_EXT_QUOTA)
    sla: Optional[SLAReadExtendedPublic] = Field(default=None, description=DOC_EXT_SLA)

    @classmethod
    def from_orm(cls, obj: Project) -> "ProjectReadExtended":
        """Method to merge public and private flavors, images and networks.

        `obj` is the orm model instance.
        """
        obj.flavors = obj.public_flavors() + obj.private_flavors.all()
        obj.images = obj.public_images() + obj.private_images.all()
        obj.networks = obj.public_networks() + obj.private_networks.all()
        return super().from_orm(obj)
