"""Pydantic extended models of the Resource Provider (openstack, kubernetes...)."""

from typing import Any, Dict, Optional, Set

from pydantic import BaseModel, Field, root_validator, validator

from fed_reg.auth_method.schemas import AuthMethodCreate, AuthMethodRead
from fed_reg.flavor.schemas import FlavorCreate, FlavorRead, FlavorReadPublic
from fed_reg.identity_provider.constants import DOC_EXT_GROUP
from fed_reg.identity_provider.schemas import (
    IdentityProviderCreate,
    IdentityProviderRead,
    IdentityProviderReadPublic,
)
from fed_reg.image.schemas import ImageCreate, ImageRead, ImageReadPublic
from fed_reg.location.schemas import (
    LocationCreate,
    LocationRead,
    LocationReadPublic,
)
from fed_reg.models import BaseNodeRead, BaseReadPrivateExtended, BaseReadPublicExtended
from fed_reg.network.schemas import NetworkCreate, NetworkRead, NetworkReadPublic
from fed_reg.project.schemas import ProjectCreate, ProjectRead, ProjectReadPublic
from fed_reg.provider.constants import (
    DOC_EXT_AUTH_METH,
    DOC_EXT_IDP,
    DOC_EXT_PROJ,
    DOC_EXT_REG,
    DOC_NEW_GROUP,
    DOC_NEW_PROJ_UUID,
    DOC_NEW_PROJ_UUIDS,
    DOC_NEW_SERV_BLO_STO,
    DOC_NEW_SERV_COMP,
    DOC_NEW_SERV_ID,
    DOC_NEW_SERV_NET,
)
from fed_reg.provider.schemas import (
    ProviderBase,
    ProviderBasePublic,
    ProviderCreate,
    ProviderRead,
    ProviderReadPublic,
)
from fed_reg.quota.schemas import (
    BlockStorageQuotaCreate,
    BlockStorageQuotaRead,
    BlockStorageQuotaReadPublic,
    ComputeQuotaCreate,
    ComputeQuotaRead,
    ComputeQuotaReadPublic,
    NetworkQuotaCreate,
    NetworkQuotaRead,
    NetworkQuotaReadPublic,
    ObjectStoreQuotaCreate,
    ObjectStoreQuotaRead,
    ObjectStoreQuotaReadPublic,
)
from fed_reg.region.constants import DOC_EXT_LOC, DOC_EXT_SERV
from fed_reg.region.schemas import RegionCreate, RegionRead, RegionReadPublic
from fed_reg.service.constants import (
    DOC_EXT_FLAV,
    DOC_EXT_IMAG,
    DOC_EXT_NETW,
    DOC_EXT_QUOTA,
)
from fed_reg.service.schemas import (
    BlockStorageServiceCreate,
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    ComputeServiceCreate,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    IdentityServiceCreate,
    IdentityServiceRead,
    IdentityServiceReadPublic,
    NetworkServiceCreate,
    NetworkServiceRead,
    NetworkServiceReadPublic,
    ObjectStoreServiceCreate,
    ObjectStoreServiceRead,
    ObjectStoreServiceReadPublic,
)
from fed_reg.sla.schemas import SLACreate, SLARead, SLAReadPublic
from fed_reg.user_group.constants import DOC_EXT_SLA
from fed_reg.user_group.schemas import (
    UserGroupCreate,
    UserGroupRead,
    UserGroupReadPublic,
)


class UserGroupReadExtended(UserGroupRead):
    """Model to extend the User Group data read from the DB.

    Attributes:
    ----------
        uid (int): User Group unique ID.
        description (str): Brief description.
        name (str): User Group name.
        slas (list of SLARead): Owned SLAs.
    """

    slas: list[SLARead] = Field(default_factory=list, description=DOC_EXT_SLA)


class UserGroupReadExtendedPublic(UserGroupReadPublic):
    """Model to extend the User Group public data read from the DB.

    Attributes:
    ----------
        uid (int): User Group unique ID.
        description (str): Brief description.
        name (str): User Group name.
        slas (list of SLARead): Owned SLAs.
    """

    slas: list[SLAReadPublic] = Field(default_factory=list, description=DOC_EXT_SLA)


