from typing import Any

import pytest
from neomodel.exceptions import MultipleNodesReturned
from pytest_cases import parametrize_with_cases

from fed_reg.crud import CRUDInterface
from fed_reg.flavor.crud import (
    CRUDFlavor,
    CRUDPrivateFlavor,
    CRUDSharedFlavor,
    flavor_mgr,
    private_flavor_mgr,
    shared_flavor_mgr,
)
from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.flavor.schemas import FlavorUpdate, PrivateFlavorCreate, SharedFlavorCreate
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    PrivateFlavorCreateExtended,
    SharedFlavorCreateExtended,
)
from fed_reg.service.models import ComputeService
from tests.models.utils import flavor_model_dict, project_model_dict
from tests.schemas.utils import flavor_schema_dict


@pytest.fixture
@parametrize_with_cases("key, value", has_tag="create")
def flavor_create_dict(key: str, value: Any) -> dict[str, Any]:
    d = flavor_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    return d


@pytest.fixture
@parametrize_with_cases("key, value", has_tag="get_single")
def flavor_read_dict(key: str, value: Any) -> dict[str, Any]:
    d = flavor_schema_dict()
    if key:
        d[key] = value
        if key.startswith("gpu_"):
            d["gpus"] = 1
    return d


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDFlavor, CRUDInterface)
    assert issubclass(CRUDPrivateFlavor, CRUDInterface)
    assert issubclass(CRUDSharedFlavor, CRUDInterface)

    assert isinstance(flavor_mgr, CRUDFlavor)
    assert isinstance(private_flavor_mgr, CRUDPrivateFlavor)
    assert isinstance(shared_flavor_mgr, CRUDSharedFlavor)

    assert flavor_mgr.model == Flavor
    assert flavor_mgr.schema_create is None
    assert private_flavor_mgr.model == PrivateFlavor
    assert private_flavor_mgr.schema_create == PrivateFlavorCreate
    assert shared_flavor_mgr.model == SharedFlavor
    assert shared_flavor_mgr.schema_create == SharedFlavorCreate


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_create_shared(
    flavor_create_dict: dict[str, Any],
    compute_service_model: ComputeService,
    mgr: CRUDFlavor | CRUDSharedFlavor,
) -> None:
    """Create shared flavor.

    In each case, provide a possible attribute and double check it.
    Test this method for both CRUDFlavor and CRUDSharedFlavor.
    """
    flavor_schema = SharedFlavorCreateExtended(**flavor_create_dict)
    item = mgr.create(obj_in=flavor_schema, service=compute_service_model)
    assert isinstance(item, SharedFlavor)
    assert item.uid is not None
    assert item.description == flavor_schema.description
    assert item.name == flavor_schema.name
    assert item.uuid == flavor_schema.uuid
    assert item.disk == flavor_schema.disk
    assert item.ram == flavor_schema.ram
    assert item.vcpus == flavor_schema.vcpus
    assert item.swap == flavor_schema.swap
    assert item.ephemeral == flavor_schema.ephemeral
    assert item.infiniband == flavor_schema.infiniband
    assert item.gpus == flavor_schema.gpus
    assert item.gpu_model == flavor_schema.gpu_model
    assert item.gpu_vendor == flavor_schema.gpu_vendor
    assert item.local_storage == flavor_schema.local_storage
    assert len(item.services.all()) == 1
    assert item.services.single() == compute_service_model


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_create_private_single_project(
    flavor_create_dict: dict[str, Any],
    compute_service_model: ComputeService,
    project_model: Project,
    mgr: CRUDFlavor | CRUDPrivateFlavor,
) -> None:
    """Create private flavor with a single project.

    In each case, provide a possible attribute and double check it.
    Assert project is only one.
    Test this method for both CRUDFlavor and CRUDPrivateFlavor.
    """
    flavor_create_dict["projects"] = [project_model.uuid]
    flavor_schema = PrivateFlavorCreateExtended(**flavor_create_dict)
    item = mgr.create(
        obj_in=flavor_schema, service=compute_service_model, projects=[project_model]
    )
    assert isinstance(item, PrivateFlavor)
    assert item.uid is not None
    assert item.description == flavor_schema.description
    assert item.name == flavor_schema.name
    assert item.uuid == flavor_schema.uuid
    assert item.disk == flavor_schema.disk
    assert item.ram == flavor_schema.ram
    assert item.vcpus == flavor_schema.vcpus
    assert item.swap == flavor_schema.swap
    assert item.ephemeral == flavor_schema.ephemeral
    assert item.infiniband == flavor_schema.infiniband
    assert item.gpus == flavor_schema.gpus
    assert item.gpu_model == flavor_schema.gpu_model
    assert item.gpu_vendor == flavor_schema.gpu_vendor
    assert item.local_storage == flavor_schema.local_storage
    assert len(item.services.all()) == 1
    assert item.services.single() == compute_service_model
    assert len(item.projects.all()) == 1
    assert item.projects.single() == project_model


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_create_private_multi_projects(
    flavor_create_dict: dict[str, Any],
    compute_service_model: ComputeService,
    mgr: CRUDFlavor | CRUDPrivateFlavor,
) -> None:
    """Create private flavor with multiple projects.

    Assert projects are exactly two.
    Test this method for both CRUDFlavor and CRUDPrivateFlavor.
    """
    project_models = [
        Project(**project_model_dict()).save(),
        Project(**project_model_dict()).save(),
    ]
    flavor_create_dict["projects"] = [i.uuid for i in project_models]
    flavor_schema = PrivateFlavorCreateExtended(**flavor_create_dict)
    item = mgr.create(
        obj_in=flavor_schema, service=compute_service_model, projects=project_models
    )
    assert isinstance(item, PrivateFlavor)
    assert len(item.projects.all()) == 2


