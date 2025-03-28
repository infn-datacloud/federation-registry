from uuid import uuid4

import pytest
from fedreg.project.models import Project
from fedreg.project.schemas import ProjectCreate
from fedreg.provider.models import Provider
from pytest_cases import parametrize_with_cases

from fed_reg.project.crud import project_mgr
from tests.utils import random_lower_string, random_provider_type


@pytest.fixture
def provider_model() -> Provider:
    """Provider model."""
    return Provider(name=random_lower_string(), type=random_provider_type()).save()


@pytest.fixture
def project_model(provider_model: Provider) -> Project:
    """Project model linked to the same provider.

    Connected to a different provider.
    """
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider_model.projects.connect(project)
    return project


class CaseProject:
    def case_project_create(self) -> ProjectCreate:
        return ProjectCreate(name=random_lower_string(), uuid=uuid4())


@parametrize_with_cases("item", cases=CaseProject)
def test_create(item: ProjectCreate, provider_model: Provider) -> None:
    """Create a new istance"""
    db_obj = project_mgr.create(obj_in=item, provider=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Project)
    assert db_obj.provider.is_connected(provider_model)


@parametrize_with_cases("item", cases=CaseProject)
def test_create_same_uuid_diff_provider(
    item: ProjectCreate,
    provider_model: Provider,
    stand_alone_project_model: Project,
) -> None:
    """A project with the given uuid already exists but on a different provider."""
    item.uuid = stand_alone_project_model.uuid

    db_obj = project_mgr.create(obj_in=item, provider=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Project)
    assert db_obj.provider.is_connected(provider_model)


@parametrize_with_cases("item", cases=CaseProject)
def test_create_already_exists(item: ProjectCreate, project_model: Project) -> None:
    """A project with the given uuid on this provider already exists"""
    provider = project_model.provider.single()

    item.uuid = project_model.uuid

    msg = (
        f"A project with uuid {item.uuid} belonging to provider "
        f"{provider.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        project_mgr.create(obj_in=item, provider=provider)


@parametrize_with_cases("item", cases=CaseProject)
def test_update(item: ProjectCreate, project_model: Project) -> None:
    """Completely update the project attributes. Also override not set ones."""
    db_obj = project_mgr.update(obj_in=item, db_obj=project_model)

    assert db_obj is not None
    assert isinstance(db_obj, Project)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("item", cases=CaseProject)
def test_update_no_changes(item: ProjectCreate, project_model: Project) -> None:
    """The new item is equal to the existing one. No changes."""
    item.uuid = project_model.uuid
    item.name = project_model.name

    db_obj = project_mgr.update(obj_in=item, db_obj=project_model)

    assert db_obj is None
