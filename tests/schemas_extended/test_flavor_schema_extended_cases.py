from uuid import UUID, uuid4

from pytest_cases import case, parametrize

from fed_reg.project.models import Project
from fed_reg.service.models import ComputeService
from tests.create_dict import compute_service_model_dict, project_model_dict


class CaseAttr:
    @case(tags=["create_extended"])
    @parametrize(len=(1, 2))
    def case_create_projects(self, len: int) -> list[UUID]:
        return [uuid4() for _ in range(len)]

    @case(tags=["read", "services"])
    @parametrize(len=(1, 2))
    def case_services(self, len: int) -> list[ComputeService]:
        return [
            ComputeService(**compute_service_model_dict()).save() for _ in range(len)
        ]

    @case(tags=["read", "projects"])
    @parametrize(len=(1, 2))
    def case_projects(self, len: int) -> list[Project]:
        return [Project(**project_model_dict()).save() for _ in range(len)]