class IdentityProviderReadExtended(IdentityProviderRead):
    """Model to extend the Identity Provider data read from the DB.

    Attributes:
    ----------
        uid (int): Identity Provider unique ID.
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        group_claim (str): value of the key from which retrieve
            the user group name from an authentication token.
        relationship (AuthMethodRead): Authentication method used by the target
            provider to connect.
        user_groups (list of UserGroupReadExtended): Owned user groups.
    """

    relationship: AuthMethodRead = Field(description=DOC_EXT_AUTH_METH)
    user_groups: list[UserGroupReadExtended] = Field(
        default_factory=list, description=DOC_EXT_GROUP
    )


class IdentityProviderReadExtendedPublic(IdentityProviderReadPublic):
    """Model to extend the Identity Provider public data read from the DB.

    Attributes:
    ----------
        uid (int): Identity Provider unique ID.
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        relationship (AuthMethodRead): Authentication method used by the target
            provider to connect.
        user_groups (list of UserGroupReadExtendedPublic): Owned user groups.
    """

    relationship: AuthMethodRead = Field(description=DOC_EXT_AUTH_METH)
    user_groups: list[UserGroupReadExtendedPublic] = Field(
        default_factory=list, description=DOC_EXT_GROUP
    )


class BlockStorageServiceReadExtended(BlockStorageServiceRead):
    """Model to extend the Block Storage Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        quotas (list of BlockStorageQuotaReadExtended): Quotas pointing to this service.
    """

    quotas: list[BlockStorageQuotaRead] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class BlockStorageServiceReadExtendedPublic(BlockStorageServiceReadPublic):
    """Model to extend the Block Storage Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadExtendedPublic): Region hosting this service.
        quotas (list of BlockStorageQuotaReadExtendedPublic): Quotas pointing to this
            service.
    """

    quotas: list[BlockStorageQuotaReadPublic] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class ComputeServiceReadExtended(ComputeServiceRead):
    """Model to extend the Compute Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        flavors (list of FlavorRead): Supplied flavors.
        images (list of ImageRead): Supplied images.
        quotas (list of ComputeQuotaReadExtended): Quotas pointing to this service.
    """

    flavors: list[FlavorRead] = Field(default_factory=list, description=DOC_EXT_FLAV)
    images: list[ImageRead] = Field(default_factory=list, description=DOC_EXT_IMAG)
    quotas: list[ComputeQuotaRead] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class ComputeServiceReadExtendedPublic(ComputeServiceReadPublic):
    """Model to extend the Compute Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        flavors (list of FlavorReadPublic): Supplied flavors.
        images (list of ImageReadPublic): Supplied images.
        quotas (list of ComputeQuotaReadExtendedPublic): Quotas pointing to this
            service.
    """

    flavors: list[FlavorReadPublic] = Field(
        default_factory=list, description=DOC_EXT_FLAV
    )
    images: list[ImageReadPublic] = Field(
        default_factory=list, description=DOC_EXT_IMAG
    )
    quotas: list[ComputeQuotaReadPublic] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class NetworkServiceReadExtended(NetworkServiceRead):
    """Model to extend the Network Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        networks (list of NetworkRead): Supplied networks.
        quotas (list of NetworkQuotaReadExtended): Quotas pointing to this
            service.
    """

    networks: list[NetworkRead] = Field(default_factory=list, description=DOC_EXT_NETW)
    quotas: list[NetworkQuotaRead] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class NetworkServiceReadExtendedPublic(NetworkServiceReadPublic):
    """Model to extend the Network Service public data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        networks (list of NetworkReadPublic): Supplied networks.
        quotas (list of NetworkQuotaReadExtendedPublic): Quotas pointing to this
            service.
    """

    networks: list[NetworkReadPublic] = Field(
        default_factory=list, description=DOC_EXT_NETW
    )
    quotas: list[NetworkQuotaReadPublic] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class ObjectStoreServiceReadExtended(ObjectStoreServiceRead):
    """Model to extend the Object Storage Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name.
        quotas (list of ObjectStoreQuotaReadExtended): Quotas pointing to this
            service.
    """

    quotas: list[ObjectStoreQuotaRead] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class ObjectStoreServiceReadExtendedPublic(ObjectStoreServiceReadPublic):
    """Model to extend the Object Storage Service data read from the DB.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        region (RegionReadExtendedPublic): Region hosting this service.
        quotas (list of ObjectStoreQuotaReadExtendedPublic): Quotas pointing to this
            service.
    """

    quotas: list[ObjectStoreQuotaReadPublic] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )


