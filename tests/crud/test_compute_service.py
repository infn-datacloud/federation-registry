from uuid import uuid4

import pytest
from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.image.models import PrivateImage, SharedImage
from fedreg.project.models import Project
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import ComputeServiceCreateExtended
from fedreg.quota.models import ComputeQuota
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import ComputeService
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.service.crud import compute_service_mng
from tests.utils import (
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def stand_alone_service_model() -> ComputeService:
    """Compute service model belonging to a different provider.

    Already connected to a region and a provider.
    """
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    provider.regions.connect(region)
    region.services.connect(service)
    return service


@pytest.fixture
def region_model() -> Region:
    """Region model. Already connected to a provider."""
    provider = Provider(name=random_lower_string(), type=random_provider_type()).save()
    region = Region(name=random_lower_string()).save()
    provider.regions.connect(region)
    return region


@pytest.fixture
def service_model(region_model: Region) -> ComputeService:
    """Compute service model.

    Already connected to a region and a provider. It already has one quota, one private
    and one share flavor, one private and one share image.
    """
    provider = region_model.provider.single()
    service = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    quota = ComputeQuota().save()
    shared_flavor = SharedFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    private_flavor = PrivateFlavor(name=random_lower_string(), uuid=str(uuid4())).save()
    shared_image = SharedImage(name=random_lower_string(), uuid=str(uuid4())).save()
    private_image = PrivateImage(name=random_lower_string(), uuid=str(uuid4())).save()
    project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
    provider.projects.connect(project)
    region_model.services.connect(service)
    service.quotas.connect(quota)
    service.flavors.connect(shared_flavor)
    service.flavors.connect(private_flavor)
    service.images.connect(shared_image)
    service.images.connect(private_image)
    quota.project.connect(project)
    private_flavor.projects.connect(project)
    private_image.projects.connect(project)
    return service


class CaseService:
    @case(tags="base")
    def case_compute_service(self) -> ComputeServiceCreateExtended:
        return ComputeServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.COMPUTE),
        )

    @case(tags="quotas")
    @parametrize(tot_quotas=(1, 2))
    def case_compute_service_with_quotas(
        self, tot_quotas: int, region_model: Region
    ) -> ComputeServiceCreateExtended:
        provider = region_model.provider.single()
        quotas = []
        for _ in range(tot_quotas):
            project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
            provider.projects.connect(project)
            quotas.append({"project": project.uuid})
        return ComputeServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.COMPUTE),
            quotas=quotas,
        )

    @case(tags="flavors")
    def case_compute_service_with_flavors(
        self, region_model: Region
    ) -> ComputeServiceCreateExtended:
        provider = region_model.provider.single()
        flavors = []
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        flavors.append(
            {"name": random_lower_string(), "uuid": uuid4(), "projects": [project.uuid]}
        )
        flavors.append({"name": random_lower_string(), "uuid": uuid4()})
        return ComputeServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.COMPUTE),
            flavors=flavors,
        )

    @case(tags="images")
    def case_compute_service_with_images(
        self, region_model: Region
    ) -> ComputeServiceCreateExtended:
        provider = region_model.provider.single()
        images = []
        project = Project(name=random_lower_string(), uuid=str(uuid4())).save()
        provider.projects.connect(project)
        images.append(
            {"name": random_lower_string(), "uuid": uuid4(), "projects": [project.uuid]}
        )
        images.append({"name": random_lower_string(), "uuid": uuid4()})
        return ComputeServiceCreateExtended(
            endpoint=random_url(),
            name=random_service_name(ServiceType.COMPUTE),
            images=images,
        )


