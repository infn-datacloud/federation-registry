from datetime import datetime
from pydantic import UUID4, BaseModel
from typing import Optional

from ..models import BaseNodeCreate, BaseNodeQuery, BaseNodeRead


class SLABase(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    document_uuid: Optional[UUID4] = None


class SLAQuery(BaseNodeQuery):
    """Service Level Agreement (SLA) Query Model class.

    Attributes:
        description (str | None): Brief description.
        start_date (datetime | None): SLA validity start date.
        end_date (datetime | None): SLA validity end date.
    """

    document_uuid: Optional[UUID4] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SLACreate(BaseNodeCreate, SLABase):
    """Service Level Agreement (SLA) Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PATCH, PUT or POST request.

    Attributes:
        description (str): Brief description.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
        project (UUID4): UUID4 of the target Project.
        user_group (UUID4): UUID4 of the target UserGroup.
        quotas (list of QuotaCreate): List of quotas defined by the SLA.
    """


class SLAUpdate(SLACreate):
    """Service Level Agreement (SLA) Update Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PATCH request.

    Attributes:
        description (str): Brief description.
        start_date (datetime | None): SLA validity start date.
        end_date (datetime | None): SLA validity end date.
        project (UUID4 | None): UUID4 of the target Project.
        user_group (UUID4 | None): UUID4 of the target UserGroup.
        quotas (list of QuotaCreate): List of quotas defined by the SLA.
    """


class SLARead(BaseNodeRead, SLABase):
    """Service Level Agreement (SLA) class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): Unique ID.
        description (str): Brief description.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
        project (Project): UUID4 of the target Project.
        user_group (UserGroup): UUID4 of the target UserGroup.
        quotas (list of Quota): List of quotas defined by the SLA.
    """
