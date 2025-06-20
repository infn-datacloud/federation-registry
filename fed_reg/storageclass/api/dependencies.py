"""StorageClass REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.storageclass.models import StorageClass
from fedreg.storageclass.schemas import StorageClassUpdate

from fed_reg.dependencies import valid_id
from fed_reg.storageclass.crud import storageclass_mgr


def storageclass_must_exist(storageclass_uid: str) -> StorageClass:
    """The target storageclass must exists otherwise raises `not found` error."""
    return valid_id(mgr=storageclass_mgr, item_id=storageclass_uid)


def get_storageclass_item(storageclass_uid: str) -> StorageClass:
    """Retrieve the target storageclass. If not found, return None."""
    return valid_id(mgr=storageclass_mgr, item_id=storageclass_uid, error=False)


def validate_new_storageclass_values(
    item: Annotated[StorageClass, Depends(storageclass_must_exist)],
    new_data: StorageClassUpdate,
) -> tuple[StorageClass, StorageClassUpdate]:
    """Check given data are valid ones.

    Check there are no other storageclasss, belonging to the same service, with the same
    uuid and name. Avoid to change storageclass visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid and belonging to the
    same service already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.uuid is not None and new_data.uuid != item.uuid:
        service = item.service.single()
        db_item = service.storageclasss.get_or_none(uuid=new_data.uuid)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"StorageClass with uuid '{item.uuid}' already registered",
            )
    return item, new_data
