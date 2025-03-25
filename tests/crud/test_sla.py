import re
from uuid import uuid4

import pytest
from fedreg.identity_provider.models import IdentityProvider
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import SLACreateExtended
from fedreg.sla.models import SLA
from fedreg.user_group.models import UserGroup
from neomodel import DoesNotExist
from pytest_cases import parametrize_with_cases

from fed_reg.sla.crud import sla_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_start_end_dates,
    random_url,
)


@pytest.fixture
def project_model() -> Project:
    """Region model."""
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.projects.connect(project)
    return project


@pytest.fixture
def user_group_model(project_model: Project) -> UserGroup:
    """User Group model.

    The parent identity provider is connected to the project's provider.
    """
    identity_provider = IdentityProvider(
        endpoint=str(random_url()), group_claim=random_lower_string()
    ).save()
    user_group = UserGroup(name=random_lower_string()).save()
    provider = project_model.provider.single()
    provider.identity_providers.connect(
        identity_provider,
        {"protocol": random_lower_string(), "idp_name": random_lower_string()},
    )
    identity_provider.user_groups.connect(user_group)
    return user_group


@pytest.fixture
def sla_model(user_group_model: UserGroup) -> SLA:
    """SLA model belonging to the same provider."""
    start_date, end_date = random_start_end_dates()
    sla = SLA(doc_uuid=str(uuid4()), start_date=start_date, end_date=end_date).save()
    identity_provider = user_group_model.identity_provider.single()
    provider = identity_provider.providers.single()
    project = provider.projects.single()
    user_group_model.slas.connect(sla)
    project.sla.connect(sla)
    return sla


class CaseSLA:
    def case_sla_create(self, project_model: Project) -> SLACreateExtended:
        """This SLA points to the project_model."""
        provider = project_model.provider.single()
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        start_date, end_date = random_start_end_dates()
        return SLACreateExtended(
            doc_uuid=uuid4(),
            start_date=start_date,
            end_date=end_date,
            project=project.uuid,
        )


@parametrize_with_cases("item", cases=CaseSLA)
def test_create(
    item: SLACreateExtended, project_model: Project, user_group_model: UserGroup
) -> None:
    """Create a new istance"""
    db_obj = sla_mng.create(
        obj_in=item, project=project_model, user_group=user_group_model
    )
    assert db_obj is not None
    assert isinstance(db_obj, SLA)
    assert db_obj.user_group.is_connected(user_group_model)
    assert db_obj.projects.is_connected(project_model)


@parametrize_with_cases("item", cases=CaseSLA)
def test_create_already_exists(
    item: SLACreateExtended,
    sla_model: SLA,
) -> None:
    """A sla with the given uuid already exists"""
    item.doc_uuid = sla_model.doc_uuid
    user_group = sla_model.user_group.single()
    project = sla_model.projects.single()
    msg = f"An SLA with document uuid {item.doc_uuid} already exists"
    with pytest.raises(AssertionError, match=msg):
        sla_mng.create(obj_in=item, project=project, user_group=user_group)


@parametrize_with_cases("item", cases=CaseSLA)
def test_create_replace_project(
    item: SLACreateExtended, sla_model: SLA, stand_alone_project_model: Project
) -> None:
    """Replace the previous sla linked to the target project."""
    user_group = sla_model.user_group.single()
    project = sla_model.projects.single()
    sla_model.projects.connect(stand_alone_project_model)

    db_obj = sla_mng.create(obj_in=item, project=project, user_group=user_group)

    assert db_obj is not None
    assert isinstance(db_obj, SLA)
    assert db_obj.user_group.is_connected(user_group)
    assert db_obj.projects.is_connected(project)
    assert sla_model.projects.is_connected(stand_alone_project_model)
    assert not sla_model.projects.is_connected(project)


