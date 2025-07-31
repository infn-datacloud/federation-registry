"""Module with Create, Read, Update and Delete operations for a StorageClass."""

from fedreg.service.models import BlockStorageService
from fedreg.storageclass.models import StorageClass
from fedreg.storageclass.schemas import StorageClassCreate, StorageClassUpdate

from fed_reg.crud import CRUDBase


class CRUDStorageClass(CRUDBase[StorageClass, StorageClassCreate, StorageClassUpdate]):
    """StorageClass Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: StorageClassCreate, service: BlockStorageService
    ) -> StorageClass:
        """Create a new StorageClass.

        At first check that a storageclass with the given UUID does not already exist.
        If it does not exist create it. Otherwise check the provider of the existing
        one. If it is the same of the received service, do nothing, otherwise create a
        new storageclass. In any case connect the storageclass to the given service and
        to any received project.
        """
        db_obj = service.storage_classes.get_or_none(name=obj_in.name)
        assert not db_obj, (
            f"A private storageclass with name {obj_in.name} belonging to service "
            f"{service.endpoint} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        return db_obj


storageclass_mgr = CRUDStorageClass(
    model=StorageClass,
    create_schema=StorageClassCreate,
    update_schema=StorageClassUpdate,
)
