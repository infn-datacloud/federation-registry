from typing import Any

import pytest
from neomodel.exceptions import MultipleNodesReturned
from pytest_cases import fixture, parametrize_with_cases

from fed_reg.network.crud import CRUDNetwork, CRUDPrivateNetwork, CRUDSharedNetwork
from fed_reg.network.models import PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    PrivateNetworkCreateExtended,
    SharedNetworkCreateExtended,
)
from fed_reg.service.models import NetworkService
from tests.models.utils import network_model_dict
from tests.schemas.utils import network_schema_dict


@fixture
@parametrize_with_cases("key, value", has_tag="create")
def network_create_dict(key: str, value: Any) -> dict[str, Any]:
    d = network_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    return d


@fixture
@parametrize_with_cases("key, value", has_tag="get_single")
def network_get_dict(key: str, value: Any) -> dict[str, Any]:
    d = network_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    return d


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_create_shared(
    network_create_dict: dict[str, Any],
    network_service_model: NetworkService,
    mgr: CRUDNetwork | CRUDSharedNetwork,
) -> None:
    network_schema = SharedNetworkCreateExtended(**network_create_dict)
    item = mgr.create(obj_in=network_schema, service=network_service_model)
    assert isinstance(item, SharedNetwork)
    assert item.uid is not None
    assert item.description == network_schema.description
    assert item.name == network_schema.name
    assert item.uuid == network_schema.uuid
    assert item.is_router_external == network_schema.is_router_external
    assert item.is_default == network_schema.is_default
    assert item.mtu == network_schema.mtu
    assert item.proxy_host == network_schema.proxy_host
    assert item.proxy_user == network_schema.proxy_user
    assert item.tags == network_schema.tags
    assert len(item.service.all()) == 1
    assert item.service.single() == network_service_model


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_create_private_single_project(
    network_create_dict: dict[str, Any],
    network_service_model: NetworkService,
    project_model: Project,
    mgr: CRUDNetwork | CRUDPrivateNetwork,
) -> None:
    network_create_dict["project"] = project_model.uuid
    network_schema = PrivateNetworkCreateExtended(**network_create_dict)
    item = mgr.create(
        obj_in=network_schema, service=network_service_model, project=project_model
    )
    assert isinstance(item, PrivateNetwork)
    assert item.uid is not None
    assert item.description == network_schema.description
    assert item.name == network_schema.name
    assert item.uuid == network_schema.uuid
    assert item.is_router_external == network_schema.is_router_external
    assert item.is_default == network_schema.is_default
    assert item.mtu == network_schema.mtu
    assert item.proxy_host == network_schema.proxy_host
    assert item.proxy_user == network_schema.proxy_user
    assert item.tags == network_schema.tags
    assert len(item.service.all()) == 1
    assert item.service.single() == network_service_model
    assert len(item.project.all()) == 1
    assert item.project.single() == project_model


@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key", has_tag="mandatory")
def test_get_private_from_default_attr(
    private_network_model: PrivateNetwork,
    mgr: CRUDNetwork | CRUDSharedNetwork | CRUDPrivateNetwork,
    key: str,
) -> None:
    kwargs = {key: private_network_model.__getattribute__(key)}
    item = mgr.get(**kwargs)
    if isinstance(mgr, CRUDSharedNetwork):
        assert item is None
    else:
        assert isinstance(item, PrivateNetwork)
        assert item.uid == private_network_model.uid


@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key", has_tag="mandatory")
def test_get_shared_from_default_attr(
    shared_network_model: PrivateNetwork | SharedNetwork,
    mgr: CRUDNetwork | CRUDSharedNetwork | CRUDPrivateNetwork,
    key: str,
) -> None:
    kwargs = {key: shared_network_model.__getattribute__(key)}
    item = mgr.get(**kwargs)
    if isinstance(mgr, CRUDPrivateNetwork):
        assert item is None
    else:
        assert isinstance(item, SharedNetwork)
        assert item.uid == shared_network_model.uid


