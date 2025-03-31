"""Image REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.image.models import PrivateImage, SharedImage
from fedreg.image.schemas import ImageUpdate

from fed_reg.dependencies import valid_id
from fed_reg.image.crud import image_mgr
from fed_reg.service.api.dependencies import compute_service_must_exist


def image_must_exist(image_uid: str) -> PrivateImage | SharedImage:
    """The target image must exists otherwise raises `not found` error."""
    return valid_id(mgr=image_mgr, item_id=image_uid)


def get_image_item(image_uid: str) -> PrivateImage | SharedImage:
    """Retrieve the target image. If not found, return None."""
    return valid_id(mgr=image_mgr, item_id=image_uid, error=False)


def validate_new_image_values(
    item: Annotated[PrivateImage | SharedImage, Depends(image_must_exist)],
    new_data: ImageUpdate,
) -> tuple[PrivateImage | SharedImage, ImageUpdate]:
    """Check given data are valid ones.

    Check there are no other images, belonging to the same service, with the same
    uuid. Avoid to change image visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid and belonging to the
    same service already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.uuid != item.uuid:
        for service in item.services:
            service = compute_service_must_exist(service.uid)
            db_item = service.images.get_or_none(uuid=new_data.uuid)
            if db_item is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Image with uuid '{item.uuid}' already registered",
                )
    return item, new_data
