"""Project REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.project.models import Project
from fedreg.project.schemas import ProjectUpdate
from neomodel.exceptions import CardinalityViolation

from fed_reg.dependencies import valid_id
from fed_reg.project.crud import project_mgr


def project_must_exist(project_uid: str) -> Project:
    """The target project must exists otherwise raises `not found` error."""
    return valid_id(mgr=project_mgr, item_id=project_uid)


def get_project_item(project_uid: str) -> Project:
    """Retrieve the target project. If not found, return None."""
    return valid_id(mgr=project_mgr, item_id=project_uid, error=False)


def validate_new_project_values(
    item: Annotated[Project, Depends(project_must_exist)],
    new_data: ProjectUpdate,
) -> tuple[Project, ProjectUpdate]:
    """Check given data are valid ones.

    Check there are no other projects with the same site name. Avoid to change
    project visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical uuid, belonging to the same
    provider, already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.uuid is not None and new_data.uuid != item.uuid:
        try:
            provider = item.provider.single()
        except CardinalityViolation as e:
            msg = (
                f"Corrupted DB: Project with uuid '{item.uuid}' has no linked provider"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            ) from e
        db_item = provider.projects.get_or_none(uuid=new_data.uuid)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project with uuid '{item.uuid}' already registered",
            )
    return item, new_data
