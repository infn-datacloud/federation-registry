from pydantic import UUID4, BaseModel
from typing import Optional

from app.models import BaseNodeCreate, BaseNodeRead
from app.query import create_query_model


class ProjectBase(BaseModel):
    name: str
    uuid: UUID4
    public_network_name: Optional[str] = None
    private_network_name: Optional[str] = None
    private_network_proxy_host: Optional[str] = None
    private_network_proxy_user: Optional[str] = None


class ProjectCreate(BaseNodeCreate, ProjectBase):
    """Project Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT or POST request.

    Attributes:
        description (str): Brief description.
        public_network_name (str | None): TODO
        private_network_name (str | None): TODO
        private_network_proxy_host (str | None): TODO
        private_network_proxy_user (str | None): TODO
    """


class ProjectUpdate(ProjectCreate):
    """Project Update Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT request.

    Attributes:
        description (str): Brief description.
        public_network_name (str | None): TODO
        private_network_name (str | None): TODO
        private_network_proxy_host (str | None): TODO
        private_network_proxy_user (str | None): TODO
    """


class ProjectRead(BaseNodeRead, ProjectBase):
    """Project class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): Unique ID.
        description (str): Brief description.
        public_network_name (str | None): TODO
        private_network_name (str | None): TODO
        private_network_proxy_host (str | None): TODO
        private_network_proxy_user (str | None): TODO
    """


ProjectQuery = create_query_model("ProjectQuery", ProjectBase)