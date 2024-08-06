from typing import Any

import pytest
from pytest_cases import parametrize_with_cases

from fed_reg.service.models import IdentityService
from fed_reg.service.schemas import IdentityServiceBase, IdentityServiceRead
from tests.schemas.utils import identity_service_schema_dict


@parametrize_with_cases("key, value")
def test_invalid_base(key: str, value: Any) -> None:
    d = identity_service_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        IdentityServiceBase(**d)


@parametrize_with_cases("key, value")
def test_invalid_read(
    identity_service_model: IdentityService, key: str, value: str
) -> None:
    identity_service_model.__setattr__(key, value)
    with pytest.raises(ValueError):
        IdentityServiceRead.from_orm(identity_service_model)
