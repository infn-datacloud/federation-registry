"""Pydantic models of the Service supplied by a Provider on a specific Region."""
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field, validator

from fed_reg.models import BaseNode, BaseNodeCreate, BaseNodeRead
from fed_reg.query import create_query_model
from fed_reg.service.constants import DOC_ENDP, DOC_NAME
from fed_reg.service.enum import (
    BlockStorageServiceName,
    ComputeServiceName,
    IdentityServiceName,
    NetworkServiceName,
    ServiceType,
)


class ServiceBase(BaseNode):
    """Model with Service common attributes.

    This model is used also as a public interface.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
    """

    endpoint: AnyHttpUrl = Field(description=DOC_ENDP)


class BlockStorageServiceBase(ServiceBase):
    """Model with the Block Storage Service public and restricted attributes.

    Model derived from ServiceBase to inherit attributes common to all services.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """

    type: ServiceType = Field(
        default=ServiceType.BLOCK_STORAGE, description="Block Storage service type."
    )
    name: BlockStorageServiceName = Field(description=DOC_NAME)

    @validator("type")
    @classmethod
    def check_type(
        cls, v: Literal[ServiceType.BLOCK_STORAGE]
    ) -> Literal[ServiceType.BLOCK_STORAGE]:
        """Verify that the type value is exactly ServiceType.BLOCK_STORAGE."""
        if v != ServiceType.BLOCK_STORAGE:
            raise ValueError(f"Not valid type: {v}")
        return v


class BlockStorageServiceCreate(BaseNodeCreate, BlockStorageServiceBase):
    """Model to create a Block Storage Service.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


class BlockStorageServiceUpdate(BaseNodeCreate, BlockStorageServiceBase):
    """Model to update a Block Storage service.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        endpoint (str | None): URL of the IaaS Service.
        type (str | None): Service type.
        name (str | None): Service name. Depends on type.
    """

    endpoint: Optional[AnyHttpUrl] = Field(default=None, description=DOC_ENDP)
    name: Optional[BlockStorageServiceName] = Field(default=None, description=DOC_NAME)


class BlockStorageServiceReadPublic(BaseNodeRead, ServiceBase):
    """Model, for non-authenticated users, to read Block Storage data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
    """


class BlockStorageServiceRead(BaseNodeRead, BlockStorageServiceBase):
    """Model, for authenticated users, to read Block Storage data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


BlockStorageServiceQuery = create_query_model(
    "BlockStorageServiceQuery", BlockStorageServiceBase
)


class ComputeServiceBase(ServiceBase):
    """Model with the Compute Service public and restricted attributes.

    Model derived from ServiceBase to inherit attributes common to all services.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """

    type: ServiceType = Field(
        default=ServiceType.COMPUTE, description="Compute service type."
    )
    name: ComputeServiceName = Field(description=DOC_NAME)

    @validator("type")
    @classmethod
    def check_type(cls, v) -> Literal[ServiceType.COMPUTE]:
        """Verify that the type value is exactly ServiceType.COMPUTE."""
        if v != ServiceType.COMPUTE:
            raise ValueError(f"Not valid type: {v}")
        return v


class ComputeServiceCreate(BaseNodeCreate, ComputeServiceBase):
    """Model to create a Compute Service.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


class ComputeServiceUpdate(BaseNodeCreate, ComputeServiceBase):
    """Model to update a Compute service.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        endpoint (str | None): URL of the IaaS Service.
        type (str | None): Service type.
        name (str | None): Service name. Depends on type.
    """

    endpoint: Optional[AnyHttpUrl] = Field(default=None, description=DOC_ENDP)
    name: Optional[ComputeServiceName] = Field(default=None, description=DOC_NAME)


class ComputeServiceReadPublic(BaseNodeRead, ServiceBase):
    """Model, for non-authenticated users, to read Compute data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
    """


class ComputeServiceRead(BaseNodeRead, ComputeServiceBase):
    """Model, for authenticated users, to read Compute data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


ComputeServiceQuery = create_query_model("ComputeServiceQuery", ComputeServiceBase)


class IdentityServiceBase(ServiceBase):
    """Model with the Identity Service public and restricted attributes.

    Model derived from ServiceBase to inherit attributes common to all services.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """

    type: ServiceType = Field(
        default=ServiceType.IDENTITY, description="Identity service type."
    )
    name: IdentityServiceName = Field(description=DOC_NAME)

    @validator("type")
    @classmethod
    def check_type(cls, v) -> Literal[ServiceType.IDENTITY]:
        """Verify that the type value is exactly ServiceType.IDENTITY."""
        if v != ServiceType.IDENTITY:
            raise ValueError(f"Not valid type: {v}")
        return v


class IdentityServiceCreate(BaseNodeCreate, IdentityServiceBase):
    """Model to create a Identity Service.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


class IdentityServiceUpdate(BaseNodeCreate, IdentityServiceBase):
    """Model to update a Identity service.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        endpoint (str | None): URL of the IaaS Service.
        type (str | None): Service type.
        name (str | None): Service name. Depends on type.
    """

    endpoint: Optional[AnyHttpUrl] = Field(default=None, description=DOC_ENDP)
    name: Optional[IdentityServiceName] = Field(default=None, description=DOC_NAME)


class IdentityServiceReadPublic(BaseNodeRead, ServiceBase):
    """Model, for non-authenticated users, to read Identity data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
    """


class IdentityServiceRead(BaseNodeRead, IdentityServiceBase):
    """Model, for authenticated users, to read Identity data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


IdentityServiceQuery = create_query_model("IdentityServiceQuery", IdentityServiceBase)


class NetworkServiceBase(ServiceBase):
    """Model with the Network Service public and restricted attributes.

    Model derived from ServiceBase to inherit attributes common to all services.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """

    type: ServiceType = Field(
        default=ServiceType.NETWORK, description="Network service type."
    )
    name: NetworkServiceName = Field(description=DOC_NAME)

    @validator("type")
    @classmethod
    def check_type(cls, v) -> Literal[ServiceType.NETWORK]:
        """Verify that the type value is exactly ServiceType.NETWORK."""
        if v != ServiceType.NETWORK:
            raise ValueError(f"Not valid type: {v}")
        return v


class NetworkServiceCreate(BaseNodeCreate, NetworkServiceBase):
    """Model to create a Network Service.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


class NetworkServiceUpdate(BaseNodeCreate, NetworkServiceBase):
    """Model to update a Network service.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        endpoint (str | None): URL of the IaaS Service.
        type (str | None): Service type.
        name (str | None): Service name. Depends on type.
    """

    endpoint: Optional[AnyHttpUrl] = Field(default=None, description=DOC_ENDP)
    name: Optional[NetworkServiceName] = Field(default=None, description=DOC_NAME)


class NetworkServiceReadPublic(BaseNodeRead, ServiceBase):
    """Model, for non-authenticated users, to read Network data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
    """


class NetworkServiceRead(BaseNodeRead, NetworkServiceBase):
    """Model, for authenticated users, to read Network data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): Service unique ID.
        description (str): Brief description.
        endpoint (str): URL of the IaaS Service.
        type (str): Service type.
        name (str): Service name. Depends on type.
    """


NetworkServiceQuery = create_query_model("NetworkServiceQuery", NetworkServiceBase)
