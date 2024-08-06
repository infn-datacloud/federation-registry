from pytest_cases import case, parametrize

from fed_reg.project.models import Project
from fed_reg.project.schemas import ProjectBase, ProjectCreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("name", "uuid"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("name", "uuid"))
    def case_missing_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "read_public", "read"))
    @parametrize(value=("uid",))
    def case_missing_uid(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[ProjectBase]:
        return ProjectBase

    @case(tags="class")
    def case_create_class(self) -> type[ProjectCreate]:
        return ProjectCreate


class CaseModel:
    @case(tags="model")
    def case_project(self) -> type[Project]:
        return Project