class RegionReadExtended(RegionRead):
    """Model to extend the Region data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        overbooking_cpu (float): CPU overbooking factor.
        overbooking_ram (float): RAM overbooking factor.
        bandwidth_in (float): Bandwidth in.
        bandwidth_out (float): Bandwidth out.
        location (LocationRead | None): Location hosting this region.
        services (list of Service): Supplied services (block-storage, compute, identity
            and network type).
    """

    location: Optional[LocationRead] = Field(default=None, description=DOC_EXT_LOC)
    services: list[
        BlockStorageServiceReadExtended
        | ComputeServiceReadExtended
        | IdentityServiceRead
        | NetworkServiceReadExtended
        | ObjectStoreServiceReadExtended
    ] = Field(default_factory=list, description=DOC_EXT_SERV)


class RegionReadExtendedPublic(RegionReadPublic):
    """Model to extend the Region public data read from the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        location (LocationReadPublic | None): Location hosting this region.
        services (list of ServicePublic): Supplied services (block-storage, compute,
            identity and network type).
    """

    location: Optional[LocationReadPublic] = Field(
        default=None, description=DOC_EXT_LOC
    )
    services: list[
        BlockStorageServiceReadExtendedPublic
        | ComputeServiceReadExtendedPublic
        | IdentityServiceReadPublic
        | NetworkServiceReadExtendedPublic
        | ObjectStoreServiceReadExtendedPublic
    ] = Field(default_factory=list, description=DOC_EXT_SERV)


class ProviderReadExtended(BaseNodeRead, BaseReadPrivateExtended, ProviderBase):
    """Model to extend the Provider data read from the DB.

    Attributes:
    ----------
        uid (int): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): list of maintainers emails.
        overbooking_cpu (float): CPU overbooking factor.
        overbooking_ram (float): RAM overbooking factor.
        bandwidth_in (float): Bandwidth in.
        bandwidth_out (float): Bandwidth out.
        identity_providers (list of IdentityProviderReadExtended): Supported identity
            providers.
        projects (list of ProjectRead): Supplied projects.
        regions (list of RegionReadExtended): Supplied regions.
    """

    identity_providers: list[IdentityProviderReadExtended] = Field(
        description=DOC_EXT_IDP
    )
    projects: list[ProjectRead] = Field(description=DOC_EXT_PROJ)
    regions: list[RegionReadExtended] = Field(description=DOC_EXT_REG)


class ProviderReadExtendedPublic(
    BaseNodeRead, BaseReadPublicExtended, ProviderBasePublic
):
    """Model to extend the Provider public data read from the DB.

    Attributes:
    ----------
        uid (int): Provider unique ID.
        description (str): Brief description.
        name (str): Provider name.
        identity_providers (list of IdentityProviderReadExtendedPublic): Supported
            identity providers.
        projects (list of ProjectReadPublic): Supplied projects.
        projects (list of RegionReadExtendedPublic): Supplied regions.
    """

    identity_providers: list[IdentityProviderReadExtendedPublic] = Field(
        description=DOC_EXT_IDP
    )
    projects: list[ProjectReadPublic] = Field(description=DOC_EXT_PROJ)
    regions: list[RegionReadExtendedPublic] = Field(description=DOC_EXT_REG)


