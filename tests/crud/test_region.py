import pytest
from fedreg.location.models import Location
from fedreg.provider.models import Provider
from fedreg.provider.schemas_extended import (
    RegionCreateExtended,
)
from fedreg.region.models import Region
from fedreg.service.enum import ServiceType
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.region.crud import region_mng
from tests.utils import (
    random_country,
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_url,
)


@pytest.fixture
def another_provider_model() -> Provider:
    """Another provider model"""
    return Provider(name=random_lower_string(), type=random_provider_type()).save()


@pytest.fixture
def location_model() -> Location:
    """Stand alone location model"""
    return Location(site=random_lower_string(), country=random_country()).save()


@pytest.fixture
def provider_model() -> Provider:
    """Provider model"""
    return Provider(name=random_lower_string(), type=random_provider_type()).save()


@pytest.fixture
def region_model(provider_model: Provider) -> Region:
    """BlockStorage service model.

    Already connected to a region and a provider. It already has one quota.
    """
    region = Region(name=random_lower_string()).save()
    service1 = BlockStorageService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.BLOCK_STORAGE)
    ).save()
    service2 = ComputeService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.COMPUTE)
    ).save()
    service3 = IdentityService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.IDENTITY)
    ).save()
    service4 = NetworkService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.NETWORK)
    ).save()
    service5 = ObjectStoreService(
        endpoint=str(random_url()), name=random_service_name(ServiceType.OBJECT_STORE)
    ).save()
    location = Location(site=random_lower_string(), country=random_country()).save()
    provider_model.regions.connect(region)
    region.services.connect(service1)
    region.services.connect(service2)
    region.services.connect(service3)
    region.services.connect(service4)
    region.services.connect(service5)
    region.location.connect(location)
    return region


class CaseRegion:
    @case(tags="base")
    def case_region(self) -> RegionCreateExtended:
        return RegionCreateExtended(name=random_lower_string())

    @case(tags="location")
    def case_region_with_location(self) -> RegionCreateExtended:
        location = {"site": random_lower_string(), "country": random_country()}
        return RegionCreateExtended(name=random_lower_string(), location=location)

    @case(tags="block_storage_services")
    @parametrize(tot_srv=(1, 2))
    def case_region_with_block_storage_services(
        self, tot_srv: int
    ) -> RegionCreateExtended:
        services = []
        for _ in range(tot_srv):
            services.append(
                {
                    "endpoint": random_url(),
                    "name": random_service_name(ServiceType.BLOCK_STORAGE),
                }
            )
        return RegionCreateExtended(
            name=random_lower_string(), block_storage_services=services
        )

    @case(tags="compute_services")
    @parametrize(tot_srv=(1, 2))
    def case_region_with_compute_services(self, tot_srv: int) -> RegionCreateExtended:
        services = []
        for _ in range(tot_srv):
            services.append(
                {
                    "endpoint": random_url(),
                    "name": random_service_name(ServiceType.COMPUTE),
                }
            )
        return RegionCreateExtended(
            name=random_lower_string(), compute_services=services
        )

    @case(tags="identity_services")
    @parametrize(tot_srv=(1, 2))
    def case_region_with_identity_services(self, tot_srv: int) -> RegionCreateExtended:
        services = []
        for _ in range(tot_srv):
            services.append(
                {
                    "endpoint": random_url(),
                    "name": random_service_name(ServiceType.IDENTITY),
                }
            )
        return RegionCreateExtended(
            name=random_lower_string(), identity_services=services
        )

    @case(tags="network_services")
    @parametrize(tot_srv=(1, 2))
    def case_region_with_network_services(self, tot_srv: int) -> RegionCreateExtended:
        services = []
        for _ in range(tot_srv):
            services.append(
                {
                    "endpoint": random_url(),
                    "name": random_service_name(ServiceType.NETWORK),
                }
            )
        return RegionCreateExtended(
            name=random_lower_string(), network_services=services
        )

    @case(tags="object_store_services")
    @parametrize(tot_srv=(1, 2))
    def case_region_with_object_store_services(
        self, tot_srv: int
    ) -> RegionCreateExtended:
        services = []
        for _ in range(tot_srv):
            services.append(
                {
                    "endpoint": random_url(),
                    "name": random_service_name(ServiceType.OBJECT_STORE),
                }
            )
        return RegionCreateExtended(
            name=random_lower_string(), object_store_services=services
        )


