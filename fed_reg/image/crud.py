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

from fed_reg.crud import CRUDBase, CRUDMultiProject, CRUDPrivateSharedDispatcher


class CRUDPrivateImage(
    CRUDMultiProject[
        PrivateImage,
        PrivateImageCreate,
        PrivateImageCreateExtended,
        ImageUpdate,
        ImageRead,
        ImageReadPublic,
        ImageReadExtended,
        ImageReadExtendedPublic,
    ]
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
            assert db_provider1 != db_provider2, (
                f"A private image with uuid {obj_in.uuid} belonging to provider "
                f"{db_provider1.name} already exists"
            )
            db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)
        self._connect_projects(
            db_obj=db_obj,
            input_uuids=obj_in.projects,
            provider_projects=provider_projects,
        )

        return db_obj


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
            assert db_provider1 != db_provider2, (
                f"A shared image with uuid {obj_in.uuid} belonging to provider "
                f"{db_provider1.name} already exists"
            )
            db_obj = super().create(obj_in=obj_in)

        db_obj.services.connect(service)

        return db_obj


class CRUDImage(
    CRUDPrivateSharedDispatcher[
        PrivateImage,
        SharedImage,
        CRUDPrivateImage,
        CRUDSharedImage,
        PrivateImageCreateExtended,
        SharedImageCreate,
        ImageUpdate,
    ]
):
    """Private and Shared Image Create, Read, Update and Delete operations."""


private_image_mng = CRUDPrivateImage(
    model=PrivateImage,
    create_schema=PrivateImageCreate,
    update_schema=ImageUpdate,
    read_schema=ImageRead,
    read_public_schema=ImageReadPublic,
    read_extended_schema=ImageReadExtended,
    read_extended_public_schema=ImageReadExtendedPublic,
)

shared_image_mng = CRUDSharedImage(
    model=SharedImage,
    create_schema=SharedImageCreate,
    update_schema=ImageUpdate,
    read_schema=ImageRead,
    read_public_schema=ImageReadPublic,
    read_extended_schema=ImageReadExtended,
    read_extended_public_schema=ImageReadExtendedPublic,
)
image_mgr = CRUDImage(
    private_mgr=private_image_mng,
    shared_mgr=shared_image_mng,
    shared_model=SharedImage,
    shared_create_schema=SharedImageCreate,
)
