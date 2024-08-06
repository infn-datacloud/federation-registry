from typing import Any

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    NetworkQuotaCreateExtended,
    NetworkServiceCreateExtended,
)
from fed_reg.service.models import NetworkService
from fed_reg.service.schemas import NetworkServiceBase, NetworkServiceRead
from tests.schemas.utils import network_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_base(key: str, value: Any) -> None:
    d = network_service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        NetworkServiceBase(**d)


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_read(
    network_service_model: NetworkService, key: str, value: str
) -> None:
    network_service_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        NetworkServiceRead.from_orm(network_service_model)


@parametrize_with_cases("attr, values, msg", has_tag="create_extended")
def test_invalid_create_extended(
    attr: str, values: list[NetworkQuotaCreateExtended], msg: str
) -> None:
    d = network_service_schema_dict()
    d[attr] = values
    with pytest.raises(ValueError, match=msg):
        NetworkServiceCreateExtended(**d)
