from typing import Any

from fastapi import HTTPException, status


def valid_id(*, mgr: Any, item_id: str, error: bool = True) -> Any:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        flavor_uid (str): uid of the target DB entity.

    Returns:
    -------
        Flavor: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = mgr.get(uid=item_id)
    if not item and error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{mgr.model} with uid '{item_id}' not found",
        )
    return item
