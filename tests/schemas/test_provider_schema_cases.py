from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.provider.models import Provider
from fed_reg.provider.schemas import ProviderBase, ProviderCreate
from tests.schemas.utils import provider_schema_dict, random_provider_status
from tests.utils import random_email, random_lower_string


class CaseProviderSchema:
    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return provider_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**provider_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_is_public(self) -> dict[str, Any]:
        return {**provider_schema_dict(), "is_public": True}

    @case(tags=("dict", "valid", "base", "update"))
    def case_status(self) -> dict[str, Any]:
        return {**provider_schema_dict(), "status": random_provider_status()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_support_emails(self) -> dict[str, Any]:
        return {**provider_schema_dict(), "support_emails": [random_email()]}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = provider_schema_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_type(self) -> tuple[dict[str, Any], Literal["type"]]:
        d = provider_schema_dict()
        d.pop("type")
        return d, "type"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_type(self) -> tuple[dict[str, Any], Literal["type"]]:
        d = provider_schema_dict()
        d["type"] = random_lower_string()
        return d, "type"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_status(self) -> tuple[dict[str, Any], Literal["status"]]:
        d = provider_schema_dict()
        d["status"] = random_lower_string()
        return d, "status"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_support_emails(
        self,
    ) -> tuple[dict[str, Any], Literal["support_emails"]]:
        d = provider_schema_dict()
        d["support_emails"] = [random_lower_string()]
        return d, "support_emails"

    @case(tags="class")
    def case_base_class(self) -> type[ProviderBase]:
        return ProviderBase

    @case(tags="class")
    def case_create_class(self) -> type[ProviderCreate]:
        return ProviderCreate


class CaseProviderModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseProviderSchema, has_tag=("dict", "valid", "base")
    )
    def case_provider_model(self, data: dict[str, Any]) -> Provider:
        return Provider(**ProviderBase(**data).dict()).save()
