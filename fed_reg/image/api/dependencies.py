"""Image REST API dependencies."""

from fastapi import Depends, HTTPException, status
from fedreg.image.models import Image
from fedreg.image.schemas import ImageCreate, ImageUpdate
from fedreg.service.models import ComputeService

from fed_reg.image.crud import image_mng
from fed_reg.service.api.dependencies import valid_compute_service_id


def valid_image_id(image_uid: str) -> Image:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        image_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Image: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = image_mng.get(uid=image_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{image_uid}' not found",
        )
    return item


def valid_image_name(
    item: ImageCreate | ImageUpdate, services: list[ComputeService]
) -> None:
    """Check given data are valid ones.

    Check there are no other images, belonging to the same service, with the same name.

    Args:
    ----
        item (ImageCreate | ImageUpdate): new data.
        services (list of ComputeService): list of services to inspect.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical name,
            belonging to the same service, already exists.
    """
    for service in services:
        service = valid_compute_service_id(service.uid)
        db_item = service.images.get_or_none(name=item.name)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image with name '{item.name}' already registered",
            )


def valid_image_uuid(
    item: ImageCreate | ImageUpdate,
    services: list[ComputeService] = Depends(valid_compute_service_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other images, belonging to the same service, with the same uuid.

    Args:
    ----
        item (ImageCreate | ImageUpdate): new data.
        services (list of ComputeService): list of services to inspect.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical uuid,
            belonging to the same service, already exists.
    """
    for service in services:
        service = valid_compute_service_id(service.uid)
        db_item = service.images.get_or_none(uuid=item.uuid)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image with uuid '{item.uuid}' already registered",
            )


def validate_new_image_values(
    update_data: ImageUpdate, item: Image = Depends(valid_image_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other images, belonging to the same service, with the same uuid
    and name. Avoid to change image visibility.

    Args:
    ----
        update_data (ImageUpdate): new data.
        item (Image): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same service, already exists.
    """
    # if update_data.name != item.name:
    #     valid_image_name(item=update_data, services=item.services.all())
    if update_data.uuid != item.uuid:
        valid_image_uuid(item=update_data, services=item.services.all())
    if update_data.is_public != item.is_public:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image visibility can't be changed",
        )


def is_private_image(item: Image = Depends(valid_image_id)) -> Image:
    """Check given image has private or shared visibility.

    Args:
    ----
        item (Image): entity to validate.

    Returns:
    -------
        Image: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity has not valid visibility
    """
    if item.is_public:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image {item.uid} is a public image",
        )
    return item