@parametrize_with_cases("network_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key, value", has_tag="get_single")
def test_get_none_because_not_matching(
    network_model: PrivateNetwork | SharedNetwork,
    mgr: CRUDNetwork | CRUDPrivateNetwork | CRUDSharedNetwork,
    key: str,
    value: Any,
) -> None:
    item = mgr.get(**{key: value})
    assert item is None


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_private_err_multi_match(
    private_network_model: PrivateNetwork, mgr: CRUDNetwork | CRUDPrivateNetwork
) -> None:
    PrivateNetwork(**network_model_dict()).save()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_shared_err_multi_match(
    shared_network_model: SharedNetwork, mgr: CRUDNetwork | CRUDSharedNetwork
) -> None:
    SharedNetwork(**network_model_dict()).save()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_only_one_shared(
    shared_network_model: SharedNetwork,
    network_get_dict: dict[str, Any],
    mgr: CRUDNetwork | CRUDSharedNetwork,
    current_cases,
) -> None:
    key = current_cases["network_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = network_get_dict[key]
        network_model = SharedNetwork(**network_get_dict).save()
        item = mgr.get(**{key: value})
        assert isinstance(item, SharedNetwork)
        assert item.uid == network_model.uid


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_only_one_private(
    private_network_model: PrivateNetwork,
    network_get_dict: dict[str, Any],
    mgr: CRUDNetwork | CRUDPrivateNetwork,
    current_cases,
) -> None:
    key = current_cases["network_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = network_get_dict[key]
        network_model = PrivateNetwork(**network_get_dict).save()
        item = mgr.get(**{key: value})
        assert isinstance(item, PrivateNetwork)
        assert item.uid == network_model.uid


@parametrize_with_cases("mgr", has_tag="manager")
def test_get_multi_from_default_attr(
    private_network_model: PrivateNetwork,
    shared_network_model: SharedNetwork,
    mgr: CRUDNetwork | CRUDPrivateNetwork | CRUDSharedNetwork,
) -> None:
    items = mgr.get_multi()
    if isinstance(mgr, CRUDPrivateNetwork):
        assert len(items) == 1
        assert isinstance(items[0], PrivateNetwork)
        assert items[0] == private_network_model
    elif isinstance(mgr, CRUDSharedNetwork):
        assert len(items) == 1
        assert isinstance(items[0], SharedNetwork)
        assert items[0] == shared_network_model
    else:
        assert len(items) == 2
        assert (
            isinstance(items[0], PrivateNetwork) and isinstance(items[1], SharedNetwork)
        ) or (
            isinstance(items[1], PrivateNetwork) and isinstance(items[0], SharedNetwork)
        )


@parametrize_with_cases("network_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key, value", has_tag="get_single")
def test_get_empty_list_because_not_matching(
    network_model: PrivateNetwork | SharedNetwork,
    mgr: CRUDNetwork | CRUDPrivateNetwork | CRUDSharedNetwork,
    key: str,
    value: Any,
) -> None:
    items = mgr.get_multi(**{key: value})
    assert len(items) == 0


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_only_one_private_from_multi(
    private_network_model: PrivateNetwork,
    network_get_dict: dict[str, Any],
    mgr: CRUDNetwork | CRUDPrivateNetwork,
    current_cases,
) -> None:
    key = current_cases["network_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = network_get_dict[key]
        network_model = PrivateNetwork(**network_get_dict).save()
        items = mgr.get_multi(**{key: value})
        assert len(items) == 1
        assert isinstance(items[0], PrivateNetwork)
        assert items[0].uid == network_model.uid


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_only_one_shared_from_multi(
    shared_network_model: SharedNetwork,
    network_get_dict: dict[str, Any],
    mgr: CRUDNetwork | CRUDSharedNetwork,
    current_cases,
) -> None:
    key = current_cases["network_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = network_get_dict[key]
        network_model = SharedNetwork(**network_get_dict).save()
        items = mgr.get_multi(**{key: value})
        assert len(items) == 1
        assert isinstance(items[0], SharedNetwork)
        assert items[0].uid == network_model.uid
