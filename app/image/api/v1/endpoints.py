from fastapi import APIRouter, Depends, HTTPException, status
from neomodel import db
from typing import List, Optional

from ..dependencies import valid_image_id
from ...crud import image
from ...models import Image as ImageModel
from ...schemas import ImageQuery, ImageRead, ImageUpdate
from ....pagination import Pagination, paginate
from ....query import CommonGetQuery

router = APIRouter(prefix="/images", tags=["images"])


@db.read_transaction
@router.get("/", response_model=List[ImageRead])
def get_images(
    comm: CommonGetQuery = Depends(),
    page: Pagination = Depends(),
    item: ImageQuery = Depends(),
):
    items = image.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    return paginate(items=items, page=page.page, size=page.size)


@db.read_transaction
@router.get("/{image_uid}", response_model=ImageRead)
def get_image(item: ImageModel = Depends(valid_image_id)):
    return item


@db.write_transaction
@router.put("/{image_uid}", response_model=Optional[ImageRead])
def put_image(
    update_data: ImageUpdate, item: ImageModel = Depends(valid_image_id)
):
    return image.update(db_obj=item, obj_in=update_data)


@db.write_transaction
@router.delete("/{image_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_images(item: ImageModel = Depends(valid_image_id)):
    if not image.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
