from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.user_group.models import UserGroup
from fed_reg.user_group.schemas import UserGroupBase, UserGroupCreate
from tests.schemas.utils import user_group_schema_dict
from tests.utils import random_lower_string


class CaseUserGroupSchema:
    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return user_group_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**user_group_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = user_group_schema_dict()
        d.pop("name")
        return d, "name"

    @case(tags="class")
    def case_base_class(self) -> type[UserGroupBase]:
        return UserGroupBase

    @case(tags="class")
    def case_create_class(self) -> type[UserGroupCreate]:
        return UserGroupCreate


class CaseUserGroupModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseUserGroupSchema, has_tag=("dict", "valid", "base")
    )
    def case_flavor_model(self, data: dict[str, Any]) -> UserGroup:
        return UserGroup(**UserGroupBase(**data).dict()).save()