@parametrize_with_cases("item", cases=CaseService)
def test_create(item: ComputeServiceCreateExtended, region_model: Region) -> None:
    """Create a new istance"""
    provider = region_model.provider.single()
    projects = provider.projects.all()

    db_obj = compute_service_mng.create(
        obj_in=item, region=region_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    assert db_obj.region.is_connected(region_model)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.flavors) == len(item.flavors)
    assert len(db_obj.images) == len(item.images)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_with_no_provider_projects(
    item: ComputeServiceCreateExtended, region_model: Region
) -> None:
    """No provider_projects param is needed when items not requesting it are defined."""
    db_obj = compute_service_mng.create(obj_in=item, region=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    assert db_obj.region.is_connected(region_model)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_same_uuid_diff_provider(
    item: ComputeServiceCreateExtended,
    region_model: Region,
    stand_alone_service_model: ComputeService,
) -> None:
    """A compute service with the given endpoint exists on a different provider."""
    item.endpoint = stand_alone_service_model.endpoint

    db_obj = compute_service_mng.create(obj_in=item, region=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    assert db_obj.region.is_connected(region_model)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_create_already_exists(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """A compute service with the given uuid already exists"""
    region = service_model.region.single()
    provider = region.provider.single()

    item.endpoint = service_model.endpoint

    msg = (
        f"A compute service with endpoint {item.endpoint} "
        f"belonging to provider {provider.name} already exists"
    )
    with pytest.raises(AssertionError, match=msg):
        compute_service_mng.create(obj_in=item, region=region)


@parametrize_with_cases("item", cases=CaseService)
def test_update(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """Completely update the service attributes. Also override not set ones.

    Replace existing quotas, flavors and images with new ones.
    Remove no more used and add new ones.
    """
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    db_obj = compute_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.flavors) == len(item.flavors)
    assert len(db_obj.images) == len(item.images)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_no_changes(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """The new item is equal to the existing one. No changes."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.endpoint = service_model.endpoint
    item.name = service_model.name
    quotas = []
    for quota in service_model.quotas:
        d = {"project": quota.project.single().uuid}
        quotas.append(d)
    item.quotas = quotas
    flavors = []
    for flavor in service_model.flavors:
        d = {"name": flavor.name, "uuid": flavor.uuid}
        if not flavor.is_shared:
            d["projects"] = [x.uuid for x in flavor.projects]
        flavors.append(d)
    item.flavors = flavors
    images = []
    for image in service_model.images:
        d = {"name": image.name, "uuid": image.uuid}
        if not image.is_shared:
            d["projects"] = [x.uuid for x in image.projects]
        images.append(d)
    item.images = images

    db_obj = compute_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_service_details(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """Change only item content. Keep same relationships."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    quotas = []
    for quota in service_model.quotas:
        d = {"project": quota.project.single().uuid}
        quotas.append(d)
    item.quotas = quotas
    flavors = []
    for flavor in service_model.flavors:
        d = {"name": flavor.name, "uuid": flavor.uuid}
        if not flavor.is_shared:
            d["projects"] = [x.uuid for x in flavor.projects]
        flavors.append(d)
    item.flavors = flavors
    images = []
    for image in service_model.images:
        d = {"name": image.name, "uuid": image.uuid}
        if not image.is_shared:
            d["projects"] = [x.uuid for x in image.projects]
        images.append(d)
    item.images = images

    db_obj = compute_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.flavors) == len(item.flavors)
    assert len(db_obj.images) == len(item.images)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_flavors(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """Change only flavors."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.endpoint = service_model.endpoint
    item.name = service_model.name
    quotas = []
    for quota in service_model.quotas:
        d = {"project": quota.project.single().uuid}
        quotas.append(d)
    item.quotas = quotas
    images = []
    for image in service_model.images:
        d = {"name": image.name, "uuid": image.uuid}
        if not image.is_shared:
            d["projects"] = [x.uuid for x in image.projects]
        images.append(d)
    item.images = images

    db_obj = compute_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.flavors) == len(item.flavors)
    assert len(db_obj.images) == len(item.images)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_images(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """Change only images."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.endpoint = service_model.endpoint
    item.name = service_model.name
    quotas = []
    for quota in service_model.quotas:
        d = {"project": quota.project.single().uuid}
        quotas.append(d)
    item.quotas = quotas
    flavors = []
    for flavor in service_model.flavors:
        d = {"name": flavor.name, "uuid": flavor.uuid}
        if not flavor.is_shared:
            d["projects"] = [x.uuid for x in flavor.projects]
        flavors.append(d)
    item.flavors = flavors

    db_obj = compute_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.flavors) == len(item.flavors)
    assert len(db_obj.images) == len(item.images)


@parametrize_with_cases("item", cases=CaseService, has_tag="base")
def test_update_only_quotas(
    item: ComputeServiceCreateExtended,
    service_model: ComputeService,
) -> None:
    """Change only quotas."""
    region = service_model.region.single()
    provider = region.provider.single()
    projects = provider.projects.all()

    item.endpoint = service_model.endpoint
    item.name = service_model.name
    flavors = []
    for flavor in service_model.flavors:
        d = {"name": flavor.name, "uuid": flavor.uuid}
        if not flavor.is_shared:
            d["projects"] = [x.uuid for x in flavor.projects]
        flavors.append(d)
    item.flavors = flavors
    images = []
    for image in service_model.images:
        d = {"name": image.name, "uuid": image.uuid}
        if not image.is_shared:
            d["projects"] = [x.uuid for x in image.projects]
        images.append(d)
    item.images = images

    db_obj = compute_service_mng.update(
        obj_in=item, db_obj=service_model, provider_projects=projects
    )

    assert db_obj is not None
    assert isinstance(db_obj, ComputeService)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert len(db_obj.quotas) == len(item.quotas)
    assert len(db_obj.flavors) == len(item.flavors)
    assert len(db_obj.images) == len(item.images)
