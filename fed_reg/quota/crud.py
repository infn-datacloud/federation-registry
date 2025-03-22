"""Module with Create, Read, Update and Delete operations for a Quotas."""

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
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    NetworkService,
    ObjectStoreService,
)

from fed_reg.crud import CRUDSingleProject


class CRUDBlockStorageQuota(
    CRUDSingleProject[
        BlockStorageQuota,
        BlockStorageQuotaCreate,
        BlockStorageQuotaUpdate,
        BlockStorageQuotaRead,
        BlockStorageQuotaReadPublic,
        BlockStorageQuotaReadExtended,
        BlockStorageQuotaReadExtendedPublic,
    ]
):
    """Block Storage Quota Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: BlockStorageQuotaCreateExtended,
        service: BlockStorageService,
        provider_projects: list[Project],
    ) -> BlockStorageQuota:
        """Create a new Block Storage Quota.

        Connect the quota to the given service and project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        super()._connect_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        return db_obj

    def update(
        self,
        *,
        db_obj: BlockStorageQuota,
        obj_in: BlockStorageQuotaCreateExtended,
        provider_projects: list[Project],
    ) -> BlockStorageQuota | None:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        casted_obj_in = BlockStorageQuotaUpdate.parse_obj(obj_in)
        edited_obj1 = super()._update_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        edited_obj2 = super()._update(db_obj=db_obj, obj_in=casted_obj_in, force=True)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


class CRUDComputeQuota(
    CRUDSingleProject[
        ComputeQuota,
        ComputeQuotaCreate,
        ComputeQuotaUpdate,
        ComputeQuotaRead,
        ComputeQuotaReadPublic,
        ComputeQuotaReadExtended,
        ComputeQuotaReadExtendedPublic,
    ]
):
    """Compute Quota Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: ComputeQuotaCreate,
        service: ComputeService,
        provider_projects: list[Project],
    ) -> ComputeQuota:
        """Create a new Compute Quota.

        Connect the quota to the given service and project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        super()._connect_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        return db_obj

    def update(
        self,
        *,
        db_obj: ComputeQuota,
        obj_in: ComputeQuotaCreateExtended,
        provider_projects: list[Project],
    ) -> ComputeQuota | None:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        casted_obj_in = ComputeQuotaUpdate.parse_obj(obj_in)
        edited_obj1 = super()._update_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        edited_obj2 = super()._update(db_obj=db_obj, obj_in=casted_obj_in, force=True)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


class CRUDNetworkQuota(
    CRUDSingleProject[
        NetworkQuota,
        NetworkQuotaCreate,
        NetworkQuotaUpdate,
        NetworkQuotaRead,
        NetworkQuotaReadPublic,
        NetworkQuotaReadExtended,
        NetworkQuotaReadExtendedPublic,
    ]
):
    """Network Quota Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: NetworkQuotaCreate,
        service: NetworkService,
        provider_projects: list[Project],
    ) -> NetworkQuota:
        """Create a new Network Quota.

        Connect the quota to the given service and project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        super()._connect_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        return db_obj

    def update(
        self,
        *,
        db_obj: NetworkQuota,
        obj_in: NetworkQuotaCreateExtended | NetworkQuotaUpdate,
        provider_projects: list[Project],
    ) -> NetworkQuota | None:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        casted_obj_in = NetworkQuotaUpdate.parse_obj(obj_in)
        edited_obj1 = super()._update_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        edited_obj2 = super()._update(db_obj=db_obj, obj_in=casted_obj_in, force=True)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


class CRUDObjectStoreQuota(
    CRUDSingleProject[
        ObjectStoreQuota,
        ObjectStoreQuotaCreate,
        ObjectStoreQuotaUpdate,
        ObjectStoreQuotaRead,
        ObjectStoreQuotaReadPublic,
        ObjectStoreQuotaReadExtended,
        ObjectStoreQuotaReadExtendedPublic,
    ]
):
    """Object Storage Quota Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: ObjectStoreQuotaCreate,
        service: ObjectStoreService,
        provider_projects: list[Project],
    ) -> ObjectStoreQuota:
        """Create a new Object Storage Quota.

        Connect the quota to the given service and project.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        super()._connect_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        return db_obj

    def update(
        self,
        *,
        db_obj: ObjectStoreQuota,
        obj_in: ObjectStoreQuotaCreateExtended,
        provider_projects: list[Project],
    ) -> ObjectStoreQuota | None:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        assert len(provider_projects) > 0, "The provider's projects list is empty"
        casted_obj_in = ObjectStoreQuotaUpdate.parse_obj(obj_in)
        edited_obj1 = super()._update_project(
            db_obj=db_obj,
            input_uuid=obj_in.project,
            provider_projects=provider_projects,
        )
        edited_obj2 = super()._update(db_obj=db_obj, obj_in=casted_obj_in, force=True)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


block_storage_quota_mng = CRUDBlockStorageQuota(
    model=BlockStorageQuota,
    create_schema=BlockStorageQuotaCreate,
    read_schema=BlockStorageQuotaRead,
    read_public_schema=BlockStorageQuotaReadPublic,
    read_extended_schema=BlockStorageQuotaReadExtended,
    read_extended_public_schema=BlockStorageQuotaReadExtendedPublic,
)
compute_quota_mng = CRUDComputeQuota(
    model=ComputeQuota,
    create_schema=ComputeQuotaCreate,
    read_schema=ComputeQuotaRead,
    read_public_schema=ComputeQuotaReadPublic,
    read_extended_schema=ComputeQuotaReadExtended,
    read_extended_public_schema=ComputeQuotaReadExtendedPublic,
)
network_quota_mng = CRUDNetworkQuota(
    model=NetworkQuota,
    create_schema=NetworkQuotaCreate,
    read_schema=NetworkQuotaRead,
    read_public_schema=NetworkQuotaReadPublic,
    read_extended_schema=NetworkQuotaReadExtended,
    read_extended_public_schema=NetworkQuotaReadExtendedPublic,
)
object_store_quota_mng = CRUDObjectStoreQuota(
    model=ObjectStoreQuota,
    create_schema=ObjectStoreQuotaCreate,
    read_schema=ObjectStoreQuotaRead,
    read_public_schema=ObjectStoreQuotaReadPublic,
    read_extended_schema=ObjectStoreQuotaReadExtended,
    read_extended_public_schema=ObjectStoreQuotaReadExtendedPublic,
)
