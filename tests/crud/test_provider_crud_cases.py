from typing import Literal

from pytest_cases import case, parametrize

from fed_reg.provider.enum import ProviderStatus, ProviderType
from fed_reg.provider.models import Provider
from tests.create_dict import provider_model_dict
from tests.utils import random_lower_string


class CaseAttr:
    @case(tags="base")
    def case_uid(self) -> Literal["uid"]:
        return "uid"

    @case(tags=("base", "not-uid", "not-enum"))
    @parametrize(value=["description", "name", "is_public", "support_emails"])
    def case_key(self, value: str) -> str:
        return value

    @case(tags=("base", "not-uid", "enum"))
    @parametrize(value=["type", "status"])
    def case_enum_key(self, value: str) -> str:
        return value


class CaseProvider:
    @case(tags="single")
    @parametrize(full=[True, False])
    def case_single_provider(self, full: bool) -> Provider:
        d = provider_model_dict()
        if full:
            d["status"] = ProviderStatus.ACTIVE
            d["description"] = random_lower_string()
            d["support_emails"] = [random_lower_string()]
        return Provider(**d).save()

    @case(tags="multi")
    @parametrize(len=[1, 2])
    def case_providers_list(self, len: int) -> list[Provider]:
        providers = []
        for _ in range(len):
            providers.append(Provider(**provider_model_dict()).save())
        return providers

    @case(tags="multi-single-match")
    def case_providers_list_single_match(self) -> list[Provider]:
        providers = []
        statuses = [i for i in ProviderStatus]
        types = [i for i in ProviderType]
        for i in range(2):
            d = provider_model_dict()
            d["type"] = types[i]
            d["is_public"] = bool(i % 2)
            d["status"] = statuses[i]
            d["description"] = random_lower_string()
            d["support_emails"] = [random_lower_string()]
            providers.append(Provider(**d).save())
        return providers

    @case(tags="multi-dup-matches")
    def case_providers_list_dup_matches(self) -> list[Provider]:
        d = provider_model_dict()
        d["status"] = ProviderStatus.ACTIVE
        return [Provider(**d).save(), Provider(**d).save()]
