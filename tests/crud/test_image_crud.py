from typing import Any

import pytest
from neomodel.exceptions import MultipleNodesReturned
from pytest_cases import fixture, parametrize_with_cases

from fed_reg.crud import CRUDInterface
from fed_reg.image.crud import (
    CRUDImage,
    CRUDPrivateImage,
    CRUDSharedImage,
    image_mgr,
    private_image_mgr,
    shared_image_mgr,
)
from fed_reg.image.models import PrivateImage, SharedImage
from fed_reg.project.models import Project
from fed_reg.provider.schemas_extended import (
    PrivateImageCreateExtended,
    SharedImageCreateExtended,
)
from fed_reg.service.models import ComputeService
from tests.models.utils import image_model_dict, project_model_dict
from tests.schemas.utils import image_schema_dict


@fixture
@parametrize_with_cases("key, value", has_tag="create")
def image_create_dict(key: str, value: Any) -> dict[str, Any]:
    d = image_schema_dict()
    if key:
        d[key] = value
    return d


@fixture
@parametrize_with_cases("key, value", has_tag="get_single")
def image_get_dict(key: str, value: Any) -> dict[str, Any]:
    d = image_schema_dict()
    if key:
        d[key] = value
    return d


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDImage, CRUDInterface)
    assert issubclass(CRUDPrivateImage, CRUDInterface)
    assert issubclass(CRUDSharedImage, CRUDInterface)

    assert isinstance(image_mgr, CRUDImage)
    assert isinstance(private_image_mgr, CRUDPrivateImage)
    assert isinstance(shared_image_mgr, CRUDSharedImage)


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_create_shared(
    image_create_dict: dict[str, Any],
    compute_service_model: ComputeService,
    mgr: CRUDImage | CRUDSharedImage,
) -> None:
    image_schema = SharedImageCreateExtended(**image_create_dict)
    item = mgr.create(obj_in=image_schema, service=compute_service_model)
    assert isinstance(item, SharedImage)
    assert item.uid is not None
    assert item.description == image_schema.description
    assert item.name == image_schema.name
    assert item.uuid == image_schema.uuid
    assert item.os_type == image_schema.os_type
    assert item.os_distro == image_schema.os_distro
    assert item.os_version == image_schema.os_version
    assert item.architecture == image_schema.architecture
    assert item.kernel_id == image_schema.kernel_id
    assert item.cuda_support == image_schema.cuda_support
    assert item.gpu_driver == image_schema.gpu_driver
    assert item.tags == image_schema.tags
    assert len(item.services.all()) == 1
    assert item.services.single() == compute_service_model


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_create_private_single_project(
    image_create_dict: dict[str, Any],
    compute_service_model: ComputeService,
    project_model: Project,
    mgr: CRUDImage | CRUDPrivateImage,
) -> None:
    image_create_dict["projects"] = [project_model.uuid]
    image_schema = PrivateImageCreateExtended(**image_create_dict)
    item = mgr.create(
        obj_in=image_schema, service=compute_service_model, projects=[project_model]
    )
    assert isinstance(item, PrivateImage)
    assert item.uid is not None
    assert item.description == image_schema.description
    assert item.name == image_schema.name
    assert item.uuid == image_schema.uuid
    assert item.os_type == image_schema.os_type
    assert item.os_distro == image_schema.os_distro
    assert item.os_version == image_schema.os_version
    assert item.architecture == image_schema.architecture
    assert item.kernel_id == image_schema.kernel_id
    assert item.cuda_support == image_schema.cuda_support
    assert item.gpu_driver == image_schema.gpu_driver
    assert item.tags == image_schema.tags
    assert len(item.services.all()) == 1
    assert item.services.single() == compute_service_model
    assert len(item.projects.all()) == 1
    assert item.projects.single() == project_model


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_create_private_multi_projects(
    image_create_dict: dict[str, Any],
    compute_service_model: ComputeService,
    mgr: CRUDImage | CRUDPrivateImage,
) -> None:
    project_models = [
        Project(**project_model_dict()).save(),
        Project(**project_model_dict()).save(),
    ]
    image_create_dict["projects"] = [i.uuid for i in project_models]
    image_schema = PrivateImageCreateExtended(**image_create_dict)
    item = mgr.create(
        obj_in=image_schema, service=compute_service_model, projects=project_models
    )
    assert isinstance(item, PrivateImage)
    assert len(item.projects.all()) == 2


@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key", has_tag="mandatory")
def test_get_private_from_default_attr(
    private_image_model: PrivateImage,
    mgr: CRUDImage | CRUDSharedImage | CRUDPrivateImage,
    key: str,
) -> None:
    kwargs = {key: private_image_model.__getattribute__(key)}
    item = mgr.get(**kwargs)
    if isinstance(mgr, CRUDSharedImage):
        assert item is None
    else:
        assert isinstance(item, PrivateImage)
        assert item.uid == private_image_model.uid


