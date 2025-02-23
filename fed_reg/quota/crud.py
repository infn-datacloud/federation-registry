"""Module with Create, Read, Update and Delete operations for a Quotas."""
from typing import Optional

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

from fed_reg.crud import CRUDBase


class CRUDBlockStorageQuota(
    CRUDBase[
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
    CRUDBase[
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
    CRUDBase[
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
    CRUDBase[
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