@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key", has_tag="mandatory")
def test_get_private_from_default_attr(
    private_flavor_model: PrivateFlavor,
    mgr: CRUDFlavor | CRUDSharedFlavor | CRUDPrivateFlavor,
    key: str,
) -> None:
    kwargs = {key: private_flavor_model.__getattribute__(key)}
    item = mgr.get(**kwargs)
    if isinstance(mgr, CRUDSharedFlavor):
        assert item is None
    else:
        assert isinstance(item, PrivateFlavor)
        assert item.uid == private_flavor_model.uid


@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key", has_tag="mandatory")
def test_get_shared_from_default_attr(
    shared_flavor_model: PrivateFlavor | SharedFlavor,
    mgr: CRUDFlavor | CRUDSharedFlavor | CRUDPrivateFlavor,
    key: str,
) -> None:
    kwargs = {key: shared_flavor_model.__getattribute__(key)}
    item = mgr.get(**kwargs)
    if isinstance(mgr, CRUDPrivateFlavor):
        assert item is None
    else:
        assert isinstance(item, SharedFlavor)
        assert item.uid == shared_flavor_model.uid


@parametrize_with_cases("flavor_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key, value", has_tag="get_single")
def test_get_none_because_not_matching(
    flavor_model: PrivateFlavor | SharedFlavor,
    mgr: CRUDFlavor | CRUDPrivateFlavor | CRUDSharedFlavor,
    key: str,
    value: Any,
) -> None:
    item = mgr.get(**{key: value})
    assert item is None


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_private_err_multi_match(
    private_flavor_model: PrivateFlavor, mgr: CRUDFlavor | CRUDPrivateFlavor
) -> None:
    PrivateFlavor(**flavor_model_dict()).save()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_shared_err_multi_match(
    shared_flavor_model: SharedFlavor, mgr: CRUDFlavor | CRUDSharedFlavor
) -> None:
    SharedFlavor(**flavor_model_dict()).save()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_only_one_shared(
    shared_flavor_model: SharedFlavor,
    flavor_read_dict: dict[str, Any],
    mgr: CRUDFlavor | CRUDSharedFlavor,
    current_cases,
) -> None:
    key = current_cases["flavor_read_dict"]["key"].params["attr"]
    value = flavor_read_dict[key]
    flavor_model = SharedFlavor(**flavor_read_dict).save()
    item = mgr.get(**{key: value})
    assert isinstance(item, SharedFlavor)
    assert item.uid == flavor_model.uid


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_only_one_private(
    private_flavor_model: PrivateFlavor,
    flavor_read_dict: dict[str, Any],
    mgr: CRUDFlavor | CRUDPrivateFlavor,
    current_cases,
) -> None:
    key = current_cases["flavor_read_dict"]["key"].params["attr"]
    value = flavor_read_dict[key]
    flavor_model = PrivateFlavor(**flavor_read_dict).save()
    item = mgr.get(**{key: value})
    assert isinstance(item, PrivateFlavor)
    assert item.uid == flavor_model.uid


