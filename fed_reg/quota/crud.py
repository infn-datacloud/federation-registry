"""Module with Create, Read, Update and Delete operations for a Quotas."""

from typing import Generic, TypeVar

from fedreg.project.models import Project
from fedreg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    ComputeQuotaCreateExtended,
    NetworkQuotaCreateExtended,
    ObjectStoreQuotaCreateExtended,
)
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fedreg.quota.schemas import (
    BlockStorageQuotaCreate,
    BlockStorageQuotaRead,
    BlockStorageQuotaReadPublic,
    BlockStorageQuotaUpdate,
    ComputeQuotaCreate,
    ComputeQuotaRead,
    ComputeQuotaReadPublic,
    ComputeQuotaUpdate,
    NetworkQuotaCreate,
    NetworkQuotaRead,
    NetworkQuotaReadPublic,
    NetworkQuotaUpdate,
    ObjectStoreQuotaCreate,
    ObjectStoreQuotaRead,
    ObjectStoreQuotaReadPublic,
    ObjectStoreQuotaUpdate,
)
from fedreg.quota.schemas_extended import (
    BlockStorageQuotaReadExtended,
    BlockStorageQuotaReadExtendedPublic,
    ComputeQuotaReadExtended,
    ComputeQuotaReadExtendedPublic,
    NetworkQuotaReadExtended,
    NetworkQuotaReadExtendedPublic,
    ObjectStoreQuotaReadExtended,
    ObjectStoreQuotaReadExtendedPublic,
)

from fed_reg.crud import (
    CreateSchemaType,
    CRUDBase,
    ModelType,
    ReadExtendedPublicSchemaType,
    ReadExtendedSchemaType,
    ReadPublicSchemaType,
    ReadSchemaType,
    UpdateSchemaType,
)

CreateExtendedSchemaType = TypeVar(
    "CreateExtendedSchemaType",
    bound=BlockStorageQuotaCreateExtended
    | ComputeQuotaCreateExtended
    | NetworkQuotaCreateExtended
    | ObjectStoreQuotaCreateExtended,
)


class CRUDQuota(
    CRUDBase[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ReadSchemaType,
        ReadPublicSchemaType,
        ReadExtendedSchemaType,
        ReadExtendedPublicSchemaType,
    ],
    Generic[
        ModelType,
        CreateSchemaType,
        CreateExtendedSchemaType,
        UpdateSchemaType,
        ReadSchemaType,
        ReadPublicSchemaType,
        ReadExtendedSchemaType,
        ReadExtendedPublicSchemaType,
    ],
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
        if project is None:
            raise ValueError(
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
        assert not quota, (
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
        edited_obj1 = self._update_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        edited_obj2 = super().update(db_obj=db_obj, obj_in=obj_in)
        return edited_obj2 if edited_obj2 is not None else edited_obj1

    def _update_project(
        self,
        *,
        db_obj: ModelType,
        input_uuid: str,
        provider_projects: list[Project],
    ) -> ModelType | None:
        """Update resource linked project.

        If the new project differs from the current one, reconnect new one.
        """
        db_projects = {db_item.uuid: db_item for db_item in provider_projects}
        db_proj = db_obj.project.single()
        if input_uuid != db_proj.uuid:
            db_item = db_projects.get(input_uuid)
            assert db_item is not None, (
                f"Input project {input_uuid} not in the provider "
                f"projects: {[i.uuid for i in provider_projects]}"
            )
            db_obj.project.reconnect(db_proj, db_item)
            return db_obj.save()
        return None


class CRUDBlockStorageQuota(
    CRUDQuota[
        BlockStorageQuota,
        BlockStorageQuotaCreate,
        BlockStorageQuotaCreateExtended,
        BlockStorageQuotaUpdate,
        BlockStorageQuotaRead,
        BlockStorageQuotaReadPublic,
        BlockStorageQuotaReadExtended,
        BlockStorageQuotaReadExtendedPublic,
    ]
):
    """Block Storage Quota Create, Read, Update and Delete operations."""


class CRUDComputeQuota(
    CRUDQuota[
        ComputeQuota,
        ComputeQuotaCreate,
        ComputeQuotaCreateExtended,
        ComputeQuotaUpdate,
        ComputeQuotaRead,
        ComputeQuotaReadPublic,
        ComputeQuotaReadExtended,
        ComputeQuotaReadExtendedPublic,
    ]
):
    """Compute Quota Create, Read, Update and Delete operations."""


class CRUDNetworkQuota(
    CRUDQuota[
        NetworkQuota,
        NetworkQuotaCreate,
        NetworkQuotaCreateExtended,
        NetworkQuotaUpdate,
        NetworkQuotaRead,
        NetworkQuotaReadPublic,
        NetworkQuotaReadExtended,
        NetworkQuotaReadExtendedPublic,
    ]
):
    """Network Quota Create, Read, Update and Delete operations."""


class CRUDObjectStoreQuota(
    CRUDQuota[
        ObjectStoreQuota,
        ObjectStoreQuotaCreate,
        ObjectStoreQuotaCreateExtended,
        ObjectStoreQuotaUpdate,
        ObjectStoreQuotaRead,
        ObjectStoreQuotaReadPublic,
        ObjectStoreQuotaReadExtended,
        ObjectStoreQuotaReadExtendedPublic,
    ]
):
    """Object Storage Quota Create, Read, Update and Delete operations."""


block_storage_quota_mng = CRUDBlockStorageQuota(
    model=BlockStorageQuota,
    create_schema=BlockStorageQuotaCreate,
    update_schema=BlockStorageQuotaUpdate,
    read_schema=BlockStorageQuotaRead,
    read_public_schema=BlockStorageQuotaReadPublic,
    read_extended_schema=BlockStorageQuotaReadExtended,
    read_extended_public_schema=BlockStorageQuotaReadExtendedPublic,
)
compute_quota_mng = CRUDComputeQuota(
    model=ComputeQuota,
    create_schema=ComputeQuotaCreate,
    update_schema=ComputeQuotaUpdate,
    read_schema=ComputeQuotaRead,
    read_public_schema=ComputeQuotaReadPublic,
    read_extended_schema=ComputeQuotaReadExtended,
    read_extended_public_schema=ComputeQuotaReadExtendedPublic,
)
network_quota_mng = CRUDNetworkQuota(
    model=NetworkQuota,
    create_schema=NetworkQuotaCreate,
    update_schema=NetworkQuotaUpdate,
    read_schema=NetworkQuotaRead,
    read_public_schema=NetworkQuotaReadPublic,
    read_extended_schema=NetworkQuotaReadExtended,
    read_extended_public_schema=NetworkQuotaReadExtendedPublic,
)
object_store_quota_mng = CRUDObjectStoreQuota(
    model=ObjectStoreQuota,
    create_schema=ObjectStoreQuotaCreate,
    update_schema=ObjectStoreQuotaUpdate,
    read_schema=ObjectStoreQuotaRead,
    read_public_schema=ObjectStoreQuotaReadPublic,
    read_extended_schema=ObjectStoreQuotaReadExtended,
    read_extended_public_schema=ObjectStoreQuotaReadExtendedPublic,
)
