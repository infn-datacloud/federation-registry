"""Module with Create, Read, Update and Delete operations for a Services."""

from typing import Generic, TypeVar

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
    ) -> ModelType | None:
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

        return db_obj.save() if edit else None


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
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
            db_obj.region.connect(region)
        else:
            db_provider = region.provider.single()
            raise ValueError(
                f"A block storage service with endpoint {obj_in.endpoint} "
                f"belonging to provider {db_provider.name} already exists"
            )
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
        edited_obj1 = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edited_obj2 = super().update(db_obj=db_obj, obj_in=obj_in)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


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
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
            db_obj.region.connect(region)
        else:
            db_provider = region.provider.single()
            raise ValueError(
                f"A compute service with endpoint {obj_in.endpoint} "
                f"belonging to provider {db_provider.name} already exists"
            )
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
        edited_obj1 = self._update_flavors(
            db_obj=db_obj,
            input_flavors=obj_in.flavors,
            provider_projects=provider_projects,
        )
        edited_obj2 = self._update_images(
            db_obj=db_obj,
            input_images=obj_in.images,
            provider_projects=provider_projects,
        )
        edited_obj3 = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edited_obj4 = super().update(db_obj=db_obj, obj_in=obj_in)

        if edited_obj4:
            return edited_obj4
        if edited_obj3:
            return edited_obj3
        if edited_obj2:
            return edited_obj2
        return edited_obj1

    def _update_flavors(
        self,
        *,
        db_obj: ComputeService,
        input_flavors: list[SharedFlavorCreate | PrivateFlavorCreateExtended],
        provider_projects: list[Project],
    ) -> ComputeService | None:
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

        return db_obj.save() if edit else None

    def _update_images(
        self,
        *,
        db_obj: ComputeService,
        input_images: list[SharedImageCreate | PrivateImageCreateExtended],
        provider_projects: list[Project],
    ) -> ComputeService | None:
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

        return db_obj.save() if edit else None


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
        db_obj = region.services.filter(endpoint=obj_in.endpoint, type=obj_in.type)
        if db_obj:
            raise ValueError(
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
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
            db_obj.region.connect(region)
        else:
            db_provider = region.provider.single()
            raise ValueError(
                f"A network service with endpoint {obj_in.endpoint} "
                f"belonging to provider {db_provider.name} already exists"
            )
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

        edited_obj1 = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edited_obj2 = self._update_networks(
            db_obj=db_obj,
            input_networks=obj_in.networks,
            provider_projects=provider_projects,
        )
        edited_obj3 = super().update(db_obj=db_obj, obj_in=obj_in)

        if edited_obj3:
            return edited_obj3
        if edited_obj2:
            return edited_obj2
        return edited_obj1

    def _update_networks(
        self,
        *,
        db_obj: NetworkService,
        input_networks: list[SharedNetworkCreate | PrivateNetworkCreateExtended],
        provider_projects: list[Project],
    ) -> NetworkService | None:
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

        return db_obj.save() if edit else None


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
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
            db_obj.region.connect(region)
        else:
            db_provider = region.provider.single()
            raise ValueError(
                f"An object store service with endpoint {obj_in.endpoint} "
                f"belonging to provider {db_provider.name} already exists"
            )
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
        edited_obj1 = self._update_quotas(
            db_obj=db_obj,
            input_quotas=obj_in.quotas,
            provider_projects=provider_projects,
        )
        edited_obj2 = super().update(db_obj=db_obj, obj_in=obj_in)
        return edited_obj2 if edited_obj2 is not None else edited_obj1


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
