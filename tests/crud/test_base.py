from random import choice
from uuid import uuid4

from fedreg.flavor.models import PrivateFlavor, SharedFlavor
from fedreg.flavor.schemas import FlavorUpdate
from fedreg.identity_provider.models import IdentityProvider
from fedreg.identity_provider.schemas import IdentityProviderUpdate
from fedreg.image.models import PrivateImage, SharedImage
from fedreg.image.schemas import ImageUpdate
from fedreg.location.models import Location
from fedreg.location.schemas import LocationUpdate
from fedreg.network.models import PrivateNetwork, SharedNetwork
from fedreg.network.schemas import NetworkUpdate
from fedreg.project.models import Project
from fedreg.project.schemas import ProjectUpdate
from fedreg.provider.models import Provider
from fedreg.provider.schemas import ProviderUpdate
from fedreg.quota.models import (
    BlockStorageQuota,
    ComputeQuota,
    NetworkQuota,
    ObjectStoreQuota,
)
from fedreg.quota.schemas import (
    BlockStorageQuotaUpdate,
    ComputeQuotaUpdate,
    NetworkQuotaUpdate,
    ObjectStoreQuotaUpdate,
)
from fedreg.region.models import Region
from fedreg.region.schemas import RegionUpdate
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
    ServiceType,
)
from fedreg.service.schemas import (
    BlockStorageServiceUpdate,
    ComputeServiceUpdate,
    IdentityServiceUpdate,
    NetworkServiceUpdate,
    ObjectStoreServiceUpdate,
)
from fedreg.sla.models import SLA
from fedreg.sla.schemas import SLAUpdate
from fedreg.user_group.models import UserGroup
from fedreg.user_group.schemas import UserGroupUpdate
from pytest_cases import case, parametrize_with_cases

from fed_reg.flavor.crud import (
    CRUDPrivateFlavor,
    CRUDSharedFlavor,
    private_flavor_mng,
    shared_flavor_mng,
)
from fed_reg.identity_provider.crud import CRUDIdentityProvider, identity_provider_mgr
from fed_reg.image.crud import (
    CRUDPrivateImage,
    CRUDSharedImage,
    private_image_mng,
    shared_image_mng,
)
from fed_reg.location.crud import CRUDLocation, location_mgr
from fed_reg.network.crud import (
    CRUDPrivateNetwork,
    CRUDSharedNetwork,
    private_network_mng,
    shared_network_mng,
)
from fed_reg.project.crud import CRUDProject, project_mgr
from fed_reg.provider.crud import CRUDProvider, provider_mgr
from fed_reg.quota.crud import (
    CRUDBlockStorageQuota,
    CRUDComputeQuota,
    CRUDNetworkQuota,
    CRUDObjectStoreQuota,
    block_storage_quota_mng,
    compute_quota_mng,
    network_quota_mng,
    object_store_quota_mng,
)
from fed_reg.region.crud import CRUDRegion, region_mgr
from fed_reg.service.crud import (
    CRUDBlockStorageService,
    CRUDComputeService,
    CRUDIdentityService,
    CRUDNetworkService,
    CRUDObjectStoreService,
    block_storage_service_mng,
    compute_service_mng,
    identity_service_mng,
    network_service_mng,
    object_store_service_mng,
)
from fed_reg.sla.crud import CRUDSLA, sla_mgr
from fed_reg.user_group.crud import CRUDUserGroup, user_group_mgr
from tests.utils import (
    random_country,
    random_lower_string,
    random_provider_type,
    random_service_name,
    random_start_end_dates,
    random_url,
)


