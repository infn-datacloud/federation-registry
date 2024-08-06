from pytest_cases import case, parametrize

from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.identity_provider.schemas import (
    IdentityProviderBase,
    IdentityProviderCreate,
)


class CaseAttr:
    @case(tags=("attr", "mandatory", "base_public", "base", "update"))
    @parametrize(value=("endpoint",))
    def case_mandatory_public(self, value: str) -> str:
        return value

    @case(tags=("attr", "mandatory", "base", "update"))
    @parametrize(value=("endpoint",))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional", "base_public", "base", "update"))
    @parametrize(value=("description",))
    def case_description(self, value: str) -> str:
        return value


class CaseInvalidAttr:
    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("endpoint",))
    def case_missing_mandatory_public(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "read_public", "read"))
    @parametrize(value=("uid",))
    def case_missing_uid(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base_public", "base", "read_public", "read"))
    @parametrize(value=("not_an_endpoint",))
    def case_invalid_mandatory(self, value: str) -> str:
        return value

    @case(tags=("invalid_attr", "base", "read"))
    @parametrize(value=("group_claim",))
    def case_mandatory(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_base_class(self) -> type[IdentityProviderBase]:
        return IdentityProviderBase

    @case(tags="class")
    def case_create_class(self) -> type[IdentityProviderCreate]:
        return IdentityProviderCreate


class CaseModel:
    @case(tags="model")
    def case_identity_provider(self) -> type[IdentityProvider]:
        return IdentityProvider
