from pydantic import BaseModel
from typing import Optional

from ..models import BaseNodeCreate, BaseNodeQuery, BaseNodeRead


class UserGroupBase(BaseModel):
    name: str


class UserGroupQuery(BaseNodeQuery):
    """UserGroup Query Model class.

    Attributes:
        description (str | None): Brief description.
        name (str | None): UserGroup name.
    """

    name: Optional[str] = None


class UserGroupCreate(BaseNodeCreate, UserGroupBase):
    """UserGroup Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT or POST request.

    Attributes:
        description (str): Brief description.
        name (str): UserGroup name.
    """


class UserGroupUpdate(BaseNodeCreate, UserGroupQuery):
    """UserGroup Update Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PATCH request.

    Attributes:
        description (str): Brief description.
        name (str | None): UserGroup name.
    """


class UserGroupRead(BaseNodeRead, UserGroupBase):
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
