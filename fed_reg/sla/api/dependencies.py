"""SLA REST API dependencies."""

from fastapi import Depends, HTTPException, status

from fed_reg.sla.crud import sla_mgr
from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import SLACreate, SLAUpdate


def valid_sla_id(sla_uid: str) -> SLA:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        sla_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        SLA: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = sla_mgr.get(uid=sla_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SLA '{sla_uid}' not found",
        )
    return item


def is_unique_sla(item: SLACreate | SLAUpdate) -> None:
    """Check there are no other SLAs with the same document uuid.

    Args:
    ----
        item (SLACreate | SLAUpdate): new data.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with given document uuid already exists.
    """
    db_item = sla_mgr.get(doc_uuid=item.doc_uuid)
    if db_item is not None:
        msg = f"Document '{item.doc_uuid}' already used "
        msg += "by another SLA"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )


def validate_new_sla_values(
    update_data: SLAUpdate, item: SLA = Depends(valid_sla_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other SLAs with the same document uuid.

    Args:
    ----
        update_data (FlavorUpdate): new data.
        item (Flavor): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with given document uuid already exists.
    """
    if update_data.doc_uuid is not None and update_data.doc_uuid != item.doc_uuid:
        is_unique_sla(update_data)
