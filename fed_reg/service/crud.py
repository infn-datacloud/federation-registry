"""Module with Create, Read, Update and Delete operations for a Services."""

from typing import Generic, Literal, TypeVar

from fedreg.flavor.schemas import SharedFlavorCreate
from fedreg.image.schemas import SharedImageCreate
from fedreg.network.schemas import SharedNetworkCreate
from fedreg.project.models import Project
from fedreg.provider.schemas_extended import (
    BlockStorageQuotaCreateExtended,
    BlockStorageServiceCreateExtended,
    ComputeQuotaCreateExtended,
    ComputeServiceCreateExtended,
    NetworkQuotaCreateExtended,
    NetworkServiceCreateExtended,
    ObjectStoreQuotaCreateExtended,
    ObjectStoreServiceCreateExtended,
    PrivateFlavorCreateExtended,
    PrivateImageCreateExtended,
    PrivateNetworkCreateExtended,
)
from fedreg.region.models import Region
from fedreg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
)
from fedreg.service.schemas import (
    BlockStorageServiceCreate,
    BlockStorageServiceRead,
    BlockStorageServiceReadPublic,
    BlockStorageServiceUpdate,
    ComputeServiceCreate,
    ComputeServiceRead,
    ComputeServiceReadPublic,
    ComputeServiceUpdate,
    IdentityServiceCreate,
    IdentityServiceRead,
    IdentityServiceReadPublic,
    IdentityServiceUpdate,
    NetworkServiceCreate,
    NetworkServiceRead,
    NetworkServiceReadPublic,
    NetworkServiceUpdate,
    ObjectStoreServiceCreate,
    ObjectStoreServiceRead,
    ObjectStoreServiceReadPublic,
    ObjectStoreServiceUpdate,
)
from fedreg.service.schemas_extended import (
    BlockStorageServiceReadExtended,
    BlockStorageServiceReadExtendedPublic,
    ComputeServiceReadExtended,
    ComputeServiceReadExtendedPublic,
    IdentityServiceReadExtended,
    IdentityServiceReadExtendedPublic,
    NetworkServiceReadExtended,
    NetworkServiceReadExtendedPublic,
    ObjectStoreServiceReadExtended,
    ObjectStoreServiceReadExtendedPublic,
)

from fed_reg.crud import (
    CreateSchemaType,
    CRUDBase,
    ReadExtendedPublicSchemaType,
    ReadExtendedSchemaType,
    ReadPublicSchemaType,
    ReadSchemaType,
    SkipLimit,
    UpdateSchemaType,
)
from fed_reg.flavor.crud import CRUDPrivateFlavor, CRUDSharedFlavor, flavor_mgr
from fed_reg.image.crud import (
    CRUDPrivateImage,
    CRUDSharedImage,
    image_mgr,
)
from fed_reg.network.crud import (
    CRUDPrivateNetwork,
    CRUDSharedNetwork,
    network_mgr,
)
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

ModelType = TypeVar(
    "ModelType",
    bound=BlockStorageService | ComputeService | NetworkService | ObjectStoreService,
)
QuotaCreateExtendedSchemaType = TypeVar(
    "QuotaCreateExtendedSchemaType",
    bound=BlockStorageQuotaCreateExtended
    | ComputeQuotaCreateExtended
    | NetworkQuotaCreateExtended
    | ObjectStoreQuotaCreateExtended,
)
QuotaCRUDType = TypeVar(
    "QuotaCRUDType",
    bound=CRUDBlockStorageQuota
    | CRUDComputeQuota
    | CRUDNetworkQuota
    | CRUDObjectStoreQuota,
)
ResourceCreateExtendedSchemaType = TypeVar(
    "ResourceCreateExtendedSchema",
    bound=SharedFlavorCreate
    | PrivateFlavorCreateExtended
    | SharedImageCreate
    | PrivateImageCreateExtended
    | SharedNetworkCreate
    | PrivateNetworkCreateExtended,
)
ResourceCRUDType = TypeVar(
    "ResourceCRUDType",
    bound=CRUDSharedFlavor
    | CRUDPrivateFlavor
    | CRUDSharedImage
    | CRUDPrivateImage
    | CRUDSharedNetwork
    | CRUDPrivateNetwork,
)


