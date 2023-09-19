from typing import List

from app.image.schemas import ImageCreate, ImageQuery, ImageRead
from pydantic import UUID4, BaseModel, Field


class Representation(BaseModel):
    def __str__(self) -> str:
        if self.name is not None:
            return f"{self.name}"
        if self.uuid is not None:
            return f"{self.uuid}"
        return super().__str__()


class ImageWrite(ImageCreate, Representation):
    projects: List[UUID4] = Field(
        default_factory=list,
        description="List of projects UUIDs which have access to this image",
    )


class ImageRead(ImageRead, Representation):
    pass


class ImageQuery(ImageQuery, Representation):
    pass