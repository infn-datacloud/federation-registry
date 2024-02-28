from typing import Any, List, Literal, Optional, Tuple, Union

import pytest
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.location.schemas import LocationCreate
from fed_reg.models import BaseNode, BaseNodeCreate, BaseNodeQuery
from fed_reg.provider.schemas_extended import (
    BlockStorageServiceCreateExtended,
    ComputeServiceCreateExtended,
    NetworkServiceCreateExtended,
    RegionCreateExtended,
)
from fed_reg.region.schemas import (
    RegionBase,
    RegionBasePublic,
    RegionCreate,
    RegionQuery,
    RegionUpdate,
)
from fed_reg.service.schemas import IdentityServiceCreate
from tests.create_dict import (
    region_schema_dict,
)
from tests.utils import random_lower_string, random_url


class CaseAttr:
    @case(tags=["base_public", "update"])
    def case_none(self) -> Tuple[None, None]:
        return None, None

    @case(tags=["base_public"])
    def case_desc(self) -> Tuple[Literal["description"], str]:
        return "description", random_lower_string()

    @case(tags=["create_extended"])
    @parametrize(
        type=[
            "block_storage_services",
            "compute_services",
            "identity_services",
            "network_services",
        ]
    )
    @parametrize(len=[0, 1, 2])
    def case_services(
        self,
        block_storage_service_create_ext_schema: BlockStorageServiceCreateExtended,
        compute_service_create_ext_schema: ComputeServiceCreateExtended,
        identity_service_create_schema: IdentityServiceCreate,
        network_service_create_ext_schema: NetworkServiceCreateExtended,
        type: str,
        len: int,
    ) -> Tuple[
        str,
        Union[
            List[BlockStorageServiceCreateExtended],
            List[ComputeServiceCreateExtended],
            List[IdentityServiceCreate],
            List[NetworkServiceCreateExtended],
        ],
    ]:
        if len > 0:
            if type == "block_storage_services":
                service = block_storage_service_create_ext_schema
            elif type == "compute_services":
                service = compute_service_create_ext_schema
            elif type == "identity_services":
                service = identity_service_create_schema
            elif type == "network_services":
                service = network_service_create_ext_schema

            if len == 1:
                return type, [service]
            elif len == 2:
                service2 = service.copy()
                service2.endpoint = random_url()
                return type, [service, service2]
        else:
            return type, []

    @case(tags=["create_extended"])
    @parametrize(with_loc=[True, False])
    def case_location(
        self, location_create_schema: LocationCreate, with_loc: bool
    ) -> Tuple[Literal["location"], Optional[LocationCreate]]:
        if with_loc:
            return "location", location_create_schema
        else:
            return "location", None


class CaseInvalidAttr:
    @case(tags=["base_public", "update"])
    def case_attr(self) -> Tuple[Literal["name"], None]:
        return "name", None

    @case(tags=["create_extended"])
    @parametrize(
        type=[
            "block_storage_services",
            "compute_services",
            "identity_services",
            "network_services",
        ]
    )
    def case_services(
        self,
        block_storage_service_create_ext_schema: BlockStorageServiceCreateExtended,
        compute_service_create_ext_schema: ComputeServiceCreateExtended,
        identity_service_create_schema: IdentityServiceCreate,
        network_service_create_ext_schema: NetworkServiceCreateExtended,
        type: str,
    ) -> Tuple[
        str,
        Union[
            List[BlockStorageServiceCreateExtended],
            List[ComputeServiceCreateExtended],
            List[IdentityServiceCreate],
            List[NetworkServiceCreateExtended],
        ],
        str,
    ]:
        if type == "block_storage_services":
            service = block_storage_service_create_ext_schema
        elif type == "compute_services":
            service = compute_service_create_ext_schema
        elif type == "identity_services":
            service = identity_service_create_schema
        elif type == "network_services":
            service = network_service_create_ext_schema

        return (
            type,
            [service, service],
            "There are multiple items with identical endpoint",
        )


@parametrize_with_cases("key, value", cases=CaseAttr, has_tag=["base_public"])
def test_base_public(key: str, value: str) -> None:
    assert issubclass(RegionBasePublic, BaseNode)
    d = region_schema_dict()
    if key:
        d[key] = value
    item = RegionBasePublic(**d)
    assert item.description == d.get("description", "")
    assert item.name == d.get("name")


@parametrize_with_cases("key, value", cases=CaseInvalidAttr, has_tag=["base_public"])
def test_invalid_base_public(key: str, value: None) -> None:
    d = region_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        RegionBasePublic(**d)


@parametrize_with_cases(
    "key, value", cases=CaseAttr, filter=lambda f: not f.has_tag("create_extended")
)
def test_base(key: str, value: Any) -> None:
    assert issubclass(RegionBase, RegionBasePublic)
    d = region_schema_dict()
    if key:
        d[key] = value
    item = RegionBase(**d)
    assert item.name == d.get("name")


@parametrize_with_cases(
    "key, value",
    cases=CaseInvalidAttr,
    filter=lambda f: not f.has_tag("create_extended"),
)
def test_invalid_base(key: str, value: Any) -> None:
    d = region_schema_dict()
    d[key] = value
    with pytest.raises(ValueError):
        RegionBase(**d)


def test_create() -> None:
    assert issubclass(RegionCreate, BaseNodeCreate)
    assert issubclass(RegionCreate, RegionBase)


@parametrize_with_cases(
    "key, value", cases=[CaseInvalidAttr, CaseAttr], has_tag=["update"]
)
def test_update(key: str, value: Any) -> None:
    assert issubclass(RegionUpdate, BaseNodeCreate)
    assert issubclass(RegionUpdate, RegionBase)
    d = region_schema_dict()
    if key:
        d[key] = value
    item = RegionUpdate(**d)
    assert item.name == d.get("name")


def test_query() -> None:
    assert issubclass(RegionQuery, BaseNodeQuery)


@parametrize_with_cases("attr, values", cases=CaseAttr, has_tag=["create_extended"])
def test_create_extended(
    attr: str,
    values: Optional[
        Union[
            LocationCreate,
            List[BlockStorageServiceCreateExtended],
            List[ComputeServiceCreateExtended],
            List[IdentityServiceCreate],
            List[NetworkServiceCreateExtended],
        ]
    ],
) -> None:
    assert issubclass(RegionCreateExtended, RegionCreate)
    d = region_schema_dict()
    d[attr] = values
    item = RegionCreateExtended(**d)
    assert item.__getattribute__(attr) == values


@parametrize_with_cases(
    "attr, values, msg", cases=CaseInvalidAttr, has_tag=["create_extended"]
)
def test_invalid_create_extended(
    attr: str,
    values: Union[
        List[BlockStorageServiceCreateExtended],
        List[ComputeServiceCreateExtended],
        List[IdentityServiceCreate],
        List[NetworkServiceCreateExtended],
    ],
    msg: str,
) -> None:
    d = region_schema_dict()
    d[attr] = values
    with pytest.raises(ValueError, match=msg):
        RegionCreateExtended(**d)


# TODO Test all read classes