class CRUDMultiQuota(
    CRUDBase[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ReadSchemaType,
        ReadPublicSchemaType,
        ReadExtendedSchemaType,
        ReadExtendedPublicSchemaType,
    ],
    Generic[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
        ReadSchemaType,
        ReadPublicSchemaType,
        ReadExtendedSchemaType,
        ReadExtendedPublicSchemaType,
        QuotaCRUDType,
        QuotaCreateExtendedSchemaType,
    ],
):
    """Class with the function to merge new projects into current ones."""

    def __init__(self, quota_mgr: QuotaCRUDType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quota_mgr = quota_mgr

    def _update_quotas(
        self,
        *,
        db_obj: ModelType,
        input_quotas: list[QuotaCreateExtendedSchemaType],
        provider_projects: list[Project],
    ) -> bool:
        """Update service linked quotas.

        Connect new quotas not already connect and delete old ones no more connected to
        the service. If the project already has a quota of that type, update that quota
        with the new received values.
        """
        edit = False
        seen_items = []
        for item in input_quotas:
            db_quotas = db_obj.quotas.filter(usage=item.usage, per_user=item.per_user)
            db_item = next(
                filter(lambda q: q.project.single().uuid == item.project, db_quotas),
                None,
            )

            if not db_item:
                updated_db_item = self.quota_mgr.create(
                    obj_in=item,
                    service=db_obj,
                    provider_projects=provider_projects,
                )
                seen_items.append(updated_db_item)
                edit = True
            else:
                updated_db_item = self.quota_mgr.update(
                    db_obj=db_item,
                    obj_in=item,
                    provider_projects=provider_projects,
                )
                if updated_db_item:
                    seen_items.append(updated_db_item)
                    edit = True
                seen_items.append(db_item)

        for db_item in db_obj.quotas:
            if db_item not in seen_items:
                self.quota_mgr.remove(db_obj=db_item)
                edit = True

        return edit


class CRUDBlockStorageService(
    CRUDMultiQuota[
        BlockStorageService,
        BlockStorageServiceCreate,
        BlockStorageServiceUpdate,
        BlockStorageServiceRead,
        BlockStorageServiceReadPublic,
        BlockStorageServiceReadExtended,
        BlockStorageServiceReadExtendedPublic,
        CRUDBlockStorageQuota,
        BlockStorageQuotaCreateExtended,
    ],
):
    """Block Storage Service Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: BlockStorageServiceCreateExtended,
        region: Region,
        provider_projects: list[Project] | None = None,
    ) -> BlockStorageService:
        """Create a new Block Storage Service.

        Connect the service to the given region and create all relative quotas.
        """
        if provider_projects is None:
            provider_projects = []
        db_obj = region.services.get_or_none(endpoint=obj_in.endpoint, type=obj_in.type)
        db_provider = region.provider.single()
        assert db_obj is None, (
            f"A block storage service with endpoint {obj_in.endpoint} "
            f"belonging to provider {db_provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.region.connect(region)

        for quota in obj_in.quotas:
            self.quota_mgr.create(
                obj_in=quota, service=db_obj, provider_projects=provider_projects
            )
        return db_obj

    def update(
        self,
        *,
        db_obj: BlockStorageService,
        obj_in: BlockStorageServiceCreateExtended,
        provider_projects: list[Project] | None,
    ) -> BlockStorageService | None:
        """Update Block Storage Service attributes. Update linked quotas."""
        if provider_projects is None:
            provider_projects = []
        edit = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj.save() if edit or edit_content else None


class CRUDComputeService(
    CRUDMultiQuota[
        ComputeService,
        ComputeServiceCreate,
        ComputeServiceUpdate,
        ComputeServiceRead,
        ComputeServiceReadPublic,
        ComputeServiceReadExtended,
        ComputeServiceReadExtendedPublic,
        CRUDComputeQuota,
        ComputeQuotaCreateExtended,
    ],
):
    """Compute Service Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: ComputeServiceCreateExtended,
        region: Region,
        provider_projects: list[Project] | None = None,
    ) -> ComputeService:
        """Create a new Block Storage Service.

        Connect the service to the given region and create all relative flavors, images
        and quotas.
        """
        if provider_projects is None:
            provider_projects = []
        db_obj = region.services.get_or_none(endpoint=obj_in.endpoint, type=obj_in.type)
        db_provider = region.provider.single()
        assert db_obj is None, (
            f"A compute service with endpoint {obj_in.endpoint} "
            f"belonging to provider {db_provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.region.connect(region)

        for quota in obj_in.quotas:
            self.quota_mgr.create(
                obj_in=quota, service=db_obj, provider_projects=provider_projects
            )
        for flavor in obj_in.flavors:
            flavor_mgr.create(
                obj_in=flavor, service=db_obj, provider_projects=provider_projects
            )
        for image in obj_in.images:
            image_mgr.create(
                obj_in=image, service=db_obj, provider_projects=provider_projects
            )

        return db_obj

    def update(
        self,
        *,
        db_obj: ComputeService,
        obj_in: ComputeServiceCreateExtended,
        provider_projects: list[Project] | None,
    ) -> ComputeService | None:
        """Update Compute Service attributes.

        Update linked quotas, flavors and images.
        """
        if provider_projects is None:
            provider_projects = []
        edit1 = self.__update_flavors(
            db_obj=db_obj,
            input_flavors=obj_in.flavors,
            provider_projects=provider_projects,
        )
        edit2 = self.__update_images(
            db_obj=db_obj,
            input_images=obj_in.images,
            provider_projects=provider_projects,
        )
        edit3 = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)

        return db_obj.save() if edit1 or edit2 or edit3 or edit_content else None

    def __update_flavors(
        self,
        *,
        db_obj: ComputeService,
        input_flavors: list[SharedFlavorCreate | PrivateFlavorCreateExtended],
        provider_projects: list[Project],
    ) -> bool:
        """Update service linked flavors.

        Connect new flavors not already connect, leave untouched already linked ones and
        delete old ones no more connected to the service.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.flavors}
        for item in input_flavors:
            db_item = db_items.pop(item.uuid, None)

            if not db_item:
                flavor_mgr.create(
                    obj_in=item, service=db_obj, provider_projects=provider_projects
                )
                edit = True
            else:
                updated_db_item = flavor_mgr.update(
                    db_obj=db_item, obj_in=item, provider_projects=provider_projects
                )
                if updated_db_item:
                    edit = True

        for db_item in db_items.values():
            if len(db_item.services) == 1:
                flavor_mgr.remove(db_obj=db_item)
            else:
                # TODO in futura flavors will belong to only one service.
                # This else case will be removed.
                db_obj.flavors.disconnect(db_item)
            edit = True

        return edit

    def __update_images(
        self,
        *,
        db_obj: ComputeService,
        input_images: list[SharedImageCreate | PrivateImageCreateExtended],
        provider_projects: list[Project],
    ) -> bool:
        """Update service linked images.

        Connect new images not already connect, leave untouched already linked ones and
        delete old ones no more connected to the service.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.images}
        for item in input_images:
            db_item = db_items.pop(item.uuid, None)

            if not db_item:
                image_mgr.create(
                    obj_in=item, service=db_obj, provider_projects=provider_projects
                )
                edit = True
            else:
                updated_db_item = image_mgr.update(
                    db_obj=db_item, obj_in=item, provider_projects=provider_projects
                )
                if updated_db_item:
                    edit = True

        for db_item in db_items.values():
            if len(db_item.services) == 1:
                image_mgr.remove(db_obj=db_item)
            else:
                db_obj.images.disconnect(db_item)
            edit = True

        return edit


