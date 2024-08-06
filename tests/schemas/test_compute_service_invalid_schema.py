from typing import Any

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.provider.schemas_extended import (
    ComputeQuotaCreateExtended,
    ComputeServiceCreateExtended,
)
from fed_reg.service.models import ComputeService
from fed_reg.service.schemas import ComputeServiceBase, ComputeServiceRead
from tests.schemas.utils import compute_service_schema_dict


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_base(key: str, value: Any) -> None:
    d = compute_service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        ComputeServiceBase(**d)


@parametrize_with_cases("key, value", has_tag="base")
def test_invalid_read(
    compute_service_model: ComputeService, key: str, value: str
) -> None:
    compute_service_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        ComputeServiceRead.from_orm(compute_service_model)


@parametrize_with_cases("attr, values, msg", has_tag="create_extended")
def test_invalid_create_extended(
    attr: str, values: list[ComputeQuotaCreateExtended], msg: str
) -> None:
    d = compute_service_schema_dict()
    d[attr] = values
    with pytest.raises(ValueError, match=msg):
        ComputeServiceCreateExtended(**d)
