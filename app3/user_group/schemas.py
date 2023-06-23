from pydantic import Field
from typing import Optional, List

from ..cluster.schemas import Cluster
from ..flavor.schemas import Flavor
from ..image.schemas import Image
from ..models import BaseNodeCreate, BaseNodeQuery, BaseNodeRead


class UserGroupQuery(BaseNodeQuery):
    """UserGroup Query Model class.

    Attributes:
        description (str | None): Brief description.
        name (str | None): UserGroup name.
    """

    name: Optional[str] = None


class UserGroupPatch(BaseNodeCreate):
    """UserGroup Patch Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PATCH request.

    Attributes:
        description (str): Brief description.
        name (str | None): UserGroup name.
    """

    name: Optional[str] = None


class UserGroupCreate(UserGroupPatch):
    """UserGroup Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT or POST request.

    Attributes:
        description (str): Brief description.
        name (str): UserGroup name.
    """

    name: str


class UserGroup(UserGroupCreate, BaseNodeRead):
    """UserGroup class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): Unique ID.
        description (str): Brief description.
        name (str): UserGroup name.
    """


class UserGroupExtended(UserGroup):
    """UserGroup class

    Class retrieved from the database
    expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): UserGroup unique ID.
        name (str): UserGroup name.
        description (str): Brief description.
    """

    clusters: List[Cluster] = Field(default_factory=list)
    flavors: List[Flavor] = Field(default_factory=list)
    images: List[Image] = Field(default_factory=list)