@parametrize_with_cases("item", cases=CaseSLA)
def test_create_replace_project_and_remove_prev_sla(
    item: SLACreateExtended, sla_model: SLA
) -> None:
    """Replace the previous sla linked to the target project."""
    project = sla_model.projects.single()
    user_group = sla_model.user_group.single()

    db_obj = sla_mng.create(obj_in=item, project=project, user_group=user_group)

    assert db_obj is not None
    assert isinstance(db_obj, SLA)
    assert db_obj.user_group.is_connected(user_group)
    assert db_obj.projects.is_connected(project)
    assert not sla_model.projects.is_connected(project)
    with pytest.raises(DoesNotExist):
        sla_model.refresh()


@parametrize_with_cases("item", cases=CaseSLA)
def test_update(item: SLACreateExtended, sla_model: SLA) -> None:
    """Completely update the sla attributes. Also override not set ones.

    Connect SLA to another project of the same provider.
    """
    user_group = sla_model.user_group.single()
    project = sla_model.projects.single()
    provider = project.provider.single()
    projects = provider.projects.all()

    db_obj = sla_mng.update(obj_in=item, db_obj=sla_model, provider_projects=projects)

    assert db_obj is not None
    assert isinstance(db_obj, SLA)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.user_group.is_connected(user_group)
    assert len(db_obj.projects) == 1
    assert db_obj.projects.single().uuid == item.project


@parametrize_with_cases("item", cases=CaseSLA)
def test_update_connect_to_another_provider(
    item: SLACreateExtended, sla_model: SLA, stand_alone_project_model: Project
) -> None:
    """Completely update the sla attributes. Also override not set ones."""
    initial_project = sla_model.projects.single()
    user_group = sla_model.user_group.single()
    provider = stand_alone_project_model.provider.single()
    projects = provider.projects.all()
    item.project = stand_alone_project_model.uuid

    db_obj = sla_mng.update(obj_in=item, db_obj=sla_model, provider_projects=projects)

    assert db_obj is not None
    assert isinstance(db_obj, SLA)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.user_group.is_connected(user_group)
    assert len(db_obj.projects) == 2
    assert set([i.uuid for i in db_obj.projects]) == set(
        [item.project, initial_project.uuid]
    )


@parametrize_with_cases("item", cases=CaseSLA)
def test_update_no_changes(item: SLACreateExtended, sla_model: SLA) -> None:
    """The new item is equal to the existing one. No changes."""
    project = sla_model.projects.single()
    provider = project.provider.single()
    projects = provider.projects.all()
    item.doc_uuid = sla_model.doc_uuid
    item.start_date = sla_model.start_date
    item.end_date = sla_model.end_date
    item.project = project.uuid

    db_obj = sla_mng.update(obj_in=item, db_obj=sla_model, provider_projects=projects)

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseSLA)
def test_update_same_projects(item: SLACreateExtended, sla_model: SLA) -> None:
    """Completely update the SLA attributes. Also override not set ones.

    Keep the same projects but change content..
    """
    user_group = sla_model.user_group.single()
    project = sla_model.projects.single()
    provider = project.provider.single()
    projects = provider.projects.all()
    item.project = project.uuid

    db_obj = sla_mng.update(obj_in=item, db_obj=sla_model, provider_projects=projects)

    assert db_obj is not None
    assert isinstance(db_obj, SLA)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.user_group.is_connected(user_group)
    assert len(db_obj.projects) == 1
    assert db_obj.projects.single().uuid == item.project


@parametrize_with_cases("item", cases=CaseSLA)
def test_update_empy_provider_projects_list(
    item: SLACreateExtended, sla_model: SLA
) -> None:
    """Empty list passed to the provider_projects param."""
    msg = "The provider's projects list is empty"
    with pytest.raises(AssertionError, match=re.escape(msg)):
        sla_mng.update(obj_in=item, db_obj=sla_model, provider_projects=[])


@parametrize_with_cases("item", cases=CaseSLA)
def test_update_invalid_project(item: SLACreateExtended, sla_model: SLA) -> None:
    """None of the new flavor projects belong to the target provider."""
    projects = [Project(name=random_lower_string(), uuid=str(uuid4())).save()]
    msg = (
        f"Input project {item.project} not in the provider "
        f"projects: {[i.uuid for i in projects]}"
    )
    with pytest.raises(AssertionError, match=re.escape(msg)):
        sla_mng.update(obj_in=item, db_obj=sla_model, provider_projects=projects)
