from uuid import UUID, uuid4

from pytest_cases import case, parametrize

from fed_reg.flavor.models import Flavor
from fed_reg.flavor.schemas_extended import (
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    RegionReadExtended,
    RegionReadExtendedPublic,
)
from fed_reg.project.models import Project
from fed_reg.provider.models import Provider
from fed_reg.region.models import Region
from fed_reg.region.schemas import RegionRead, RegionReadPublic
from fed_reg.service.models import ComputeService
from fed_reg.service.schemas import (
    ComputeServiceRead,
    ComputeServiceReadPublic,
)
from tests.create_dict import (
    compute_service_model_dict,
    flavor_model_dict,
    project_model_dict,
    provider_model_dict,
    region_model_dict,
)


class CaseFlavorExtSchemas:
    @case(tags=["valid_create"])
    @parametrize(len=(0, 1, 2))
    def case_projects(self, len: int) -> list[UUID]:
        return [uuid4() for _ in range(len)]

    @case(tags=["invalid_create"])
    @parametrize(len=[0, 1, 2])
    def case_invalid_projects(self, len: int) -> tuple[list[UUID], str]:
        if len == 1:
            return [uuid4()], "Public flavors do not have linked projects"
        elif len == 2:
            i = uuid4()
            return [i, i], "There are multiple identical items"
        return [], "Projects are mandatory for private flavors"

    @case(tags=["valid_read"])
    @parametrize(len=(1, 2))
    def case_public_flavor(self, len: int):
        flavor = Flavor(**flavor_model_dict()).save()
        region = Region(**region_model_dict()).save()
        provider = Provider(**provider_model_dict()).save()
        region.provider.connect(provider)
        for _ in range(len):
            compute_service = ComputeService(**compute_service_model_dict()).save()
            compute_service.regions.connect(region)
            flavor.services.connect(compute_service)
        return flavor

    @case(tags=["valid_read"])
    @parametrize(len=(1, 2))
    def case_private_flavor(self, len: int):
        flavor = Flavor(**flavor_model_dict(), is_public=False).save()
        compute_service = ComputeService(**compute_service_model_dict()).save()
        region = Region(**region_model_dict()).save()
        provider = Provider(**provider_model_dict()).save()
        region.provider.connect(provider)
        compute_service.regions.connect(region)
        flavor.services.connect(compute_service)
        for _ in range(len):
            project = Project(**project_model_dict()).save()
            flavor.projects.connect(project)
        return flavor

    @case(tags=["invalid_read"])
    def case_missing_service(self):
        return Flavor(**flavor_model_dict()).save()

    @case(tags=["invalid_read"])
    def case_missing_region(self):
        flavor = Flavor(**flavor_model_dict()).save()
        compute_service = ComputeService(**compute_service_model_dict()).save()
        flavor.services.connect(compute_service)
        return flavor

    @case(tags=["invalid_read"])
    def case_missing_provider(self):
        flavor = Flavor(**flavor_model_dict()).save()
        compute_service = ComputeService(**compute_service_model_dict()).save()
        region = Region(**region_model_dict()).save()
        compute_service.regions.connect(region)
        flavor.services.connect(compute_service)
        return flavor

    @case(tags=["inheritance"])
    def case_region_read(self):
        return RegionReadExtended, RegionRead

    @case(tags=["inheritance"])
    def case_compute_service_read(self):
        return ComputeServiceReadExtended, ComputeServiceRead

    @case(tags=["inheritance"])
    def case_region_read_public(self):
        return RegionReadExtendedPublic, RegionReadPublic

    @case(tags=["inheritance"])
    def case_compute_service_read_public(self):
        return ComputeServiceReadExtendedPublic, ComputeServiceReadPublic
