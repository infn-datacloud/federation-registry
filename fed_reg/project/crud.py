"""Module with Create, Read, Update and Delete operations for a Project."""
from fed_reg.crud import CRUDInterface
from fed_reg.project.models import Project
from fed_reg.project.schemas import ProjectCreate, ProjectUpdate
from fed_reg.provider.models import Provider
from fed_reg.quota.crud import (
    block_storage_quota_mgr,
    compute_quota_mgr,
    network_quota_mgr,
    object_store_quota_mgr,
)
from fed_reg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fed_reg.sla.crud import sla_mgr


class CRUDProject(CRUDInterface[Project, ProjectCreate, ProjectUpdate]):
    """Flavor Create, Read, Update and Delete operations."""

    @property
    def model(self) -> type[Project]:
        return Project

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
                block_storage_quota_mgr.remove(db_obj=item)
            elif isinstance(item, ComputeQuota):
                compute_quota_mgr.remove(db_obj=item)
            elif isinstance(item, NetworkQuota):
                network_quota_mgr.remove(db_obj=item)
            elif isinstance(item, ObjectStoreQuota):
                object_store_quota_mgr.remove(db_obj=item)
        item = db_obj.sla.single()
        if item and len(item.projects) == 1:
            sla_mgr.remove(db_obj=item)
        return super().remove(db_obj=db_obj)


project_mgr = CRUDProject()
