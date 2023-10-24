from random import choice
from typing import List
from uuid import uuid4

from app.image.enum import ImageOS
from app.image.models import Image
from app.image.schemas import ImageUpdate
from app.provider.schemas_extended import ImageCreateExtended
from app.tests.utils.utils import random_bool, random_lower_string


def create_random_image(
    *, default: bool = False, projects: List[str] = []
) -> ImageCreateExtended:
    name = random_lower_string()
    uuid = uuid4()
    kwargs = {}
    if not default:
        kwargs = {
            "description": random_lower_string(),
            "os_type": random_os_type(),
            "os_distro": random_lower_string(),
            "os_version": random_lower_string(),
            "architecture": random_lower_string(),
            "is_public": len(projects) == 0,
            "kernel_id": random_lower_string(),
            "cuda_support": random_bool(),
            "gpu_driver": random_bool(),
            "tags": [random_lower_string()],
        }
        if len(projects) > 0:
            kwargs["projects"] = projects
    return ImageCreateExtended(name=name, uuid=uuid, **kwargs)


def create_random_image_patch(default: bool = False) -> ImageUpdate:
    if default:
        return ImageUpdate()
    description = random_lower_string()
    name = random_lower_string()
    uuid = uuid4()
    os_type = random_os_type()
    os_distro = random_lower_string()
    os_version = random_lower_string()
    architecture = random_lower_string()
    is_public = random_bool()
    kernel_id = random_lower_string()
    cuda_support = random_bool()
    gpu_driver = random_bool()
    tags = [random_lower_string()]
    return ImageUpdate(
        description=description,
        name=name,
        uuid=uuid,
        os_type=os_type,
        os_distro=os_distro,
        os_version=os_version,
        architecture=architecture,
        is_public=is_public,
        kernel_id=kernel_id,
        cuda_support=cuda_support,
        gpu_driver=gpu_driver,
        tags=tags,
    )


def random_os_type() -> str:
    return choice([i.value for i in ImageOS])


def validate_image_attrs(*, obj_in: ImageCreateExtended, db_item: Image) -> None:
    assert db_item.description == obj_in.description
    assert db_item.name == obj_in.name
    assert db_item.uuid == obj_in.uuid
    assert db_item.is_public == obj_in.is_public
    assert db_item.os_type == obj_in.os_type
    assert db_item.os_distro == obj_in.os_distro
    assert db_item.os_version == obj_in.os_version
    assert db_item.architecture == obj_in.architecture
    assert db_item.kernel_id == obj_in.kernel_id
    assert db_item.cuda_support == obj_in.cuda_support
    assert db_item.gpu_driver == obj_in.gpu_driver
    assert db_item.tags == obj_in.tags
    assert len(db_item.projects) == len(obj_in.projects)
    for db_proj, proj_in in zip(db_item.projects, obj_in.projects):
        assert db_proj.uuid == proj_in
