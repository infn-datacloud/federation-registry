from typing import Any, Literal

from pytest_cases import case, parametrize_with_cases

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.flavor.schemas import FlavorBase, PrivateFlavorCreate, SharedFlavorCreate
from tests.schemas.utils import flavor_schema_dict
from tests.utils import random_lower_string, random_positive_int


class CaseFlavorSchema:
    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_mandatory(self) -> dict[str, Any]:
        return flavor_schema_dict()

    @case(tags=("dict", "valid", "base_public", "base", "update"))
    def case_description(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "description": random_lower_string()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_disk(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "disk": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_ram(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "ram": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_vcpus(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "vcpus": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_swap(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "swap": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_ephemeral(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "ephemeral": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_infiniband(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "infiniband": True}

    @case(tags=("dict", "valid", "base", "update"))
    def case_gpus(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "gpus": random_positive_int()}

    @case(tags=("dict", "valid", "base", "update"))
    def case_gpu_model(self) -> dict[str, Any]:
        return {
            **flavor_schema_dict(),
            "gpus": random_positive_int(),
            "gpu_model": random_lower_string(),
        }

    @case(tags=("dict", "valid", "base", "update"))
    def case_gpu_vendor(self) -> dict[str, Any]:
        return {
            **flavor_schema_dict(),
            "gpus": random_positive_int(),
            "gpu_vendor": random_lower_string(),
        }

    @case(tags=("dict", "valid", "base", "update"))
    def case_local_storage(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "local_storage": random_lower_string()}

    @case(tags=("dict", "valid"))
    def case_is_shared(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "is_shared": True}

    @case(tags=("dict", "valid"))
    def case_is_private(self) -> dict[str, Any]:
        return {**flavor_schema_dict(), "is_shared": False}

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_name(self) -> tuple[dict[str, Any], Literal["name"]]:
        d = flavor_schema_dict()
        d.pop("name")
        return d, "name"

    @case(tags=("dict", "invalid", "base_public", "base", "read_public", "read"))
    def case_missing_uuid(self) -> tuple[dict[str, Any], Literal["uuid"]]:
        d = flavor_schema_dict()
        d.pop("uuid")
        return d, "uuid"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_disk(self) -> tuple[dict[str, Any], Literal["disk"]]:
        d = flavor_schema_dict()
        d["disk"] = -1
        return d, "disk"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_ram(self) -> tuple[dict[str, Any], Literal["ram"]]:
        d = flavor_schema_dict()
        d["ram"] = -1
        return d, "ram"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_vcpus(self) -> tuple[dict[str, Any], Literal["vcpus"]]:
        d = flavor_schema_dict()
        d["vcpus"] = -1
        return d, "vcpus"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_swap(self) -> tuple[dict[str, Any], Literal["swap"]]:
        d = flavor_schema_dict()
        d["swap"] = -1
        return d, "swap"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_ephemeral(self) -> tuple[dict[str, Any], Literal["ephemeral"]]:
        d = flavor_schema_dict()
        d["ephemeral"] = -1
        return d, "ephemeral"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_gpus(self) -> tuple[dict[str, Any], Literal["gpus"]]:
        d = flavor_schema_dict()
        d["gpus"] = -1
        return d, "gpus"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_gpu_model(self) -> tuple[dict[str, Any], Literal["gpu_model"]]:
        d = flavor_schema_dict()
        d["gpu_model"] = random_lower_string()
        return d, "gpu_model"

    @case(tags=("dict", "invalid", "base", "update", "read"))
    def case_invalid_gpu_vendor(self) -> tuple[dict[str, Any], Literal["gpu_vendor"]]:
        d = flavor_schema_dict()
        d["gpu_vendor"] = random_lower_string()
        return d, "gpu_vendor"

    @case(tags="class")
    def case_flavor(self) -> type[FlavorBase]:
        return FlavorBase

    @case(tags="class")
    def case_private_flavor(self) -> type[PrivateFlavorCreate]:
        return PrivateFlavorCreate

    @case(tags="class")
    def case_shared_flavor(self) -> type[SharedFlavorCreate]:
        return SharedFlavorCreate


class CaseFlavorModel:
    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseFlavorSchema, has_tag=("dict", "valid", "base")
    )
    def case_flavor_model(self, data: dict[str, Any]) -> Flavor:
        return Flavor(**FlavorBase(**data).dict()).save()

    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseFlavorSchema, has_tag=("dict", "valid", "base")
    )
    def case_private_flavor_class(self, data: dict[str, Any]) -> PrivateFlavor:
        return PrivateFlavor(**PrivateFlavorCreate(**data).dict()).save()

    @case(tags="model")
    @parametrize_with_cases(
        "data", cases=CaseFlavorSchema, has_tag=("dict", "valid", "base")
    )
    def case_shared_flavor_class(self, data: dict[str, Any]) -> SharedFlavor:
        return SharedFlavor(**SharedFlavorCreate(**data).dict()).save()
