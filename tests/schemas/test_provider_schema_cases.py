from pytest_cases import case, parametrize

from fed_reg.provider.models import Provider
from fed_reg.provider.schemas import ProviderBase, ProviderCreate


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("name", "type"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base", "update"))
    @parametrize(value=("is_public", "status", "support_emails"))
    def case_optional(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("name", "type"))
    def case_missing_mandatory_public(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "read_public", "read"))
    @parametrize(value=("uid",))
    def case_missing_uid(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("not_a_type",))
    def case_invalid_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "read_public", "read"))
    @parametrize(value=("not_a_status", "not_an_email"))
    def case_optional(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[ProviderBase]:
        return ProviderBase

    @case(tags="class")
    def case_create_class(self) -> type[ProviderCreate]:
        return ProviderCreate


class CaseModel:
    @case(tags="model")
    def case_provider(self) -> type[Provider]:
        return Provider