class ProviderReadSingle(BaseModel):
    __root__: (
        ProviderReadExtended
        | ProviderRead
        | ProviderReadExtendedPublic
        | ProviderReadPublic
    ) = Field(..., discriminator="schema_type")


class ProviderReadMulti(BaseModel):
    __root__: (
        list[ProviderReadExtended]
        | list[ProviderRead]
        | list[ProviderReadExtendedPublic]
        | list[ProviderReadPublic]
    ) = Field(..., discriminator="schema_type")


# CREATE CLASSES


def find_duplicates(items: Any, attr: Optional[str] = None) -> None:
    """Find duplicate items in a list.

    Optionally filter items by attribute
    """
    if attr:
        values = [j.__getattribute__(attr) for j in items]
    else:
        values = items
    seen = set()
    dupes = [x for x in values if x in seen or seen.add(x)]
    if attr:
        assert (
            len(dupes) == 0
        ), f"There are multiple items with identical {attr}: {','.join(dupes)}"
    else:
        assert len(dupes) == 0, f"There are multiple identical items: {','.join(dupes)}"


def multiple_quotas_same_project(quotas: list[Any]) -> None:
    """Verify maximum number of quotas on same project.

    A project can have at most one `project` quota, one `per-user` quota and one `usage`
    quota on a specific service.
    """
    d = {}
    for quota in quotas:
        if quota.project is not None:
            msg = f"Multiple quotas on same project {quota.project}"
            if not d.get(quota.project, None):
                d[quota.project] = [0, 0, 0]
            if quota.usage:
                d[quota.project][2] += 1
            elif quota.per_user:
                d[quota.project][1] += 1
            else:
                d[quota.project][0] += 1
            assert (
                d[quota.project][0] < 2
                and d[quota.project][1] < 2
                and d[quota.project][2] < 2
            ), msg


def find_duplicate_projects(project: str, seen: Set[str]) -> None:
    msg = f"Project {project} already used by another SLA"
    assert project not in seen, msg
    seen.add(project)


def find_duplicate_slas(doc_uuid: str, seen: Set[str]) -> None:
    msg = f"SLA {doc_uuid} already used by another user group"
    assert doc_uuid not in seen, msg
    seen.add(doc_uuid)


def proj_in_provider(
    project: Optional[str], projects: list[str], *, parent: str
) -> None:
    """Verify project is in projects list."""
    if project:
        msg = f"{parent}'s project {project} "
        msg += f"not in this provider: {projects}"
        assert project in projects, msg


class SLACreateExtended(SLACreate):
    """Model to extend the SLA data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
        project (str): Target project's UUID in the Provider.
    """

    project: str = Field(description=DOC_NEW_PROJ_UUID)


class UserGroupCreateExtended(UserGroupCreate):
    """Model to extend the User Group data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): User Group name in the Identity Provider.
        sla (SLACreateExtended): SLA owned by this project and related to this provider.
    """

    sla: SLACreateExtended = Field(description="SLA related to this provider")


class IdentityProviderCreateExtended(IdentityProviderCreate):
    """Model to extend the Identity Provider data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the Identity Provider.
        group_claim (str): Value of the key from which retrieve the user group name from
            an authentication token.
        relationship (AuthMethodCreate): Authentication method used to connect to the
            target identity provider.
        user_groups (list of UserGroupCreateExtended): Owned user groups.
    """

    relationship: AuthMethodCreate = Field(description=DOC_EXT_AUTH_METH)
    user_groups: list[UserGroupCreateExtended] = Field(description=DOC_NEW_GROUP)

    @validator("user_groups")
    @classmethod
    def validate_user_groups(
        cls, v: list[UserGroupCreateExtended]
    ) -> list[UserGroupCreateExtended]:
        """Check user group list content.

        Verify the list is not empty and there are no duplicates.
        Check that an SLA is not used by multiple user groups of the same IDP.
        """
        assert len(v), "Identity provider's user group list can't be empty"
        find_duplicates(v, "name")
        seen_slas = set()
        seen_projects = set()
        for user_group in v:
            find_duplicate_slas(user_group.sla.doc_uuid, seen_slas)
            find_duplicate_projects(user_group.sla.project, seen_projects)
        return v


