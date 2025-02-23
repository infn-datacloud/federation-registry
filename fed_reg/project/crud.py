"""Module with Create, Read, Update and Delete operations for a Project."""

from fedreg.project.models import Project
from fedreg.project.schemas import (
    ProjectCreate,
    ProjectRead,
    ProjectReadPublic,
    ProjectUpdate,
)
from fedreg.project.schemas_extended import (
    ProjectReadExtended,
    ProjectReadExtendedPublic,
)
from fedreg.provider.models import Provider
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)

from fed_reg.crud import CRUDBase
from fed_reg.quota.crud import (
    block_storage_quota_mng,
    compute_quota_mng,
    network_quota_mng,
    object_store_quota_mng,
)
from fed_reg.sla.crud import sla_mng


class CRUDProject(
    CRUDBase[
        Project,
        ProjectCreate,
        ProjectUpdate,
        ProjectRead,
        ProjectReadPublic,
        ProjectReadExtended,
        ProjectReadExtendedPublic,
    ]
):
    """Flavor Create, Read, Update and Delete operations."""

    def create(self, *, obj_in: ProjectCreate, provider: Provider) -> Project:
        """Create a new Project.

        Connect the project to the given provider.
        """
        db_obj = super().create(obj_in=obj_in)
        db_obj.provider.connect(provider)
        return db_obj

    def remove(self, *, db_obj: Project) -> bool:
        """Delete an existing project and all its relationships.

        At first delete its quotas. Then, if the linked SLA points only to this project,
        delete it. Otherwise do nothing. Finally delete the project.
        """
        for item in db_obj.quotas:
            if isinstance(item, BlockStorageQuota):
                block_storage_quota_mng.remove(db_obj=item)
            elif isinstance(item, ComputeQuota):
                compute_quota_mng.remove(db_obj=item)
            elif isinstance(item, NetworkQuota):
                network_quota_mng.remove(db_obj=item)
            elif isinstance(item, ObjectStoreQuota):
                object_store_quota_mng.remove(db_obj=item)
        item = db_obj.sla.single()
        if item and len(item.projects) == 1:
            sla_mng.remove(db_obj=item)
        return super().remove(db_obj=db_obj)


project_mng = CRUDProject(
    model=Project,
    create_schema=ProjectCreate,
    read_schema=ProjectRead,
    read_public_schema=ProjectReadPublic,
    read_extended_schema=ProjectReadExtended,
    read_extended_public_schema=ProjectReadExtendedPublic,
)
