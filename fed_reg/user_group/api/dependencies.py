"""UserGroup REST API dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import UserGroupUpdate
from neomodel.exceptions import CardinalityViolation

from fed_reg.dependencies import valid_id
from fed_reg.user_group.crud import user_group_mgr


def user_group_must_exist(user_group_uid: str) -> UserGroup:
    """The target user group must exists otherwise raises `not found` error."""
    return valid_id(mgr=user_group_mgr, item_id=user_group_uid)


def get_user_group_item(user_group_uid: str) -> UserGroup:
    """Retrieve the target user group. If not found, return None."""
    return valid_id(mgr=user_group_mgr, item_id=user_group_uid, error=False)


def validate_new_user_group_values(
    item: Annotated[UserGroup, Depends(user_group_must_exist)],
    new_data: UserGroupUpdate,
) -> tuple[UserGroup, UserGroupUpdate]:
    """Check given data are valid ones.

    Check there are no other user_groups, belonging to the same identity provider, with
    the same name. Avoid to change user group visibility.

    Raises `not found` error if the target entity does not exists.
    It raises `conflict` error if a DB entity with identical name and belonging to the
    same identity provider already exists.

    Return the current item and the schema with the new data.
    """
    if new_data.name is not None and new_data.name != item.name:
        try:
            idp = item.identity_provider.single()
        except CardinalityViolation as e:
            msg = (
                f"Corrupted DB: User group with uuid '{item.uuid}' has no linked "
                "identity provider"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg
            ) from e
        db_item = idp.user_groups.get_or_none(name=new_data.name)
        if db_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User group with name '{item.name}' already registered",
            )
    return item, new_data
