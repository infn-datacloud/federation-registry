"""Image REST API utils."""

from fedreg.image.models import PrivateImage, SharedImage
from fedreg.image.schemas import ImageRead, ImageReadPublic
from fedreg.image.schemas_extended import ImageReadExtended, ImageReadExtendedPublic
from pydantic import BaseModel, Field

from fed_reg.query import choose_out_schema


class ImageReadSingle(BaseModel):
    __root__: (
        ImageReadExtended | ImageRead | ImageReadExtendedPublic | ImageReadPublic
    ) = Field(..., discriminator="schema_type")


class ImageReadMulti(BaseModel):
    __root__: (
        list[ImageReadExtended]
        | list[ImageRead]
        | list[ImageReadExtendedPublic]
        | list[ImageReadPublic]
    ) = Field(..., discriminator="schema_type")


def choose_schema(
    items: list[PrivateImage | SharedImage],
    *,
    auth: bool,
    with_conn: bool,
    short: bool,
) -> (
    list[ImageRead]
    | list[ImageReadPublic]
    | list[ImageReadExtended]
    | list[ImageReadExtendedPublic]
    | ImageRead
    | ImageReadPublic
    | ImageReadExtended
    | ImageReadExtendedPublic
):
    return choose_out_schema(
        items=items,
        auth=auth,
        short=short,
        with_conn=with_conn,
        read_private_schema=ImageRead,
        read_public_schema=ImageReadPublic,
        read_private_extended_schema=ImageReadExtended,
        read_public_extended_schema=ImageReadExtendedPublic,
    )