class BlockStorageQuotaCreateExtended(BlockStorageQuotaCreate):
    """Model to extend the Block Storage Quota data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        gigabytes (int | None): Number of max usable gigabytes (GiB).
        per_volume_gigabytes (int | None): Number of max usable gigabytes per volume
            (GiB).
        volumes (int | None): Number of max volumes a user group can create.
        project (str): Target project's UUID in the Provider.
    """

    project: str = Field(description=DOC_NEW_PROJ_UUID)


class ComputeQuotaCreateExtended(ComputeQuotaCreate):
    """Model to extend the Compute Quota data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instances (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
        project (str): Target project's UUID in the Provider.
    """

    project: str = Field(description=DOC_NEW_PROJ_UUID)


class NetworkQuotaCreateExtended(NetworkQuotaCreate):
    """Model to extend the Network Quota data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        public_ips (int | None): The number of floating IP addresses allowed for each
            project.
        networks (int | None): The number of networks allowed for each project.
        ports (int | None): The number of ports allowed for each project.
        security_groups (int | None): The number of security groups allowed for each
            project.
        security_group_rules (int | None): The number of security group rules allowed
            for each project.
        project (str): Target project's UUID in the Provider.
    """

    project: str = Field(description=DOC_NEW_PROJ_UUID)


class ObjectStoreQuotaCreateExtended(ObjectStoreQuotaCreate):
    """Model to extend the Object Storage Quota data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        bytes (int): Maximum number of allowed bytes.
        containers (int): Maximum number of allowed containers.
        objects (int): Maximum number of allowed objects.
        project (str): Target project's UUID in the Provider.
    """

    project: str = Field(description=DOC_NEW_PROJ_UUID)