@parametrize_with_cases("item", cases=CaseRegion)
def test_create(item: RegionCreateExtended, provider_model: Provider) -> None:
    """Create a new istance"""
    db_obj = region_mng.create(obj_in=item, provider=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    assert db_obj.provider.is_connected(provider_model)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_create_same_name_diff_provider(
    item: RegionCreateExtended,
    region_model: Region,
    another_provider_model: Provider,
) -> None:
    """A region with the given name exists on another provider."""
    item.name = region_model.name

    db_obj = region_mng.create(obj_in=item, provider=another_provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    assert db_obj.provider.is_connected(another_provider_model)
    assert db_obj.location.single() is None
    assert len(db_obj.services) == 0


@parametrize_with_cases("item", cases=CaseRegion, has_tag="location")
def test_create_location_already_exists(
    item: RegionCreateExtended,
    provider_model: Provider,
    location_model: Location,
) -> None:
    """A region with the given name exists on another provider."""
    item.location.site = location_model.site

    db_obj = region_mng.create(obj_in=item, provider=provider_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    assert db_obj.provider.is_connected(provider_model)
    assert db_obj.location.is_connected(location_model)
    assert len(db_obj.services) == 0


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_create_already_exists(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """A region with the given name already exists on target provider"""
    provider = region_model.provider.single()

    item.name = region_model.name

    msg = f"Provider {provider.name} already has a region with name {item.name}"
    with pytest.raises(AssertionError, match=msg):
        region_mng.create(obj_in=item, provider=provider)


@parametrize_with_cases("item", cases=CaseRegion)
def test_update(item: RegionCreateExtended, region_model: Region) -> None:
    """Completely update the region attributes. Also override not set ones.

    Replace existing location and services with new ones.
    Remove no more used and add new ones.
    """
    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_no_changes(item: RegionCreateExtended, region_model: Region) -> None:
    """The new item is equal to the existing one. No changes."""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location.site, "country": location.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is None


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_only_region_details(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Change only item content. Keep same relationships."""
    location = region_model.location.single()

    item.location = {"site": location.site, "country": location.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_only_block_storage_services(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Change only block storage services."""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location.site, "country": location.country}
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_only_compute_services(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Change only compute services."""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location.site, "country": location.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_only_identity_services(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Change only identity services."""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location.site, "country": location.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_only_network_services(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Change only network services."""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location.site, "country": location.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_only_object_store_services(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Change only object store services."""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location.site, "country": location.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    if item.location is not None:
        assert db_obj.location.single() is not None
    else:
        assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


# TODO: Yes location -> new location


@parametrize_with_cases("item", cases=CaseRegion, has_tag="location")
def test_update_add_location(item: RegionCreateExtended, region_model: Region) -> None:
    """Currently no location. Add a new location to the region."""
    region_model.location.disconnect_all()

    item.name = region_model.name
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert db_obj.location.single() is not None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="base")
def test_update_disconnect_location(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Region has a location. Disconnect it"""
    location = region_model.location.single()

    item.name = region_model.name
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert not db_obj.location.is_connected(location)
    assert db_obj.location.single() is None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="location")
def test_update_replace_location(
    item: RegionCreateExtended, region_model: Region
) -> None:
    """Region has a location. Disconnect it, create the new one and attach it."""
    location = region_model.location.single()

    item.name = region_model.name
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert not db_obj.location.is_connected(location)
    assert db_obj.location.single() is not None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )


@parametrize_with_cases("item", cases=CaseRegion, has_tag="location")
def test_update_replace_with_existing_location(
    item: RegionCreateExtended, region_model: Region, location_model: Location
) -> None:
    """Region has a location. Disconnect it and link the new existing location"""
    location = region_model.location.single()

    item.name = region_model.name
    item.location = {"site": location_model.site, "country": location_model.country}
    block_storage_services = []
    for service in region_model.services.filter(type=ServiceType.BLOCK_STORAGE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        block_storage_services.append(d)
    item.block_storage_services = block_storage_services
    compute_services = []
    for service in region_model.services.filter(type=ServiceType.COMPUTE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        compute_services.append(d)
    item.compute_services = compute_services
    identity_services = []
    for service in region_model.services.filter(type=ServiceType.IDENTITY.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        identity_services.append(d)
    item.identity_services = identity_services
    network_services = []
    for service in region_model.services.filter(type=ServiceType.NETWORK.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        network_services.append(d)
    item.network_services = network_services
    object_store_services = []
    for service in region_model.services.filter(type=ServiceType.OBJECT_STORE.value):
        d = {"endpoint": service.endpoint, "name": service.name}
        object_store_services.append(d)
    item.object_store_services = object_store_services

    db_obj = region_mng.update(obj_in=item, db_obj=region_model)

    assert db_obj is not None
    assert isinstance(db_obj, Region)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)
    assert not db_obj.location.is_connected(location)
    assert db_obj.location.single() is not None
    assert len(db_obj.services.filter(type=ServiceType.BLOCK_STORAGE.value)) == len(
        item.block_storage_services
    )
    assert len(db_obj.services.filter(type=ServiceType.COMPUTE.value)) == len(
        item.compute_services
    )
    assert len(db_obj.services.filter(type=ServiceType.IDENTITY.value)) == len(
        item.identity_services
    )
    assert len(db_obj.services.filter(type=ServiceType.NETWORK.value)) == len(
        item.network_services
    )
    assert len(db_obj.services.filter(type=ServiceType.OBJECT_STORE.value)) == len(
        item.object_store_services
    )