@parametrize_with_cases("mgr", has_tag="manager")
def test_get_multi_from_default_attr(
    private_flavor_model: PrivateFlavor,
    shared_flavor_model: SharedFlavor,
    mgr: CRUDFlavor | CRUDPrivateFlavor | CRUDSharedFlavor,
) -> None:
    items = mgr.get_multi()
    if isinstance(mgr, CRUDPrivateFlavor):
        assert len(items) == 1
        assert isinstance(items[0], PrivateFlavor)
        assert items[0] == private_flavor_model
    elif isinstance(mgr, CRUDSharedFlavor):
        assert len(items) == 1
        assert isinstance(items[0], SharedFlavor)
        assert items[0] == shared_flavor_model
    else:
        assert len(items) == 2
        assert (
            isinstance(items[0], PrivateFlavor) and isinstance(items[1], SharedFlavor)
        ) or (
            isinstance(items[1], PrivateFlavor) and isinstance(items[0], SharedFlavor)
        )


@parametrize_with_cases("flavor_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key, value", has_tag="get_single")
def test_get_empty_list_because_not_matching(
    flavor_model: PrivateFlavor | SharedFlavor,
    mgr: CRUDFlavor | CRUDPrivateFlavor | CRUDSharedFlavor,
    key: str,
    value: Any,
) -> None:
    items = mgr.get_multi(**{key: value})
    assert len(items) == 0


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_only_one_private_from_multi(
    private_flavor_model: PrivateFlavor,
    flavor_read_dict: dict[str, Any],
    mgr: CRUDFlavor | CRUDPrivateFlavor,
    current_cases,
) -> None:
    key = current_cases["flavor_read_dict"]["key"].params["attr"]
    value = flavor_read_dict[key]
    flavor_model = PrivateFlavor(**flavor_read_dict).save()
    items = mgr.get_multi(**{key: value})
    assert len(items) == 1
    assert isinstance(items[0], PrivateFlavor)
    assert items[0].uid == flavor_model.uid


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_only_one_shared_from_multi(
    shared_flavor_model: SharedFlavor,
    flavor_read_dict: dict[str, Any],
    mgr: CRUDFlavor | CRUDSharedFlavor,
    current_cases,
) -> None:
    key = current_cases["flavor_read_dict"]["key"].params["attr"]
    value = flavor_read_dict[key]
    flavor_model = SharedFlavor(**flavor_read_dict).save()
    items = mgr.get_multi(**{key: value})
    assert len(items) == 1
    assert isinstance(items[0], SharedFlavor)
    assert items[0].uid == flavor_model.uid


@parametrize_with_cases("flavor_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
def test_update_attr(
    flavor_model: PrivateFlavor | SharedFlavor,
    flavor_create_dict: dict[str, Any],
    mgr: CRUDFlavor | CRUDPrivateFlavor | CRUDSharedFlavor,
) -> None:
    flavor_schema = FlavorUpdate(**flavor_create_dict)
    item = mgr.update(db_obj=flavor_model, obj_in=flavor_schema)
    flavor_dict = flavor_schema.dict(exclude_unset=True)
    assert isinstance(item, type(flavor_model))
    assert item.uid is not None
    assert item.description == flavor_dict.get("description", flavor_schema.description)
    assert item.name == flavor_dict.get("name", flavor_schema.name)
    assert item.uuid == flavor_dict.get("uuid", flavor_schema.uuid)
    assert item.disk == flavor_dict.get("disk", flavor_schema.disk)
    assert item.ram == flavor_dict.get("ram", flavor_schema.ram)
    assert item.vcpus == flavor_dict.get("vcpus", flavor_schema.vcpus)
    assert item.swap == flavor_dict.get("swap", flavor_schema.swap)
    assert item.ephemeral == flavor_dict.get("ephemeral", flavor_schema.ephemeral)
    assert item.infiniband == flavor_dict.get("infiniband", flavor_schema.infiniband)
    assert item.gpus == flavor_dict.get("gpus", flavor_schema.gpus)
    assert item.gpu_model == flavor_dict.get("gpu_model", flavor_schema.gpu_model)
    assert item.gpu_vendor == flavor_dict.get("gpu_vendor", flavor_schema.gpu_vendor)
    assert item.local_storage == flavor_dict.get(
        "local_storage", flavor_schema.local_storage
    )


@parametrize_with_cases("flavor_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
def test_delete(
    flavor_model: PrivateFlavor | SharedFlavor,
    mgr: CRUDFlavor | CRUDPrivateFlavor | CRUDSharedFlavor,
) -> None:
    assert mgr.remove(db_obj=flavor_model)
    assert flavor_model.deleted

    with pytest.raises(ValueError, match="attempted on deleted node"):
        mgr.remove(db_obj=flavor_model)
