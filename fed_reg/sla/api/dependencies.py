"""SLA REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.sla.models import SLA
from fedreg.sla.schemas import SLAUpdate

from fed_reg.dependencies import valid_id
from fed_reg.sla.crud import sla_mgr


def sla_must_exist(sla_uid: str) -> SLA:
    """The target sla must exists otherwise raises `not found` error."""
    return valid_id(mgr=sla_mgr, item_id=sla_uid)


def get_sla_item(sla_uid: str) -> SLA:
    """Retrieve the target sla. If not found, return None."""
    return valid_id(mgr=sla_mgr, item_id=sla_uid, error=False)


def validate_new_sla_values(
    item: Annotated[SLA, Depends(sla_must_exist)], new_data: SLAUpdate
) -> tuple[SLA, SLAUpdate]:
    """Check given data are valid ones.

    Check there are no other slas with the same site name. Avoid to change
    sla visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical document uuid already
    exists.

    Return the current item and the schema with the new data.
    """
    if new_data.doc_uuid != item.doc_uuid:
        db_item = sla_mgr.get(doc_uuid=new_data.doc_uuid)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SLA with document uuid '{item.doc_uuid}' already registered",
            )
    return item, new_data
