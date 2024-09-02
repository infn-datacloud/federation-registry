"""Module with Create, Read, Update and Delete operations for a Quotas."""
from typing import Optional

from fed_reg.crud import CRUDInterface
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    ComputeQuotaCreateExtended,
    NetworkQuotaCreateExtended,
    ObjectStoreQuotaCreateExtended,
)
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fed_reg.quota.schemas import (
    BlockStorageQuotaCreate,
    BlockStorageQuotaUpdate,
    ComputeQuotaCreate,
    ComputeQuotaUpdate,
    NetworkQuotaCreate,
    NetworkQuotaUpdate,
    ObjectStoreQuotaCreate,
    ObjectStoreQuotaUpdate,
)
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    NetworkService,
    ObjectStoreService,
)


class CRUDBlockStorageQuota(
    CRUDInterface[BlockStorageQuota, BlockStorageQuotaCreate, BlockStorageQuotaUpdate]
):
    """Block Storage Quota Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[BlockStorageQuota]:
        return BlockStorageQuota

    def create(
        self,
        *,
        obj_in: BlockStorageQuotaCreate,
        service: BlockStorageService,
        project: Project,
    ) -> BlockStorageQuota:
        """Create a new Block Storage Quota.

        Connect the quota to the given service and project.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        db_obj.project.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: BlockStorageQuota,
        obj_in: BlockStorageQuotaCreateExtended | BlockStorageQuotaUpdate,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[BlockStorageQuota]:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            db_projects = {db_item.uuid: db_item for db_item in projects}
            db_proj = db_obj.project.single()
            if obj_in.project != db_proj.uuid:
                db_item = db_projects.get(obj_in.project)
                db_obj.project.reconnect(db_proj, db_item)
                edit = True

        if isinstance(obj_in, BlockStorageQuotaCreateExtended):
            obj_in = BlockStorageQuotaUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data


class CRUDComputeQuota(
    CRUDInterface[ComputeQuota, ComputeQuotaCreate, ComputeQuotaUpdate]
):
    """Compute Quota Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[ComputeQuota]:
        return ComputeQuota

    def create(
        self,
        *,
        obj_in: ComputeQuotaCreate,
        service: ComputeService,
        project: Project,
    ) -> ComputeQuota:
        """Create a new Compute Quota.

        Connect the quota to the given service and project.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        db_obj.project.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: ComputeQuota,
        obj_in: ComputeQuotaCreateExtended | ComputeQuotaUpdate,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[ComputeQuota]:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            db_projects = {db_item.uuid: db_item for db_item in projects}
            db_proj = db_obj.project.single()
            if obj_in.project != db_proj.uuid:
                db_item = db_projects.get(obj_in.project)
                db_obj.project.reconnect(db_proj, db_item)
                edit = True

        if isinstance(obj_in, ComputeQuotaCreateExtended):
            obj_in = ComputeQuotaUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data


class CRUDNetworkQuota(
    CRUDInterface[NetworkQuota, NetworkQuotaCreate, NetworkQuotaUpdate]
):
    """Network Quota Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[NetworkQuota]:
        return NetworkQuota

    def create(
        self,
        *,
        obj_in: NetworkQuotaCreate,
        service: NetworkService,
        project: Project,
    ) -> NetworkQuota:
        """Create a new Network Quota.

        Connect the quota to the given service and project.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        db_obj.project.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: NetworkQuota,
        obj_in: NetworkQuotaCreateExtended | NetworkQuotaUpdate,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[NetworkQuota]:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            db_projects = {db_item.uuid: db_item for db_item in projects}
            db_proj = db_obj.project.single()
            if obj_in.project != db_proj.uuid:
                db_item = db_projects.get(obj_in.project)
                db_obj.project.reconnect(db_proj, db_item)
                edit = True

        if isinstance(obj_in, NetworkQuotaCreateExtended):
            obj_in = NetworkQuotaUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data


class CRUDObjectStoreQuota(
    CRUDInterface[ObjectStoreQuota, ObjectStoreQuotaCreate, ObjectStoreQuotaUpdate]
):
    """Object Storage Quota Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[ObjectStoreQuota]:
        return ObjectStoreQuota

    def create(
        self,
        *,
        obj_in: ObjectStoreQuotaCreate,
        service: ObjectStoreService,
        project: Project,
    ) -> ObjectStoreQuota:
        """Create a new Object Storage Quota.

        Connect the quota to the given service and project.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.service.connect(service)
        db_obj.project.connect(project)
        return db_obj

    def update(
        self,
        *,
        db_obj: ObjectStoreQuota,
        obj_in: ObjectStoreQuotaCreateExtended | ObjectStoreQuotaUpdate,
        projects: Optional[list[Project]] = None,
        force: bool = False,
    ) -> Optional[ObjectStoreQuota]:
        """Update Quota attributes.

        By default do not update relationships or default values. If force is True, if
        different from the current one, replace linked project and apply default values
        when explicit.
        """
        if projects is None:
            projects = []
        edit = False
        if force:
            db_projects = {db_item.uuid: db_item for db_item in projects}
            db_proj = db_obj.project.single()
            if obj_in.project != db_proj.uuid:
                db_item = db_projects.get(obj_in.project)
                db_obj.project.reconnect(db_proj, db_item)
                edit = True

        if isinstance(obj_in, ObjectStoreQuotaCreateExtended):
            obj_in = ObjectStoreQuotaUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data


block_storage_quota_mgr = CRUDBlockStorageQuota()
compute_quota_mgr = CRUDComputeQuota()
network_quota_mgr = CRUDNetworkQuota()
object_store_quota_mgr = CRUDObjectStoreQuota()