@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key", has_tag="mandatory")
def test_get_shared_from_default_attr(
    shared_image_model: PrivateImage | SharedImage,
    mgr: CRUDImage | CRUDSharedImage | CRUDPrivateImage,
    key: str,
) -> None:
    kwargs = {key: shared_image_model.__getattribute__(key)}
    item = mgr.get(**kwargs)
    if isinstance(mgr, CRUDPrivateImage):
        assert item is None
    else:
        assert isinstance(item, SharedImage)
        assert item.uid == shared_image_model.uid


@parametrize_with_cases("image_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key, value", has_tag="get_single")
def test_get_none_because_not_matching(
    image_model: PrivateImage | SharedImage,
    mgr: CRUDImage | CRUDPrivateImage | CRUDSharedImage,
    key: str,
    value: Any,
) -> None:
    item = mgr.get(**{key: value})
    assert item is None


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_private_err_multi_match(
    private_image_model: PrivateImage, mgr: CRUDImage | CRUDPrivateImage
) -> None:
    PrivateImage(**image_model_dict()).save()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_shared_err_multi_match(
    shared_image_model: SharedImage, mgr: CRUDImage | CRUDSharedImage
) -> None:
    SharedImage(**image_model_dict()).save()
    with pytest.raises(MultipleNodesReturned):
        mgr.get()


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_only_one_shared(
    shared_image_model: SharedImage,
    image_get_dict: dict[str, Any],
    mgr: CRUDImage | CRUDSharedImage,
    current_cases,
) -> None:
    key = current_cases["image_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = image_get_dict[key]
        image_model = SharedImage(**image_get_dict).save()
        item = mgr.get(**{key: value})
        assert isinstance(item, SharedImage)
        assert item.uid == image_model.uid


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_only_one_private(
    private_image_model: PrivateImage,
    image_get_dict: dict[str, Any],
    mgr: CRUDImage | CRUDPrivateImage,
    current_cases,
) -> None:
    key = current_cases["image_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = image_get_dict[key]
        image_model = PrivateImage(**image_get_dict).save()
        item = mgr.get(**{key: value})
        assert isinstance(item, PrivateImage)
        assert item.uid == image_model.uid


@parametrize_with_cases("mgr", has_tag="manager")
def test_get_multi_from_default_attr(
    private_image_model: PrivateImage,
    shared_image_model: SharedImage,
    mgr: CRUDImage | CRUDPrivateImage | CRUDSharedImage,
) -> None:
    items = mgr.get_multi()
    if isinstance(mgr, CRUDPrivateImage):
        assert len(items) == 1
        assert isinstance(items[0], PrivateImage)
        assert items[0] == private_image_model
    elif isinstance(mgr, CRUDSharedImage):
        assert len(items) == 1
        assert isinstance(items[0], SharedImage)
        assert items[0] == shared_image_model
    else:
        assert len(items) == 2
        assert (
            isinstance(items[0], PrivateImage) and isinstance(items[1], SharedImage)
        ) or (isinstance(items[1], PrivateImage) and isinstance(items[0], SharedImage))


@parametrize_with_cases("image_model", has_tag="model")
@parametrize_with_cases("mgr", has_tag="manager")
@parametrize_with_cases("key, value", has_tag="get_single")
def test_get_empty_list_because_not_matching(
    image_model: PrivateImage | SharedImage,
    mgr: CRUDImage | CRUDPrivateImage | CRUDSharedImage,
    key: str,
    value: Any,
) -> None:
    items = mgr.get_multi(**{key: value})
    assert len(items) == 0


@parametrize_with_cases("mgr", has_tag=("manager", "private"))
def test_get_only_one_private_from_multi(
    private_image_model: PrivateImage,
    image_get_dict: dict[str, Any],
    mgr: CRUDImage | CRUDPrivateImage,
    current_cases,
) -> None:
    key = current_cases["image_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = image_get_dict[key]
        image_model = PrivateImage(**image_get_dict).save()
        items = mgr.get_multi(**{key: value})
        assert len(items) == 1
        assert isinstance(items[0], PrivateImage)
        assert items[0].uid == image_model.uid


@parametrize_with_cases("mgr", has_tag=("manager", "shared"))
def test_get_only_one_shared_from_multi(
    shared_image_model: SharedImage,
    image_get_dict: dict[str, Any],
    mgr: CRUDImage | CRUDSharedImage,
    current_cases,
) -> None:
    key = current_cases["image_get_dict"]["key"].params.get("attr", None)
    if key is not None:
        value = image_get_dict[key]
        image_model = SharedImage(**image_get_dict).save()
        items = mgr.get_multi(**{key: value})
        assert len(items) == 1
        assert isinstance(items[0], SharedImage)
        assert items[0].uid == image_model.uid