class CaseCRUD:
    """Return tuples with CRUD, model and new_item."""

    def case_private_flavor(
        self,
    ) -> tuple[CRUDPrivateFlavor, PrivateFlavor, FlavorUpdate]:
        model = PrivateFlavor(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = FlavorUpdate(description=random_lower_string())
        return private_flavor_mng, model, new_item

    @case(tags="update")
    def case_shared_flavor(
        self,
    ) -> tuple[CRUDSharedFlavor, SharedFlavor, FlavorUpdate]:
        model = SharedFlavor(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = FlavorUpdate(description=random_lower_string())
        return shared_flavor_mng, model, new_item

    def case_identity_provider(
        self,
    ) -> tuple[CRUDIdentityProvider, IdentityProvider, IdentityProviderUpdate]:
        model = IdentityProvider(
            endpoint=random_url(),
            group_claim=random_lower_string(),
            description=random_lower_string(),
        ).save()
        new_item = IdentityProviderUpdate(description=random_lower_string())
        return identity_provider_mgr, model, new_item

    def case_private_image(
        self,
    ) -> tuple[CRUDPrivateImage, PrivateImage, ImageUpdate]:
        model = PrivateImage(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = ImageUpdate(description=random_lower_string())
        return private_image_mng, model, new_item

    @case(tags="update")
    def case_shared_image(
        self,
    ) -> tuple[CRUDSharedImage, SharedImage, ImageUpdate]:
        model = SharedImage(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = ImageUpdate(description=random_lower_string())
        return shared_image_mng, model, new_item

    @case(tags="update")
    def case_location(
        self,
    ) -> tuple[CRUDLocation, Location, LocationUpdate]:
        model = Location(
            site=random_lower_string(),
            country=random_country(),
            description=random_lower_string(),
        ).save()
        new_item = LocationUpdate(description=random_lower_string())
        return location_mgr, model, new_item

    def case_private_network(
        self,
    ) -> tuple[CRUDPrivateNetwork, PrivateNetwork, NetworkUpdate]:
        model = PrivateNetwork(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = NetworkUpdate(description=random_lower_string())
        return private_network_mng, model, new_item

    @case(tags="update")
    def case_shared_network(
        self,
    ) -> tuple[CRUDSharedNetwork, SharedNetwork, NetworkUpdate]:
        model = SharedNetwork(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = NetworkUpdate(description=random_lower_string())
        return shared_network_mng, model, new_item

    @case(tags="update")
    def case_project(
        self,
    ) -> tuple[CRUDProject, Project, ProjectUpdate]:
        model = Project(
            name=random_lower_string(),
            uuid=str(uuid4()),
            description=random_lower_string(),
        ).save()
        new_item = ProjectUpdate(description=random_lower_string())
        return project_mgr, model, new_item

    def case_provider(
        self,
    ) -> tuple[CRUDProvider, Provider, ProviderUpdate]:
        model = Provider(
            name=random_lower_string(),
            type=random_provider_type(),
            description=random_lower_string(),
        ).save()
        new_item = ProviderUpdate(description=random_lower_string())
        return provider_mgr, model, new_item

    def case_block_storage_quota(
        self,
    ) -> tuple[CRUDBlockStorageQuota, BlockStorageQuota, BlockStorageQuotaUpdate]:
        model = BlockStorageQuota(description=random_lower_string()).save()
        new_item = BlockStorageQuotaUpdate(description=random_lower_string())
        return block_storage_quota_mng, model, new_item

    def case_compute_quota(
        self,
    ) -> tuple[CRUDComputeQuota, ComputeQuota, ComputeQuotaUpdate]:
        model = ComputeQuota(description=random_lower_string()).save()
        new_item = ComputeQuotaUpdate(description=random_lower_string())
        return compute_quota_mng, model, new_item

    def case_network_quota(
        self,
    ) -> tuple[CRUDNetworkQuota, NetworkQuota, NetworkQuotaUpdate]:
        model = NetworkQuota(description=random_lower_string()).save()
        new_item = NetworkQuotaUpdate(description=random_lower_string())
        return network_quota_mng, model, new_item

    def case_object_store_quota(
        self,
    ) -> tuple[CRUDObjectStoreQuota, ObjectStoreQuota, ObjectStoreQuotaUpdate]:
        model = ObjectStoreQuota(description=random_lower_string()).save()
        new_item = ObjectStoreQuotaUpdate(description=random_lower_string())
        return object_store_quota_mng, model, new_item

    def case_region(
        self,
    ) -> tuple[CRUDRegion, Region, RegionUpdate]:
        model = Region(
            name=random_lower_string(), description=random_lower_string()
        ).save()
        new_item = RegionUpdate(description=random_lower_string())
        return region_mgr, model, new_item

    def case_block_storage_service(
        self,
    ) -> tuple[CRUDBlockStorageService, BlockStorageService, BlockStorageServiceUpdate]:
        model = BlockStorageService(
            endpoint=random_url(),
            name=random_service_name(ServiceType.BLOCK_STORAGE),
            description=random_lower_string(),
        ).save()
        new_item = BlockStorageServiceUpdate(description=random_lower_string())
        return block_storage_service_mng, model, new_item

    def case_compute_service(
        self,
    ) -> tuple[CRUDComputeService, ComputeService, ComputeServiceUpdate]:
        model = ComputeService(
            endpoint=random_url(),
            name=random_service_name(ServiceType.COMPUTE),
            description=random_lower_string(),
        ).save()
        new_item = ComputeServiceUpdate(description=random_lower_string())
        return compute_service_mng, model, new_item

    @case(tags="update")
    def case_identity_service(
        self,
    ) -> tuple[CRUDIdentityService, IdentityService, IdentityServiceUpdate]:
        model = IdentityService(
            endpoint=random_url(),
            name=random_service_name(ServiceType.IDENTITY),
            description=random_lower_string(),
        ).save()
        new_item = IdentityServiceUpdate(description=random_lower_string())
        return identity_service_mng, model, new_item

    def case_network_service(
        self,
    ) -> tuple[CRUDNetworkService, NetworkService, NetworkServiceUpdate]:
        model = NetworkService(
            endpoint=random_url(),
            name=random_service_name(ServiceType.NETWORK),
            description=random_lower_string(),
        ).save()
        new_item = NetworkServiceUpdate(description=random_lower_string())
        return network_service_mng, model, new_item

    def case_object_store_service(
        self,
    ) -> tuple[CRUDObjectStoreService, ObjectStoreService, ObjectStoreServiceUpdate]:
        model = ObjectStoreService(
            endpoint=random_url(),
            name=random_service_name(ServiceType.OBJECT_STORE),
            description=random_lower_string(),
        ).save()
        new_item = ObjectStoreServiceUpdate(description=random_lower_string())
        return object_store_service_mng, model, new_item

    def case_sla(
        self,
    ) -> tuple[CRUDSLA, SLA, SLAUpdate]:
        start_date, end_date = random_start_end_dates()
        model = SLA(
            doc_uuid=str(uuid4()),
            start_date=start_date,
            end_date=end_date,
            description=random_lower_string(),
        ).save()
        new_item = SLAUpdate(description=random_lower_string())
        return sla_mgr, model, new_item

    @case(tags="update")
    def case_user_group(
        self,
    ) -> tuple[CRUDUserGroup, UserGroup, UserGroupUpdate]:
        model = UserGroup(
            name=random_lower_string(), description=random_lower_string()
        ).save()
        new_item = UserGroupUpdate(description=random_lower_string())
        return user_group_mgr, model, new_item


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_patch(mgr, model, item) -> None:
    """Update only a subset of the flavor attributes."""
    cls = type(model)
    db_obj = mgr.patch(obj_in=item, db_obj=model)

    assert db_obj is not None

    assert isinstance(db_obj, cls)
    d = item.dict(exclude_unset=True)
    exclude_properties = ["uid", "element_id_property"]
    for k, v in db_obj.__properties__.items():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k, v)


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_patch_no_changes(mgr, model, item) -> None:
    """The new item is equal to the existing one. No changes."""
    cls = type(item)
    item = cls.parse_obj(model.__dict__)

    db_obj = mgr.patch(obj_in=item, db_obj=model)

    assert db_obj is None


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD, has_tag="update")
def test_update(mgr, model, item) -> None:
    """Completely update the item attributes. Override not set ones."""
    cls = type(model)
    required_properties = [i for i in model.__required_properties__ if i != "uid"]
    for property in required_properties:
        item.__setattr__(property, model.__getattribute__(property))

    db_obj = mgr.update(obj_in=item, db_obj=model)

    assert db_obj is not None
    assert isinstance(db_obj, cls)
    d = item.dict()
    exclude_properties = ["uid", "element_id_property", "is_shared"]
    for k in db_obj.__properties__.keys():
        if k not in exclude_properties:
            assert db_obj.__getattribute__(k) == d.get(k)


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD, has_tag="update")
def test_update_no_changes(mgr, model, item) -> None:
    """The new item is equal to the existing one. No changes."""
    cls = type(item)
    item = cls.parse_obj(model.__dict__)

    db_obj = mgr.update(obj_in=item, db_obj=model)

    assert db_obj is None


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_read_multi(mgr, model, item) -> None:
    items = mgr.get_multi()
    assert len(items) == 1
    assert len(set([i.uid for i in items])) == len(items)
    for item in items:
        assert isinstance(item, type(model))


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_read_multi_with_attr(mgr, model, item) -> None:
    items = mgr.get_multi(uid=model.uid)
    assert len(items) == 1
    assert len(set([i.uid for i in items])) == len(items)
    for item in items:
        assert isinstance(item, type(model))
        assert item.uid == model.uid

    properties = [i for i in model.__required_properties__ if i != "uid"]
    properties.append("description")
    attr = choice(properties)
    items = mgr.get_multi(**{attr: model.__getattribute__(attr)})
    assert len(items) == 1
    assert len(set([i.uid for i in items])) == len(items)
    for item in items:
        assert isinstance(item, type(model))
        assert item.uid == model.uid
        assert item.__getattribute__(attr) == model.__getattribute__(attr)


# TODO add tests get multi with skip, limit, sort, duplicate matches


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_read_empty_list(mgr, model, item) -> None:
    model.delete()
    items = mgr.get_multi()
    assert len(items) == 0


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_read_single_with_attr(mgr, model, item) -> None:
    item = mgr.get(uid=model.uid)
    assert isinstance(item, type(model))
    assert item.uid == model.uid

    properties = [i for i in model.__required_properties__ if i != "uid"]
    properties.append("description")
    attr = choice(properties)
    item = mgr.get(**{attr: model.__getattribute__(attr)})
    assert isinstance(item, type(model))
    assert item.uid == model.uid
    assert item.__getattribute__(attr) == model.__getattribute__(attr)


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_read_none(mgr, model, item) -> None:
    model.delete()
    assert not mgr.get()


# TODO add tests get single raises error because multiple matches
# @parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
# def test_read_single_error(mgr, model, item) -> None:
#     with pytest.raises(MultipleNodesReturned):
#         mgr.get()


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_delete(mgr, model, item) -> None:
    assert mgr.remove(db_obj=model)
    assert model.deleted


@parametrize_with_cases("mgr, model, item", cases=CaseCRUD)
def test_delete_not_existing(mgr, model, item) -> None:
    model.delete()
    assert mgr.remove(db_obj=model)
    assert model.deleted
