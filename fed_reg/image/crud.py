"""Module with Create, Read, Update and Delete operations for a Image."""

from fedreg.image.models import PrivateImage, SharedImage
from fedreg.image.schemas import (
    ImageRead,
    ImageReadPublic,
    ImageUpdate,
    PrivateImageCreate,
    SharedImageCreate,
)
from fedreg.image.schemas_extended import ImageReadExtended, ImageReadExtendedPublic
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import PrivateImageCreateExtended
from fedreg.service.models import ComputeService

from fed_reg.crud import CRUDBase, ResourceMultiProjectsBase


class CRUDPrivateImage(
    CRUDBase[
        PrivateImage,
        PrivateImageCreate,
        ImageUpdate,
        ImageRead,
        ImageReadPublic,
        ImageReadExtended,
        ImageReadExtendedPublic,
    ],
    ResourceMultiProjectsBase[PrivateImage],
):
    """Private Image Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: PrivateImageCreateExtended,
        service: ComputeService,
        provider_projects: list[Project],
    ) -> PrivateImage:
        """Create a new Image.

        At first check that a image with the given UUID does not already exist. If it
        does not exist create it. Otherwise check the provider of the existing one. If
        it is the same of the received service, do nothing, otherwise create a new
        image. In any case connect the image to the given service and to any received
        project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        db_obj = self.get(uuid=obj_in.uuid)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            # It's indifferent which service, we want to reach the provider
            db_service = db_obj.services.single()
            db_region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)
            else:
                raise ValueError(
                    f"A private image with uuid {obj_in.uuid} belonging to provider "
                    f"{db_provider1.name} already exists"
                )

        db_obj.services.connect(service)
        super()._connect_projects(
            db_obj=db_obj,
            input_uuids=obj_in.projects,
            provider_projects=provider_projects,
        )

        return db_obj

    def update(
        self,
        *,
        db_obj: PrivateImage,
        obj_in: PrivateImageCreateExtended,
        provider_projects: list[Project],
    ) -> PrivateImage | None:
        """Update Image attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        casted_obj_in = ImageUpdate.parse_obj(obj_in)
        edited_obj1 = super()._update_projects(
            db_obj=db_obj,
            input_uuids=obj_in.projects,
            provider_projects=provider_projects,
        )
        edited_obj2 = super()._update(db_obj=db_obj, obj_in=casted_obj_in, force=True)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


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
        self, *, obj_in: SharedImageCreate, service: ComputeService
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
            # It's indifferent which service, we want to reach the provider
            db_service = db_obj.services.single()
            db_region = db_service.region.single()
            db_provider1 = db_region.provider.single()
            db_region = service.region.single()
            db_provider2 = db_region.provider.single()
            if db_provider1 != db_provider2:
                db_obj = super().create(obj_in=obj_in)
            else:
                raise ValueError(
                    f"A shared image with uuid {obj_in.uuid} belonging to provider "
                    f"{db_provider1.name} already exists"
                )

        db_obj.services.connect(service)

        return db_obj

    def update(
        self, *, db_obj: SharedImage, obj_in: SharedImageCreate
    ) -> SharedImage | None:
        """Update Image attributes.

        By default do not update relationships or default values. If force is True,
        update linked projects and apply default values when explicit.
        """
        obj_in = ImageUpdate.parse_obj(obj_in)
        return super()._update(db_obj=db_obj, obj_in=obj_in, force=True)


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
