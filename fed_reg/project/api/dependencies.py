"""Project REST API dependencies."""

from fastapi import Depends, HTTPException, status
from fedreg.project.models import Project
from fedreg.project.schemas import ProjectCreate, ProjectUpdate
from fedreg.provider.models import Provider

from fed_reg.project.crud import project_mgr
from fed_reg.provider.api.dependencies import valid_provider_id


def valid_project_id(project_uid: str) -> Project:
    """Check given uid corresponds to an entity in the DB.

    Args:
    ----
        project_uid (UUID4): uid of the target DB entity.

    Returns:
    -------
        Project: DB entity with given uid.

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
    """
    item = project_mgr.get(uid=project_uid.replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_uid}' not found",
        )
    return item


# def project_has_no_sla(
#     project: Project = Depends(valid_project_id),
# ) -> Project:
#     """Check target project is not already involved into a SLA.

#     Args:
#         update_data (ProejctRead): new data.

#     Returns:
#         None

#     Raises:
#         NotFoundError: DB entity with given uid not found.
#         BadRequestError: DB entity already has an associated SLA.
#     """

#     if project.sla.single():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Project '{project.name}' already has an associated SLA",
#         )
#     return project


def valid_project_name(
    item: ProjectCreate | ProjectUpdate,
    provider: Provider = Depends(valid_provider_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other projects, belonging to the same provider, with the same
    name.

    Args:
    ----
        item (ProjectCreate | ProjectUpdate): new data.
        provider (Provider): hosting provider.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical name,
            belonging to the same provider, already exists.
    """
    db_item = provider.projects.get_or_none(name=item.name)
    if db_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with name '{item.name}' already registered",
        )


def valid_project_uuid(
    item: ProjectCreate | ProjectUpdate,
    provider: Provider = Depends(valid_provider_id),
) -> None:
    """Check given data are valid ones.

    Check there are no other projects, belonging to the same provider, with the same
    uuid.

    Args:
    ----
        item (ProjectCreate | ProjectUpdate): new data.
        provider (Provider): hosting provider.

    Returns:
    -------
        None

    Raises:
    ------
        BadRequestError: DB entity with identical uuid,
            belonging to the same provider, already exists.
    """
    db_item = provider.projects.get_or_none(uuid=item.uuid)
    if db_item is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with uuid '{item.uuid}' already registered",
        )


def validate_new_project_values(
    update_data: ProjectUpdate, item: Project = Depends(valid_project_id)
) -> None:
    """Check given data are valid ones.

    Check there are no other projects, belonging to the same provider, with the same
    uuid and name.

    Args:
    ----
        update_data (ProjectUpdate): new data.
        item (Project): DB entity to update.

    Returns:
    -------
        None

    Raises:
    ------
        NotFoundError: DB entity with given uid not found.
        BadRequestError: DB entity with identical name or uuid,
            belonging to the same provider, already exists.
    """
    if update_data.name != item.name:
        valid_project_name(item=update_data, provider=item.provider.single())
    if update_data.uuid != item.uuid:
        valid_project_uuid(item=update_data, provider=item.provider.single())
