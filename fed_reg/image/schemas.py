"""Pydantic models of the Virtual Machine Image owned by a Provider."""
from typing import Literal, Optional

from pydantic import Field

from fed_reg.image.constants import (
    DOC_ARCH,
    DOC_CUDA,
    DOC_GPU_DRIV,
    DOC_KERN,
    DOC_NAME,
    DOC_OS_DISTR,
    DOC_OS_TYPE,
    DOC_OS_VERS,
    DOC_SHARED,
    DOC_TAGS,
    DOC_UUID,
)
from fed_reg.image.enum import ImageOS
from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseNodeRead,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model


class ImageBasePublic(BaseNode):
    """Model with Image public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        name (str): Image name in the Provider.
        uuid (str): Image unique ID in the Provider
    """

    name: str = Field(description=DOC_NAME)
    uuid: str = Field(description=DOC_UUID)


class ImageBase(ImageBasePublic):
    """Model with Image public and restricted attributes.

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
    """

    os_type: Optional[ImageOS] = Field(default=None, description=DOC_OS_TYPE)
    os_distro: Optional[str] = Field(default=None, description=DOC_OS_DISTR)
    os_version: Optional[str] = Field(default=None, description=DOC_OS_VERS)
    architecture: Optional[str] = Field(default=None, description=DOC_ARCH)
    kernel_id: Optional[str] = Field(default=None, description=DOC_KERN)
    cuda_support: bool = Field(default=False, description=DOC_CUDA)
    gpu_driver: bool = Field(default=False, description=DOC_GPU_DRIV)
    tags: list[str] = Field(default_factory=list, description=DOC_TAGS)


class PrivateImageCreate(BaseNodeCreate, ImageBase):
    """Model to create an Image.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

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
    """

    is_public: Literal[False] = Field(default=False, description=DOC_SHARED)


class SharedImageCreate(BaseNodeCreate, ImageBase):
    """Model to create an Image.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

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
    """

    is_public: Literal[True] = Field(default=True, description=DOC_SHARED)


class ImageUpdate(BaseNodeCreate, ImageBase):
    """Model to update an Image.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        name (str | None): Image name in the Provider.
        uuid (str | None): Image unique ID in the Provider
        os_type (str | None): OS type.
        os_distro (str | None): OS distribution.
        os_version (str | None): Distribution version.
        architecture (str | None): OS architecture.
        kernel_id (str | None): Kernel version.
        cuda_support (str | None): Support for cuda enabled.
        gpu_driver (str | None): Support for GPUs drivers.
        is_public (bool | None): Public or private Image.
        tags (list of str | None): list of tags associated to this Image.
    """

    name: Optional[str] = Field(default=None, description=DOC_NAME)
    uuid: Optional[str] = Field(default=None, description=DOC_UUID)


class ImageReadPublic(BaseNodeRead, BaseReadPublic, ImageBasePublic):
    """Model, for non-authenticated users, to read Image data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): Image unique ID.
        description (str): Brief description.
        name (str): Image name in the Provider.
        uuid (str): Image unique ID in the Provider
    """


class ImageRead(BaseNodeRead, BaseReadPrivate, ImageBase):
    """Model, for authenticated users, to read Image data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

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
        tags (list of str): list of tags associated to this Image.
    """

    is_public: bool | None = Field(default=None, description=DOC_SHARED)


ImageQuery = create_query_model("ImageQuery", ImageBase)