class FlavorCreateExtended(FlavorCreate):
    """Model to extend the Flavor data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Flavor name in the Provider.
        uuid (str): Flavor unique ID in the Provider
        disk (int): Reserved disk size (GiB)
        is_public (bool): Public or private Flavor.
        ram (int): Reserved RAM (MiB)
        vcpus (int): Number of Virtual CPUs.
        swap (int): Swap size (GiB).
        ephemeral (int): Ephemeral disk size (GiB).
        infiniband (bool): MPI - parallel multi-process enabled.
        gpus (int): Number of GPUs.
        gpu_model (str | None): GPU model name.
        gpu_vendor (str | None): Name of the GPU vendor.
        local_storage (str | None): Local storage presence.
        projects (list of str): list of project' UUIDs in the Provider having access to
            the resource.
    """

    projects: list[str] = Field(default_factory=list, description=DOC_NEW_PROJ_UUIDS)

    @validator("projects")
    @classmethod
    def validate_projects(cls, v: list[str]) -> list[str]:
        """Cast to string possible UUIDs and verify there are no duplicate values."""
        find_duplicates(v)
        return v

    @root_validator
    def project_require_if_private_flavor(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify list emptiness based on flavor type.

        If public verify the projects list is empty, otherwise the list can't be empty.
        """
        if not values.get("is_public"):
            assert len(
                values.get("projects", [])
            ), "Projects are mandatory for private flavors"
        else:
            assert not len(
                values.get("projects", [])
            ), "Public flavors do not have linked projects"
        return values


class ImageCreateExtended(ImageCreate):
    """Model to extend the Image data to add to the DB.

    Attributes:
    ----------
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
        tags (list of str): list of tags associated to this Image.
        projects (list of str): list of project' UUIDs in the Provider having access to
            the resource.
    """

    projects: list[str] = Field(default_factory=list, description=DOC_NEW_PROJ_UUIDS)

    @validator("projects")
    @classmethod
    def validate_projects(cls, v: list[str]) -> str:
        """Cast to string possible UUIDs and verify there are no duplicate values."""
        find_duplicates(v)
        return v

    @root_validator
    def project_require_if_private_image(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Verify list emptiness based on image type.

        If public verify the projects list is empty, otherwise the list can't be empty.
        """
        if not values.get("is_public"):
            assert len(
                values.get("projects", [])
            ), "Projects are mandatory for private images"
        else:
            assert not len(
                values.get("projects", [])
            ), "Public images do not have linked projects"
        return values


class NetworkCreateExtended(NetworkCreate):
    """Model to extend the Network data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Network name in the Provider.
        uuid (str): Network unique ID in the Provider
        is_shared (bool): Public or private Network.
        is_router_external (bool): Network with access to outside networks. Externa
            network.
        is_default (bool): Network to use as default.
        mtu (int | None): Metric transmission unit (B).
        proxy_host (str | None): Proxy IP address.
        proxy_user (str | None): Proxy username.
        tags (list of str): list of tags associated to this Network.
        project (str | None): Target project's UUID in the Provider.
    """

    project: Optional[str] = Field(default=None, description=DOC_NEW_PROJ_UUID)

    @root_validator
    def project_require_if_private_net(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Verify target project is defined based on network type.

        If shared verify the project is None, otherwise the project must be defined.
        """
        if not values.get("is_shared"):
            assert (
                values.get("project") is not None
            ), "Projects is mandatory for private networks"
        else:
            assert not values.get(
                "project"
            ), "Shared networks do not have a linked project"
        return values


class BlockStorageServiceCreateExtended(BlockStorageServiceCreate):
    """Model to extend the Block Storage Service data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
        quotas (list of BlockStorageQuotaCreateExtended): Quotas pointing to this
            service.
    """

    quotas: list[BlockStorageQuotaCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )

    @validator("quotas")
    @classmethod
    def max_two_quotas_on_same_project(
        cls, v: list[BlockStorageQuotaCreateExtended]
    ) -> list[BlockStorageQuotaCreateExtended]:
        """Verify maximum number of quotas on same project."""
        multiple_quotas_same_project(v)
        return v


class ComputeServiceCreateExtended(ComputeServiceCreate):
    """Model to extend the Compute Service data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
        quotas (list of ComputeQuotaCreateExtended): Quotas pointing to this service.
        flavors (list of FlavorRead): Supplied flavors.
        images (list of ImageRead): Supplied images.
    """

    flavors: list[FlavorCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_FLAV
    )
    images: list[ImageCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_IMAG
    )
    quotas: list[ComputeQuotaCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )

    @validator("flavors", "images")
    @classmethod
    def no_duplicate_uuid_in_flavors_and_images(
        cls, v: list[FlavorCreateExtended] | list[ImageCreateExtended]
    ) -> list[FlavorCreateExtended] | list[ImageCreateExtended]:
        """Verify there are no duplicated names or UUIDs in the flavor list."""
        find_duplicates(v, "uuid")
        return v

    @validator("quotas")
    @classmethod
    def max_two_quotas_on_same_project(
        cls, v: list[ComputeQuotaCreateExtended]
    ) -> list[ComputeQuotaCreateExtended]:
        """Verify maximum number of quotas on same project."""
        multiple_quotas_same_project(v)
        return v


class NetworkServiceCreateExtended(NetworkServiceCreate):
    """Model to extend the Network Service data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
        quotas (list of NetworkQuotaCreateExtended): Quotas pointing to this service.
        networks (list of NetworkRead): Supplied networks.
    """

    networks: list[NetworkCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_NETW
    )
    quotas: list[NetworkQuotaCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )

    @validator("networks")
    @classmethod
    def validate_networks(
        cls, v: list[NetworkCreateExtended]
    ) -> list[NetworkCreateExtended]:
        """Verify there are no duplicated UUIDs in the network list."""
        find_duplicates(v, "uuid")
        return v

    @validator("quotas")
    @classmethod
    def max_two_quotas_on_same_project(
        cls, v: list[NetworkQuotaCreateExtended]
    ) -> list[NetworkQuotaCreateExtended]:
        """Verify maximum number of quotas on same project."""
        multiple_quotas_same_project(v)
        return v


class ObjectStoreServiceCreateExtended(ObjectStoreServiceCreate):
    """Model to extend the Object Storage Service data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
        quotas (list of ObjectStoreQuotaCreateExtended): Quotas pointing to this
            service.
    """

    quotas: list[ObjectStoreQuotaCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_QUOTA
    )

    @validator("quotas")
    @classmethod
    def max_two_quotas_on_same_project(
        cls, v: list[ObjectStoreQuotaCreateExtended]
    ) -> list[ObjectStoreQuotaCreateExtended]:
        """Verify maximum number of quotas on same project."""
        multiple_quotas_same_project(v)
        return v


class RegionCreateExtended(RegionCreate):
    """Model to extend the Region data to add to the DB.

    Attributes:
    ----------
        uid (uuid): AssociatedRegion unique ID.
        description (str): Brief description.
        name (str): Name of the Region in the Provider.
        overbooking_cpu (float): CPU overbooking factor.
        overbooking_ram (float): RAM overbooking factor.
        bandwidth_in (float): Bandwidth in.
        bandwidth_out (float): Bandwidth out.
        provider (ProviderRead): Provider hosting this region.
        location (LocationRead | None): Location hosting this region.
        block_storage_services (list of BlockStorageServiceCreateExtended): Supplied
            block storage services.
        compute_services (list of ComputeServiceCreateExtended): Supplied compute
            services.
        identity_services (list of IdentityServiceCreateExtended): Supplied identity
            services.
        network_services (list of NetworkServiceCreateExtended): Supplied network
            services.
        object_store_services (list of ObjectStoreServiceCreateExtended): Supplied
            object storage services.
    """

    location: Optional[LocationCreate] = Field(default=None, description=DOC_EXT_LOC)
    block_storage_services: list[BlockStorageServiceCreateExtended] = Field(
        default_factory=list, description=DOC_NEW_SERV_BLO_STO
    )
    compute_services: list[ComputeServiceCreateExtended] = Field(
        default_factory=list, description=DOC_NEW_SERV_COMP
    )
    identity_services: list[IdentityServiceCreate] = Field(
        default_factory=list, description=DOC_NEW_SERV_ID
    )
    network_services: list[NetworkServiceCreateExtended] = Field(
        default_factory=list, description=DOC_NEW_SERV_NET
    )
    object_store_services: list[ObjectStoreServiceCreateExtended] = Field(
        default_factory=list, description=DOC_NEW_SERV_BLO_STO
    )

    @validator(
        "block_storage_services",
        "compute_services",
        "identity_services",
        "network_services",
        "object_store_services",
    )
    @classmethod
    def validate_services(
        cls,
        v: list[BlockStorageServiceCreateExtended]
        | list[ComputeServiceCreateExtended]
        | list[IdentityServiceCreate]
        | list[NetworkServiceCreateExtended]
        | list[ObjectStoreServiceCreateExtended],
    ) -> (
        list[BlockStorageServiceCreateExtended]
        | list[ComputeServiceCreateExtended]
        | list[IdentityServiceCreate]
        | list[NetworkServiceCreateExtended]
        | list[ObjectStoreServiceCreateExtended]
    ):
        """Verify there are no duplicated endpoints in the service lists."""
        find_duplicates(v, "endpoint")
        return v


class ProviderCreateExtended(ProviderCreate):
    """Model to extend the Provider data to add to the DB.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Provider name.
        type (str): Provider type.
        status (str | None): Provider status.
        is_public (bool): Public or private Provider.
        support_email (list of str): list of maintainers emails.
        identity_providers (list of IdentityProviderCreateExtended): Supported identity
            providers.
        projects (list of ProjectCreate): Supplied projects.
        regions (list of RegionCreateExtended): Supplied regions.
    """

    projects: list[ProjectCreate] = Field(
        default_factory=list, description=DOC_EXT_PROJ
    )
    identity_providers: list[IdentityProviderCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_IDP
    )
    regions: list[RegionCreateExtended] = Field(
        default_factory=list, description=DOC_EXT_REG
    )

    @validator("identity_providers")
    @classmethod
    def validate_identity_providers(
        cls, v: list[IdentityProviderCreateExtended], values: Dict[str, Any]
    ) -> list[IdentityProviderCreateExtended]:
        """Validate list of identity providers.

        Verify there are no duplicated endpoints in the identity provider list.
        Check that an SLA is not used by multiple user groups of different IDPs.
        Check that the project pointed by an SLA is not used by multiple user groups of
        different IDPs.
        Check that the SLA's projects belong to the target provider.
        """
        find_duplicates(v, "endpoint")
        projects: list[ProjectCreate] = [i.uuid for i in values.get("projects", [])]
        seen_slas = set()
        seen_projects = set()
        for identity_provider in v:
            for user_group in identity_provider.user_groups:
                find_duplicate_slas(user_group.sla.doc_uuid, seen_slas)
                find_duplicate_projects(user_group.sla.project, seen_projects)
                proj_in_provider(
                    user_group.sla.project,
                    projects,
                    parent=f"SLA {user_group.sla.doc_uuid}",
                )
        return v

    @validator("projects")
    @classmethod
    def validate_projects(cls, v: list[ProjectCreate]) -> list[ProjectCreate]:
        """Verify there are no duplicated names and UUIDs in the project list."""
        find_duplicates(v, "uuid")
        find_duplicates(v, "name")
        return v

    @validator("regions")
    @classmethod
    def validate_regions(
        cls, v: list[RegionCreateExtended], values: Dict[str, Any]
    ) -> list[RegionCreateExtended]:
        """Validate list of regions.

        Verify there are no duplicated names in the region list.
        Verify region's services projects belong to the target provider.
        """
        find_duplicates(v, "name")
        projects: list[ProjectCreate] = [i.uuid for i in values.get("projects", [])]
        for region in v:
            cls.__check_block_storage_service_projects(
                region.block_storage_services, projects
            )
            cls.__check_compute_service_projects(region.compute_services, projects)
            cls.__check_network_service_projects(region.network_services, projects)
            cls.__check_object_store_service_projects(
                region.object_store_services, projects
            )
        return v

    @classmethod
    def __check_block_storage_service_projects(
        cls, services: list[BlockStorageServiceCreateExtended], projects: list[str]
    ) -> None:
        """Check Block Storage service's projects.

        Check quotas' projects belong to the provider.
        """
        for service in services:
            for quota in service.quotas:
                proj_in_provider(quota.project, projects, parent="Block Storage quota")

    @classmethod
    def __check_compute_service_projects(
        cls, services: list[ComputeServiceCreateExtended], projects: list[str]
    ) -> None:
        """Check Compute service's projects.

        Check quotas, flavors and images' projects belong to the provider.
        """
        for service in services:
            for flavor in service.flavors:
                for project in flavor.projects:
                    proj_in_provider(project, projects, parent=f"Flavor {flavor.name}")
            for image in service.images:
                for project in image.projects:
                    proj_in_provider(project, projects, parent=f"Image {image.name}")
            for quota in service.quotas:
                proj_in_provider(quota.project, projects, parent="Compute quota")

    @classmethod
    def __check_network_service_projects(
        cls, services: list[NetworkServiceCreateExtended], projects: list[str]
    ) -> None:
        """Check Network service's projects.

        Check quotas and networks' projects belong to the provider.
        """
        for service in services:
            for network in service.networks:
                proj_in_provider(
                    network.project, projects, parent=f"Network {network.name}"
                )
            for quota in service.quotas:
                proj_in_provider(quota.project, projects, parent="Network quota")

    @classmethod
    def __check_object_store_service_projects(
        cls, services: list[ObjectStoreServiceCreateExtended], projects: list[str]
    ) -> None:
        """Check Object Storage service's projects.

        Check quotas' projects belong to the provider.
        """
        for service in services:
            for quota in service.quotas:
                proj_in_provider(quota.project, projects, parent="Object Storage quota")
