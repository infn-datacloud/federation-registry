"""Module with Create, Read, Update and Delete operations for an Image."""
from typing import Optional

from fed_reg.crud import CRUDBase
from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.image.schemas import (
    ImageRead,
    ImageReadPublic,
    ImageUpdate,
    PrivateImageCreate,
    SharedImageCreate,
)
from fed_reg.image.schemas_extended import ImageReadExtended, ImageReadExtendedPublic
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    PrivateImageCreateExtended,
    SharedImageCreateExtended,
)
from fed_reg.region.models import Region
from fed_reg.service.models import ComputeService


class CRUDPrivateImage(
    CRUDBase[
        PrivateImage,
        PrivateImageCreate,
        ImageUpdate,
        ImageRead,
        ImageReadPublic,
        ImageReadExtended,
        ImageReadExtendedPublic,
    ]
):
    """Image Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: PrivateImageCreateExtended,
        service: ComputeService,
        projects: list[Project],
    ) -> PrivateImage:
        """Create a new Image.

        At first check that a image with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        image. In any case connect the image to the given service and to any received
        project.
        """
        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # If a image with the same properties already exists, we need to check if
            # they belong to the same provider. If they belong to different providers we
            # treat them as separate entities.
            # We choose any service; it's irrelevant since we want to reach the provider
            db_service: ComputeService = db_obj.services.single()
            db_region: Region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)

        for project in filter(lambda x: x.uuid in obj_in.projects, projects):
            db_obj.projects.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: PrivateImage,
        obj_in: ImageUpdate | PrivateImageCreateExtended,
        projects: list[Project],
        force: bool = False,
    ) -> PrivateImage | None:
        """Update Image attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        edit = False
        if force:
            edit = self.__update_projects(
                db_obj=db_obj, obj_in=obj_in, provider_projects=projects
            )

        if isinstance(obj_in, PrivateImageCreateExtended):
            obj_in = ImageUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_projects(
        self,
        *,
        obj_in: PrivateImageCreateExtended,
        db_obj: PrivateImage,
        provider_projects: list[Project],
    ) -> bool:
        """Update image linked projects.

        Connect new projects not already connect, leave untouched already linked ones
        and delete old ones no more connected to the image.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.projects}
        db_projects = {db_item.uuid: db_item for db_item in provider_projects}
        for proj in obj_in.projects:
            db_item = db_items.pop(proj, None)
            if not db_item:
                db_item = db_projects.get(proj)
                db_obj.projects.connect(db_item)
                edit = True
        for db_item in db_items.values():
            db_obj.projects.disconnect(db_item)
            edit = True
        return edit


class CRUDSharedImage(
    CRUDBase[
        SharedImage,
        SharedImageCreate,
        ImageUpdate,
        ImageRead,
        ImageReadPublic,
        ImageReadExtended,
        ImageReadExtendedPublic,
    ]
):
    """Image Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: SharedImageCreateExtended, service: ComputeService
    ) -> SharedImage:
        """Create a new Image.

        At first check that a image with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        image. In any case connect the image to the given service and to any received
        project.
        """
        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # If a image with the same properties already exists, we need to check if
            # they belong to the same provider. If they belong to different providers we
            # treat them as separate entities.
            # We choose any service; it's irrelevant since we want to reach the provider
            db_service: ComputeService = db_obj.services.single()
            db_region: Region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)
        return db_obj


private_image_mng = CRUDPrivateImage(
    model=PrivateImage,
    create_schema=PrivateImageCreate,
    read_schema=ImageRead,
    read_public_schema=ImageReadPublic,
    read_extended_schema=ImageReadExtended,
    read_extended_public_schema=ImageReadExtendedPublic,
)

shared_image_mng = CRUDSharedImage(
    model=SharedImage,
    create_schema=SharedImageCreate,
    read_schema=ImageRead,
    read_public_schema=ImageReadPublic,
    read_extended_schema=ImageReadExtended,
    read_extended_public_schema=ImageReadExtendedPublic,
)


class CRUDImage(
    CRUDBase[
        Image,
        PrivateImageCreateExtended | SharedImageCreateExtended,
        ImageUpdate,
        ImageRead,
        ImageReadPublic,
        ImageReadExtended,
        ImageReadExtendedPublic,
    ]
):
    """Image Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: PrivateImageCreateExtended | SharedImageCreateExtended,
        service: ComputeService,
        projects: list[Project] | None = None,
    ) -> Image:
        """Create a new Image.

        At first check that a image with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        image. In any case connect the image to the given service and to any received
        project.
        """
        if isinstance(obj_in, PrivateImageCreateExtended):
            return private_image_mng.create(
                obj_in=obj_in, service=service, projects=projects
            )
        return shared_image_mng.create(obj_in=obj_in, service=service)

    def update(
        self,
        *,
        db_obj: Image,
        obj_in: ImageUpdate | PrivateImageCreateExtended,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[Image]:
        """Update Image attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        if isinstance(obj_in, PrivateImageCreateExtended):
            return private_image_mng.update(
                db_obj=db_obj, obj_in=obj_in, projects=projects, force=force
            )
        elif isinstance(obj_in, SharedImageCreateExtended):
            return shared_image_mng.update(db_obj=db_obj, obj_in=obj_in, force=force)
        return super().update(db_obj=db_obj, obj_in=obj_in, force=force)


image_mng = CRUDImage(
    model=Image,
    create_schema=PrivateImageCreateExtended | SharedImageCreateExtended,
    read_schema=ImageRead,
    read_public_schema=ImageReadPublic,
    read_extended_schema=ImageReadExtended,
    read_extended_public_schema=ImageReadExtendedPublic,
)
