from typing import Literal

import pytest
from neomodel import DoesNotExist
from pytest_cases import parametrize_with_cases

from fed_reg.crud import CRUDInterface
from fed_reg.project.models import Project
from fed_reg.sla.crud import CRUDSLA, sla_mgr
from fed_reg.sla.models import SLA
from fed_reg.sla.schemas import SLACreate
from fed_reg.user_group.models import UserGroup
from tests.models.utils import project_model_dict
from tests.schemas.utils import sla_schema_dict
from tests.utils import random_date_after, random_date_before


class CaseDate:
    def case_start_date(self) -> Literal["start_date"]:
        return "start_date"

    def case_end_date(self) -> Literal["end_date"]:
        return "end_date"


def test_inheritance():
    """Test CRUD classes inheritance."""
    assert issubclass(CRUDSLA, CRUDInterface)

    assert isinstance(sla_mgr, CRUDSLA)
    assert sla_mgr.model == SLA
    assert sla_mgr.schema_create == SLACreate


def test_create_new_sla(project_model: Project, user_group_model: UserGroup):
    """Create new SLA.

    Project and UserGroup neomodel entities are mandatory.
    """
    sla_schema = SLACreate(**sla_schema_dict())
    item = sla_mgr.create(
        obj_in=sla_schema, project=project_model, user_group=user_group_model
    )
    assert item.doc_uuid == sla_schema.doc_uuid
    assert item.start_date == sla_schema.start_date
    assert item.end_date == sla_schema.end_date
    assert len(item.projects) == 1
    assert item.projects.single() == project_model
    assert len(item.user_group) == 1
    assert item.user_group.single() == user_group_model


def test_create_sla_dup_doc_uuid(
    sla_model: SLA, project_model: Project, user_group_model: UserGroup
):
    """Create an SLA pointing to projects belonging to different providers.

    An SLA can have multiple projects, each belonging to a different provider, and a
    single user group.
    The SLACreate object expect only one project because the logic to add SLA is done
    one by one. This way we can have a situation were we are adding again an SLA
    pointing to the same doc uuid of another one, but in fact they are the same.
    In this case we just need to update the projects list.
    """
    sla_model.projects.connect(project_model)
    sla_model.user_group.connect(user_group_model)
    assert len(sla_model.projects) == 1
    assert len(sla_model.user_group) == 1

    sla_schema = SLACreate(
        doc_uuid=sla_model.doc_uuid,
        start_date=sla_model.start_date,
        end_date=sla_model.end_date,
    )
    project_model2 = Project(**project_model_dict()).save()
    item = sla_mgr.create(
        obj_in=sla_schema, project=project_model2, user_group=user_group_model
    )
    assert item == sla_model
    assert len(item.projects) == 2
    assert item.projects.get(uid=project_model.uid) == project_model
    assert item.projects.get(uid=project_model2.uid) == project_model2
    assert len(item.user_group) == 1
    assert item.user_group.single() == user_group_model


@parametrize_with_cases("date_attr", cases=CaseDate)
def test_create_sla_dup_doc_uuid_fail(
    sla_model: SLA, project_model: Project, user_group_model: UserGroup, date_attr: str
):
    """Creating an SLA pointing to an already doc uuid with different dates fails.

    If the start and end dates of an SLA pointing to a document uuid differ from the
    start and end dates of another SLA already pointing to that documents, the input SLA
    may point to the wrong document uuid or it should be used an update procedure
    instead.

    The create procedure raises a AssertionError.
    """
    sla_model.projects.connect(project_model)
    sla_model.user_group.connect(user_group_model)
    assert len(sla_model.projects) == 1
    assert len(sla_model.user_group) == 1

    sla_schema = SLACreate(
        doc_uuid=sla_model.doc_uuid,
        start_date=sla_model.start_date,
        end_date=sla_model.end_date,
    )
    if date_attr == "start_date":
        sla_schema.__setattr__(date_attr, random_date_before(sla_schema.end_date))
    else:
        sla_schema.__setattr__(date_attr, random_date_after(sla_schema.start_date))

    with pytest.raises(AssertionError, match=f"Different {date_attr}"):
        sla_mgr.create(
            obj_in=sla_schema, project=project_model, user_group=user_group_model
        )


def test_create_sla_replace_and_delete_existing(
    sla_model: SLA, project_model: Project, user_group_model: UserGroup
):
    """Create an SLA an replace the one already assigned to a project.

    If the user group's name change, the procedure creates a new user group and create a
    new SLA. This SLA points to an already existing project, yet pointing to the
    previous SLA instance (this instance still exists since it is deleted at the end
    only if it has no more related projects).
    This way we need to replace the SLA connection since a project can have only one SLA


    Delete the previous SLA at the end.
    """
    sla_model.projects.connect(project_model)
    sla_model.user_group.connect(user_group_model)
    assert len(sla_model.projects) == 1
    assert len(sla_model.user_group) == 1

    sla_schema = SLACreate(**sla_schema_dict())
    item = sla_mgr.create(
        obj_in=sla_schema, project=project_model, user_group=user_group_model
    )
    assert item.doc_uuid == sla_schema.doc_uuid
    assert item.start_date == sla_schema.start_date
    assert item.end_date == sla_schema.end_date
    assert len(item.projects) == 1
    assert item.projects.get(uid=project_model.uid) == project_model
    assert len(item.user_group) == 1
    assert item.user_group.single() == user_group_model

    with pytest.raises(DoesNotExist):
        sla_model.refresh()


def test_create_sla_replace_existing(
    sla_model: SLA, project_model: Project, user_group_model: UserGroup
):
    """Create an SLA an replace the one already assigned to a project.

    If the user group's name change, the procedure creates a new user group and create a
    new SLA. This SLA points to an already existing project, yet pointing to the
    previous SLA instance (this instance still exists since it is deleted at the end
    only if it has no more related projects).
    This way we need to replace the SLA connection since a project can have only one SLA

    Previous SLA, still exists since it has another linked project.
    """
    project_model2 = Project(**project_model_dict()).save()
    sla_model.projects.connect(project_model)
    sla_model.projects.connect(project_model2)
    sla_model.user_group.connect(user_group_model)
    assert len(sla_model.projects) == 2
    assert len(sla_model.user_group) == 1

    sla_schema = SLACreate(**sla_schema_dict())
    item = sla_mgr.create(
        obj_in=sla_schema, project=project_model, user_group=user_group_model
    )
    assert item.doc_uuid == sla_schema.doc_uuid
    assert item.start_date == sla_schema.start_date
    assert item.end_date == sla_schema.end_date
    assert len(item.projects) == 1
    assert item.projects.get(uid=project_model.uid) == project_model
    assert len(item.user_group) == 1
    assert item.user_group.single() == user_group_model

    assert len(sla_model.projects) == 1
    assert sla_model.projects.get(uid=project_model2.uid) == project_model2
