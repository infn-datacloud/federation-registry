"""Pydantic models of the Resource limitations for Projects on Services."""
from typing import Literal, Optional

from pydantic import Field

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model
from fed_reg.quota.constants import (
    DOC_CORES,
    DOC_GB,
    DOC_GROUP_RULES,
    DOC_GROUPS,
    DOC_INST,
    DOC_NETS,
    DOC_PER_USER,
    DOC_PORT,
    DOC_PUB_IPS,
    DOC_RAM,
    DOC_USAGE,
    DOC_VOL_GB,
    DOC_VOLS,
)
from fed_reg.quota.enum import QuotaType


class QuotaBase(BaseNode):
    """Model with Quota common attributes.

    This model is used also as a public interface.

    Attributes:
    ----------
        description (str): Brief description.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
    """

    per_user: bool = Field(default=False, description=DOC_PER_USER)
    usage: bool = Field(default=False, description=DOC_USAGE)


class BlockStorageQuotaBasePublic(QuotaBase):
    """Model with the Block Storage Quota public and restricted attributes.

    Model derived from QuotaBase to inherit attributes common to all quotas.

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
    """

    type: Literal[QuotaType.BLOCK_STORAGE] = Field(
        default=QuotaType.BLOCK_STORAGE, description="Block storage type"
    )


class BlockStorageQuotaBase(BlockStorageQuotaBasePublic):
    """Model with the Block Storage Quota public and restricted attributes.

    Model derived from QuotaBase to inherit attributes common to all quotas.

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
    """

    gigabytes: Optional[int] = Field(default=None, ge=-1, description=DOC_GB)
    per_volume_gigabytes: Optional[int] = Field(
        default=None, ge=-1, description=DOC_VOL_GB
    )
    volumes: Optional[int] = Field(default=None, ge=-1, description=DOC_VOLS)


class BlockStorageQuotaCreate(BaseNodeCreate, BlockStorageQuotaBase):
    """Model to create a Block Storage Quota.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

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
    """


class BlockStorageQuotaUpdate(BaseNodeCreate, BlockStorageQuotaBase):
    """Model to update a Block Storage Quota.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        type (str | None): Quota type.
        per_user (str | None): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        gigabytes (int | None): Number of max usable gigabytes (GiB).
        per_volume_gigabytes (int | None): Number of max usable gigabytes per volume
            (GiB).
        volumes (int | None): Number of max volumes a user group can create.
    """


class BlockStorageQuotaReadPublic(
    BaseNodeRead, BaseReadPublic, BlockStorageQuotaBasePublic
):
    """Model, for non-authenticated users, to read Block Storage data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
    """


class BlockStorageQuotaRead(BaseNodeRead, BaseReadPrivate, BlockStorageQuotaBase):
    """Model, for authenticated users, to read Block Storage data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

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
    """


BlockStorageQuotaQuery = create_query_model(
    "BlockStorageQuotaQuery", BlockStorageQuotaBase
)


class ComputeQuotaBasePublic(QuotaBase):
    """Model with the Compute Quota public and restricted attributes.

    Model derived from QuotaBase to inherit attributes common to all quotas.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instances (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
    """

    type: Literal[QuotaType.COMPUTE] = Field(
        default=QuotaType.COMPUTE, description="Compute type"
    )


class ComputeQuotaBase(ComputeQuotaBasePublic):
    """Model with the Compute Quota public and restricted attributes.

    Model derived from QuotaBase to inherit attributes common to all quotas.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instances (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
    """

    cores: Optional[int] = Field(default=None, ge=0, description=DOC_CORES)
    instances: Optional[int] = Field(default=None, ge=0, description=DOC_INST)
    ram: Optional[int] = Field(default=None, ge=0, description=DOC_RAM)


class ComputeQuotaCreate(BaseNodeCreate, ComputeQuotaBase):
    """Model to create a Compute Quota.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instances (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
    """


class ComputeQuotaUpdate(BaseNodeCreate, ComputeQuotaBase):
    """Model to update a Compute Quota.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        type (str | None): Quota type.
        per_user (str | None): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instances (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
    """


class ComputeQuotaReadPublic(BaseNodeRead, BaseReadPublic, ComputeQuotaBasePublic):
    """Model, for non-authenticated users, to read Compute data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
    """


class ComputeQuotaRead(BaseNodeRead, BaseReadPrivate, ComputeQuotaBase):
    """Model, for authenticated users, to read Compute data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
        cores (int | None): Number of max usable cores.
        instances (int | None): Number of max VM instances.
        ram (int | None): Number of max usable RAM (MiB).
    """


ComputeQuotaQuery = create_query_model("ComputeQuotaQuery", ComputeQuotaBase)


class NetworkQuotaBasePublic(QuotaBase):
    """Model with the Network Quota public and restricted attributes.

    Model derived from QuotaBase to inherit attributes common to all quotas.

    Attributes:
    ----------
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
    """

    type: Literal[QuotaType.NETWORK] = Field(
        default=QuotaType.NETWORK, description="Network type"
    )


class NetworkQuotaBase(NetworkQuotaBasePublic):
    """Model with the Network Quota public and restricted attributes.

    Model derived from QuotaBase to inherit attributes common to all quotas.

    Attributes:
    ----------
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
    """

    public_ips: Optional[int] = Field(default=None, ge=-1, description=DOC_PUB_IPS)
    networks: Optional[int] = Field(default=None, ge=-1, description=DOC_NETS)
    ports: Optional[int] = Field(default=None, ge=-1, description=DOC_PORT)
    security_groups: Optional[int] = Field(default=None, ge=-1, description=DOC_GROUPS)
    security_group_rules: Optional[int] = Field(
        default=None, ge=-1, description=DOC_GROUP_RULES
    )


class NetworkQuotaCreate(BaseNodeCreate, NetworkQuotaBase):
    """Model to create a Network Quota.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
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
    """


class NetworkQuotaUpdate(BaseNodeCreate, NetworkQuotaBase):
    """Model to update a Network Quota.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
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
    """


class NetworkQuotaReadPublic(BaseNodeRead, BaseReadPublic, NetworkQuotaBasePublic):
    """Model, for non-authenticated users, to read Network data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Quota unique ID.
        description (str): Brief description.
        type (str): Quota type.
        per_user (str): This limitation should be applied to each user.
        usage (str): This quota defines the current resource usage.
    """

    type: QuotaType = Field(description="Network type")


class NetworkQuotaRead(BaseNodeRead, BaseReadPrivate, NetworkQuotaBase):
    """Model, for authenticated users, to read Network data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

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
    """


NetworkQuotaQuery = create_query_model("NetworkQuotaQuery", NetworkQuotaBase)
