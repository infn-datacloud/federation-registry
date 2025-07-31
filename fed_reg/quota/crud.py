"""Module with Create, Read, Update and Delete operations for a Quotas."""

from typing import Generic, TypeVar

from fedreg.project.models import Project
from fedreg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    ComputeQuotaCreateExtended,
    NetworkQuotaCreateExtended,
    ObjectStoreQuotaCreateExtended,
    StorageClassQuotaCreateExtended,
)
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
    StorageClassQuota,
)
from fedreg.quota.schemas import (
    BlockStorageQuotaCreate,
    BlockStorageQuotaUpdate,
    ComputeQuotaCreate,
    ComputeQuotaUpdate,
    NetworkQuotaCreate,
    NetworkQuotaUpdate,
    ObjectStoreQuotaCreate,
    ObjectStoreQuotaUpdate,
    StorageClassQuotaCreate,
    StorageClassQuotaUpdate,
)
from fedreg.storageclass.models import StorageClass

from fed_reg.crud import CreateSchemaType, CRUDBase, ModelType, UpdateSchemaType

CreateExtendedSchemaType = TypeVar(
    "CreateExtendedSchemaType",
    bound=BlockStorageQuotaCreateExtended
    | ComputeQuotaCreateExtended
    | NetworkQuotaCreateExtended
    | ObjectStoreQuotaCreateExtended
    | StorageClassQuotaCreateExtended,
)


class CRUDQuota(
    CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, CreateExtendedSchemaType, UpdateSchemaType],
):
    """Class with the function to merge new projects into current ones."""

    def create(
        self,
        *,
        obj_in: CreateExtendedSchemaType,
        service: ModelType,
        provider_projects: list[Project],
    ) -> ModelType:
        """Create a new Block Storage Quota.

        Connect the quota to the given service and project.
        Before this, check projects list and verify that target project does already
        have a quota with the same usage and per-user values on target service.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        project = next(
            filter(lambda x: x.uuid == obj_in.project, provider_projects), None
        )
        assert project is not None, (
            f"Input project {obj_in.project} not in the provider "
            f"projects: {[i.uuid for i in provider_projects]}"
        )
        service_quotas = service.quotas.filter(
            usage=obj_in.usage, per_user=obj_in.per_user
        )
        quota = next(
            filter(lambda x: x.project.single().uuid == obj_in.project, service_quotas),
            None,
        )
        assert quota is None, (
            f"Target project {obj_in.project} already has a quota with usage="
            f"{obj_in.usage} and per_user={obj_in.per_user} on service "
            f"{service.endpoint}"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        db_obj.project.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: CreateExtendedSchemaType,
        provider_projects: list[Project],
    ) -> ModelType | None:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"

        edit = False
        db_projects = {db_item.uuid: db_item for db_item in provider_projects}
        db_proj = db_obj.project.single()

        if obj_in.project != db_proj.uuid:
            db_item = db_projects.get(obj_in.project)
            assert db_item is not None, (
                f"Input project {obj_in.project} not in the provider "
                f"projects: {[i.uuid for i in provider_projects]}"
            )
            db_obj.project.reconnect(db_proj, db_item)
            edit = True

        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)

        return db_obj.save() if edit or edit_content else None


class CRUDBlockStorageQuota(
    CRUDQuota[
        BlockStorageQuota,
        BlockStorageQuotaCreate,
        BlockStorageQuotaCreateExtended,
        BlockStorageQuotaUpdate,
    ]
):
    """Block Storage Quota Create, Read, Update and Delete operations."""


class CRUDComputeQuota(
    CRUDQuota[
        ComputeQuota, ComputeQuotaCreate, ComputeQuotaCreateExtended, ComputeQuotaUpdate
    ]
):
    """Compute Quota Create, Read, Update and Delete operations."""


class CRUDNetworkQuota(
    CRUDQuota[
        NetworkQuota, NetworkQuotaCreate, NetworkQuotaCreateExtended, NetworkQuotaUpdate
    ]
):
    """Network Quota Create, Read, Update and Delete operations."""


class CRUDObjectStoreQuota(
    CRUDQuota[
        ObjectStoreQuota,
        ObjectStoreQuotaCreate,
        ObjectStoreQuotaCreateExtended,
        ObjectStoreQuotaUpdate,
    ]
):
    """Object Storage Quota Create, Read, Update and Delete operations."""


class CRUDStorageClassQuota(
    CRUDQuota[
        StorageClassQuota,
        StorageClassQuotaCreate,
        StorageClassQuotaCreateExtended,
        StorageClassQuotaUpdate,
    ]
):
    """Object Storage Quota Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: CreateExtendedSchemaType,
        storage_class: StorageClass,
        provider_projects: list[Project],
    ) -> ModelType:
        """Create a new Block Storage Quota.

        Connect the quota to the given service and project.
        Before this, check projects list and verify that target project does already
        have a quota with the same usage and per-user values on target service.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        project = next(
            filter(lambda x: x.uuid == obj_in.project, provider_projects), None
        )
        assert project is not None, (
            f"Input project {obj_in.project} not in the provider "
            f"projects: {[i.uuid for i in provider_projects]}"
        )
        storage_class_quotas = storage_class.quotas.filter(
            usage=obj_in.usage, per_user=obj_in.per_user
        )
        quota = next(
            filter(
                lambda x: x.project.single().uuid == obj_in.project,
                storage_class_quotas,
            ),
            None,
        )
        assert quota is None, (
            f"Target project {obj_in.project} already has a quota with usage="
            f"{obj_in.usage} and per_user={obj_in.per_user} on storage_class "
            f"{storage_class.name}"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.storage_class.connect(storage_class)
        db_obj.project.connect(project)
        return db_obj


block_storage_quota_mng = CRUDBlockStorageQuota(
    model=BlockStorageQuota,
    create_schema=BlockStorageQuotaCreate,
    update_schema=BlockStorageQuotaUpdate,
)
compute_quota_mng = CRUDComputeQuota(
    model=ComputeQuota,
    create_schema=ComputeQuotaCreate,
    update_schema=ComputeQuotaUpdate,
)
network_quota_mng = CRUDNetworkQuota(
    model=NetworkQuota,
    create_schema=NetworkQuotaCreate,
    update_schema=NetworkQuotaUpdate,
)
object_store_quota_mng = CRUDObjectStoreQuota(
    model=ObjectStoreQuota,
    create_schema=ObjectStoreQuotaCreate,
    update_schema=ObjectStoreQuotaUpdate,
)
storage_class_quota_mng = CRUDStorageClassQuota(
    model=StorageClassQuota,
    create_schema=StorageClassQuotaCreate,
    update_schema=StorageClassQuotaUpdate,
)
