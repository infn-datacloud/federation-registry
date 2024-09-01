"""Pydantic models of the Service Level Agreement between a Project and a User Group."""
from datetime import date
from typing import Any, Dict, Optional

from pydantic import Field, validator

from fed_reg.models import (
    BaseNode,
    BaseNodeCreate,
    BaseReadPrivate,
    BaseReadPublic,
)
from fed_reg.query import create_query_model
from fed_reg.sla.constants import DOC_END, DOC_START, DOC_UUID


class SLABasePublic(BaseNode):
    """Model with SLA public attributes.

    Attributes:
    ----------
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
    """

    doc_uuid: str = Field(description=DOC_UUID)


class SLABase(SLABasePublic):
    """Model with SLA public and restricted attributes.

    Attributes:
    ----------
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
    """

    start_date: date = Field(description=DOC_START)
    end_date: date = Field(description=DOC_END)

    @validator("end_date")
    @classmethod
    def start_date_before_end_date(cls, v: date, values: Dict[str, Any]) -> date:
        """Verify start date precedes end date."""
        start = values.get("start_date", None)
        if start and v:
            assert start < v, f"Start date {start} greater or equal than end date {v}"
        return v


class SLACreate(BaseNodeCreate, SLABase):
    """Model to create an SLA.

    Class without id (which is populated by the database). Expected as input when
    performing a POST request.

    Attributes:
    ----------
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
    """


class SLAUpdate(BaseNodeCreate, SLABase):
    """Model to update an SLA.

    Class without id (which is populated by the database). Expected as input when
    performing a PUT request.

    Default to None attributes with a different default or required.

    Attributes:
    ----------
        description (str | None): Brief description.
        doc_uuid (str | None): Unique ID of the document with the SLA details.
        start_date (datetime | None): SLA validity start date.
        end_date (datetime | None): SLA validity end date.
    """

    doc_uuid: Optional[str] = Field(default=None, description=DOC_UUID)
    start_date: Optional[date] = Field(default=None, description=DOC_START)
    end_date: Optional[date] = Field(default=None, description=DOC_END)


class SLAReadPublic(BaseReadPublic, SLABasePublic):
    """Model, for non-authenticated users, to read SLA data from DB.

    Class to read non-sensible data written in the DB. Expected as output when
    performing a generic REST request without authentication.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (str): SLA unique ID.
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
    """


class SLARead(BaseReadPrivate, SLABase):
    """Model, for authenticated users, to read SLA data from DB.

    Class to read all data written in the DB. Expected as output when performing a
    generic REST request with an authenticated user.

    Add the *uid* attribute, which is the item unique identifier in the database.

    Attributes:
    ----------
        uid (int): SLA unique ID.
        description (str): Brief description.
        doc_uuid (str): Unique ID of the document with the SLA details.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
    """


SLAQuery = create_query_model("SLAQuery", SLABase)