class CRUDIdentityService(
    CRUDBase[
        IdentityService,
        IdentityServiceCreate,
        IdentityServiceUpdate,
        IdentityServiceRead,
        IdentityServiceReadPublic,
        IdentityServiceReadExtended,
        IdentityServiceReadExtendedPublic,
    ]
):
    """Identity Service Create, Read, Update and Delete operations."""

    def create(
        self, *, obj_in: IdentityServiceCreate, region: Region
    ) -> IdentityService:
        """Create a new Identity Service.

        Connect the service to the given region.
        """
        db_obj = region.services.get_or_none(endpoint=obj_in.endpoint, type=obj_in.type)
        assert db_obj is None, (
            f"An identity service with endpoint {obj_in.endpoint} "
            f"belonging to region {region.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.region.connect(region)
        return db_obj


class CRUDNetworkService(
    CRUDMultiQuota[
        NetworkService,
        NetworkServiceCreate,
        NetworkServiceUpdate,
        NetworkServiceRead,
        NetworkServiceReadPublic,
        NetworkServiceReadExtended,
        NetworkServiceReadExtendedPublic,
        CRUDNetworkQuota,
        NetworkQuotaCreateExtended,
    ],
):
    """Network Service Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: NetworkServiceCreateExtended,
        region: Region,
        provider_projects: list[Project] | None = None,
    ) -> NetworkService:
        """Create a new Block Storage Service.

        Connect the service to the given region and create all relative networks.
        """
        if provider_projects is None:
            provider_projects = []
        db_obj = region.services.get_or_none(endpoint=obj_in.endpoint, type=obj_in.type)
        db_provider = region.provider.single()
        assert db_obj is None, (
            f"A network service with endpoint {obj_in.endpoint} "
            f"belonging to provider {db_provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.region.connect(region)

        for quota in obj_in.quotas:
            self.quota_mgr.create(
                obj_in=quota, service=db_obj, provider_projects=provider_projects
            )
        for network in obj_in.networks:
            network_mgr.create(
                obj_in=network, service=db_obj, provider_projects=provider_projects
            )
        return db_obj

    def update(
        self,
        *,
        db_obj: NetworkService,
        obj_in: NetworkServiceCreateExtended,
        provider_projects: list[Project] | None,
    ) -> NetworkService | None:
        """Update Network Service attributes. Update linked quotas and networks."""
        if provider_projects is None:
            provider_projects = []

        edit1 = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edit2 = self.__update_networks(
            db_obj=db_obj,
            input_networks=obj_in.networks,
            provider_projects=provider_projects,
        )
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)

        return db_obj.save() if edit1 or edit2 or edit_content else None

    def __update_networks(
        self,
        *,
        db_obj: NetworkService,
        input_networks: list[SharedNetworkCreate | PrivateNetworkCreateExtended],
        provider_projects: list[Project],
    ) -> bool:
        """Update service linked networks.

        Connect new networks not already connect, leave untouched already linked ones
        and delete old ones no more connected to the service.
        """
        edit = False
        db_items = {db_item.uuid: db_item for db_item in db_obj.networks}
        for item in input_networks:
            db_item = db_items.pop(item.uuid, None)

            if not db_item:
                network_mgr.create(
                    obj_in=item, service=db_obj, provider_projects=provider_projects
                )
                edit = True
            else:
                updated_data = network_mgr.update(
                    db_obj=db_item, obj_in=item, provider_projects=provider_projects
                )
                if updated_data:
                    edit = True

        for db_item in db_items.values():
            network_mgr.remove(db_obj=db_item)
            edit = True

        return edit


class CRUDObjectStoreService(
    CRUDMultiQuota[
        ObjectStoreService,
        ObjectStoreServiceCreate,
        ObjectStoreServiceUpdate,
        ObjectStoreServiceRead,
        ObjectStoreServiceReadPublic,
        ObjectStoreServiceReadExtended,
        ObjectStoreServiceReadExtendedPublic,
        CRUDObjectStoreQuota,
        ObjectStoreQuotaCreateExtended,
    ],
):
    """Object Storage Service Create, Read, Update and Delete operations."""

    def create(
        self,
        *,
        obj_in: ObjectStoreServiceCreateExtended,
        region: Region,
        provider_projects: list[Project] | None = None,
    ) -> ObjectStoreService:
        """Create a new Object Storage Service.

        Connect the service to the given region and create all relative quotas.
        """
        if provider_projects is None:
            provider_projects = []
        db_obj = region.services.get_or_none(endpoint=obj_in.endpoint, type=obj_in.type)
        db_provider = region.provider.single()
        assert db_obj is None, (
            f"An object store service with endpoint {obj_in.endpoint} "
            f"belonging to provider {db_provider.name} already exists"
        )
        db_obj = super().create(obj_in=obj_in)
        db_obj.region.connect(region)

        for quota in obj_in.quotas:
            self.quota_mgr.create(
                obj_in=quota, service=db_obj, provider_projects=provider_projects
            )
        return db_obj

    def update(
        self,
        *,
        db_obj: ObjectStoreService,
        obj_in: ObjectStoreServiceCreateExtended,
        provider_projects: list[Project] | None,
    ) -> ObjectStoreService | None:
        """Update Object Storage Service attributes.

        By default do not update relationships or default values. If force is True,
        update linked quotas and apply default values when explicit.
        """
        if provider_projects is None:
            provider_projects = []
        edit = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edit_content = self._update(db_obj=db_obj, obj_in=obj_in, force=True)
        return db_obj.save() if edit or edit_content else None


class CRUDServiceDispatcher(
    SkipLimit[
        BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService
    ],
):
    """Flavor (both shared and private) Create, Read, Update and Delete operations."""

    def __init__(
        self,
        *,
        block_storage_mgr: CRUDBlockStorageService,
        compute_mgr: CRUDComputeService,
        identity_mgr: CRUDIdentityService,
        network_mgr: CRUDNetworkService,
        object_store_mgr: CRUDObjectStoreService,
    ):
        self.__block_storage_mgr = block_storage_mgr
        self.__compute_mgr = compute_mgr
        self.__identity_mgr = identity_mgr
        self.__network_mgr = network_mgr
        self.__object_store_mgr = object_store_mgr

    # def get(
    #     self, **kwargs
    # ) -> (
    #     BlockStorageService
    #     | ComputeService
    #     | IdentityService
    #     | NetworkService
    #     | ObjectStoreService
    #     | None
    # ):
    #     """Get a single resource. Return None if the resource is not found."""
    #     item = self.__block_storage_mgr.get(**kwargs)
    #     if item:
    #         return item
    #     item = self.__compute_mgr.get(**kwargs)
    #     if item:
    #         return item
    #     item = self.__identity_mgr.get(**kwargs)
    #     if item:
    #         return item
    #     item = self.__network_mgr.get(**kwargs)
    #     if item:
    #         return item
    #     item = self.__object_store_mgr.get(**kwargs)
    #     if item:
    #         return item

    # def get_multi(
    #     self, skip: int = 0, limit: int | None = None, sort: str | None = None,
    # **kwargs
    # ) -> list[
    #     BlockStorageService
    #     | ComputeService
    #     | IdentityService
    #     | NetworkService
    #     | ObjectStoreService
    # ]:
    #     """Get list of resources."""
    #     req_is_shared = kwargs.get("is_shared", None)

    #     if req_is_shared is None:
    #         shared_items = self.__compute_mgr.get_multi(**kwargs)
    #         private_items = self.__block_storage_mgr.get_multi(**kwargs)

    #         if sort:
    #             if sort.startswith("-"):
    #                 sort = sort[1:]
    #                 reverse = True
    #             sorting = [sort, "uid"]
    #             items = sorted(
    #                 [*shared_items, *private_items],
    #                 key=lambda x: (x.__getattribute__(k) for k in sorting),
    #                 reverse=reverse,
    #             )

    #         return self._apply_limit_and_skip(items=items, skip=skip, limit=limit)

    #     if req_is_shared:
    #         return self.__compute_mgr.get_multi(
    #             skip=skip, limit=limit, sort=sort, **kwargs
    #         )
    #     return self.__block_storage_mgr.get_multi(
    #         skip=skip, limit=limit, sort=sort, **kwargs
    #     )

    def create(
        self,
        *,
        obj_in: BlockStorageServiceCreateExtended
        | ComputeServiceCreateExtended
        | IdentityServiceCreate
        | NetworkServiceCreateExtended
        | ObjectStoreServiceCreateExtended,
        provider_projects: list[Project] | None = None,
        **kwargs,
    ) -> (
        BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService
    ):
        """Create a new service."""
        if isinstance(obj_in, BlockStorageServiceCreateExtended):
            return self.__block_storage_mgr.create(
                obj_in=obj_in, provider_projects=provider_projects, **kwargs
            )
        if isinstance(obj_in, ComputeServiceCreateExtended):
            return self.__compute_mgr.create(
                obj_in=obj_in, provider_projects=provider_projects, **kwargs
            )
        if isinstance(obj_in, IdentityServiceCreate):
            return self.__identity_mgr.create(obj_in=obj_in, **kwargs)
        if isinstance(obj_in, NetworkServiceCreateExtended):
            return self.__network_mgr.create(
                obj_in=obj_in, provider_projects=provider_projects, **kwargs
            )
        if isinstance(obj_in, ObjectStoreServiceCreateExtended):
            return self.__object_store_mgr.create(
                obj_in=obj_in, provider_projects=provider_projects, **kwargs
            )
        raise ValueError(f"Not supported service type {obj_in.type}")

    def update(
        self,
        *,
        db_obj: BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService,
        obj_in: BlockStorageServiceCreateExtended
        | ComputeServiceCreateExtended
        | IdentityServiceCreate
        | NetworkServiceCreateExtended
        | ObjectStoreServiceCreateExtended,
        provider_projects: list[Project] | None = None,
    ) -> (
        BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService
        | None
    ):
        """Update and existing service."""
        if isinstance(db_obj, BlockStorageService):
            return self.__block_storage_mgr.update(
                obj_in=obj_in, db_obj=db_obj, provider_projects=provider_projects
            )
        if isinstance(db_obj, ComputeService):
            return self.__compute_mgr.update(
                obj_in=obj_in, db_obj=db_obj, provider_projects=provider_projects
            )
        if isinstance(db_obj, IdentityService):
            return self.__identity_mgr.update(obj_in=obj_in, db_obj=db_obj)
        if isinstance(db_obj, NetworkService):
            return self.__network_mgr.update(
                obj_in=obj_in, db_obj=db_obj, provider_projects=provider_projects
            )
        if isinstance(db_obj, ObjectStoreService):
            return self.__object_store_mgr.update(
                obj_in=obj_in, db_obj=db_obj, provider_projects=provider_projects
            )
        raise ValueError(f"Not supported service type {db_obj.type}")

    def patch(
        self,
        *,
        db_obj: BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService,
        obj_in: UpdateSchemaType,
    ) -> (
        BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService
        | None
    ):
        """Patch an existing service."""
        if isinstance(db_obj, BlockStorageService):
            return self.__block_storage_mgr.patch(obj_in=obj_in, db_obj=db_obj)
        if isinstance(db_obj, ComputeService):
            return self.__compute_mgr.patch(obj_in=obj_in, db_obj=db_obj)
        if isinstance(db_obj, IdentityService):
            return self.__identity_mgr.patch(obj_in=obj_in, db_obj=db_obj)
        if isinstance(db_obj, NetworkService):
            return self.__network_mgr.patch(obj_in=obj_in, db_obj=db_obj)
        if isinstance(db_obj, ObjectStoreService):
            return self.__object_store_mgr.patch(obj_in=obj_in, db_obj=db_obj)
        raise ValueError(f"Not supported service type {db_obj.type}")

    def remove(
        self,
        *,
        db_obj: BlockStorageService
        | ComputeService
        | IdentityService
        | NetworkService
        | ObjectStoreService,
    ) -> Literal[True]:
        """Remove an existing service."""
        if isinstance(db_obj, BlockStorageService):
            return self.__block_storage_mgr.remove(db_obj=db_obj)
        if isinstance(db_obj, ComputeService):
            return self.__compute_mgr.remove(db_obj=db_obj)
        if isinstance(db_obj, IdentityService):
            return self.__identity_mgr.remove(db_obj=db_obj)
        if isinstance(db_obj, NetworkService):
            return self.__network_mgr.remove(db_obj=db_obj)
        if isinstance(db_obj, ObjectStoreService):
            return self.__object_store_mgr.remove(db_obj=db_obj)
        raise ValueError(f"Not supported service type {db_obj.type}")


block_storage_service_mng = CRUDBlockStorageService(
    model=BlockStorageService,
    create_schema=BlockStorageServiceCreate,
    update_schema=BlockStorageServiceUpdate,
    read_schema=BlockStorageServiceRead,
    read_public_schema=BlockStorageServiceReadPublic,
    read_extended_schema=BlockStorageServiceReadExtended,
    read_extended_public_schema=BlockStorageServiceReadExtendedPublic,
    quota_mgr=block_storage_quota_mng,
)
compute_service_mng = CRUDComputeService(
    model=ComputeService,
    create_schema=ComputeServiceCreate,
    update_schema=ComputeServiceUpdate,
    read_schema=ComputeServiceRead,
    read_public_schema=ComputeServiceReadPublic,
    read_extended_schema=ComputeServiceReadExtended,
    read_extended_public_schema=ComputeServiceReadExtendedPublic,
    quota_mgr=compute_quota_mng,
)
identity_service_mng = CRUDIdentityService(
    model=IdentityService,
    create_schema=IdentityServiceCreate,
    update_schema=IdentityServiceUpdate,
    read_schema=IdentityServiceRead,
    read_public_schema=IdentityServiceReadPublic,
    read_extended_schema=IdentityServiceReadExtended,
    read_extended_public_schema=IdentityServiceReadExtendedPublic,
)
network_service_mng = CRUDNetworkService(
    model=NetworkService,
    create_schema=NetworkServiceCreate,
    update_schema=NetworkServiceUpdate,
    read_schema=NetworkServiceRead,
    read_public_schema=NetworkServiceReadPublic,
    read_extended_schema=NetworkServiceReadExtended,
    read_extended_public_schema=NetworkServiceReadExtendedPublic,
    quota_mgr=network_quota_mng,
)
object_store_service_mng = CRUDObjectStoreService(
    model=ObjectStoreService,
    create_schema=ObjectStoreServiceCreate,
    update_schema=ObjectStoreServiceUpdate,
    read_schema=ObjectStoreServiceRead,
    read_public_schema=ObjectStoreServiceReadPublic,
    read_extended_schema=ObjectStoreServiceReadExtended,
    read_extended_public_schema=ObjectStoreServiceReadExtendedPublic,
    quota_mgr=object_store_quota_mng,
)
service_mgr = CRUDServiceDispatcher(
    block_storage_mgr=block_storage_service_mng,
    compute_mgr=compute_service_mng,
    identity_mgr=identity_service_mng,
    network_mgr=network_service_mng,
    object_store_mgr=object_store_service_mng,
)
