from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.identity_provider.models import IdentityProvider
from fed_reg.identity_provider.schemas import (
    IdentityProviderBase,
    IdentityProviderCreate,
)
from tests.schemas.utils import identity_provider_schema_dict
from tests.utils import random_lower_string


class CaseIdentityProviderSchema:
    @case(tags=("dict", "valid", "base_public"))
    def case_mandatory_public(self) -> dict[str, Any]:
        d = identity_provider_schema_dict()
        d.pop("group_claim")
        return d

    @case(tags=("dict", "valid", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return identity_provider_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**identity_provider_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_endpoint(self) -> tuple[dict[str, Any], Literal["endpoint"]]:
        d = identity_provider_schema_dict()
        d.pop("endpoint")
        return d, "endpoint"

    @case(tags=("dict", "invalid", "base", "read"))
    def case_missing_group_claim(self) -> tuple[dict[str, Any], Literal["group_claim"]]:
        d = identity_provider_schema_dict()
        d.pop("group_claim")
        return d, "group_claim"

    @case(tags="class")
    def case_base_class(self) -> type[IdentityProviderBase]:
        return IdentityProviderBase

    @case(tags="class")
    def case_create_class(self) -> type[IdentityProviderCreate]:
        return IdentityProviderCreate


class CaseIdentityProviderModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseIdentityProviderSchema, has_tag=("dict", "valid", "base")
    )
    def case_identity_provider_model(self, data: dict[str, Any]) -> IdentityProvider:
        return IdentityProvider(**IdentityProviderBase(**data).dict()).save()
