from uuid import UUID

import pytest
from neomodel.exceptions import CardinalityViolation
from pytest_cases import parametrize_with_cases

from fed_reg.flavor.models import Flavor
from fed_reg.flavor.schemas_extended import FlavorReadExtended
from fed_reg.provider.schemas_extended import FlavorCreateExtended
from tests.create_dict import flavor_schema_dict


@parametrize_with_cases("projects", has_tag="valid_create")
def test_create_extended(projects: list[UUID]) -> None:
    d = flavor_schema_dict()
    d["is_public"] = len(projects) == 0
    d["projects"] = projects
    item = FlavorCreateExtended(**d)
    assert item.projects == [i.hex for i in projects]


@parametrize_with_cases("projects, msg", has_tag="invalid_create")
def test_invalid_create_extended(projects: list[UUID], msg: str) -> None:
    d = flavor_schema_dict()
    d["is_public"] = True if len(projects) == 1 else False
    d["projects"] = projects
    with pytest.raises(ValueError, match=msg):
        FlavorCreateExtended(**d)


@parametrize_with_cases("child, parent", has_tag="inheritance")
def test_derived_read_schemas(child, parent) -> None:
    assert issubclass(child, parent)
    assert child.__config__.orm_mode


@parametrize_with_cases("flavor", has_tag="valid_read")
def test_read_extended(flavor: Flavor) -> None:
    item = FlavorReadExtended.from_orm(flavor)
    assert len(item.services) > 0
    if item.is_public:
        assert len(item.projects) == 0
    else:
        assert len(item.projects) > 0


@parametrize_with_cases("flavor", has_tag="invalid_read")
def test_read_missing_connection(flavor: Flavor) -> None:
    with pytest.raises(CardinalityViolation):
        FlavorReadExtended.from_orm(flavor)
