from pytest_cases import case, parametrize

from fed_reg.flavor.models import Flavor, PrivateFlavor, SharedFlavor
from fed_reg.image.models import Image, PrivateImage, SharedImage
from fed_reg.network.models import Network, PrivateNetwork, SharedNetwork
from fed_reg.project.models import Project
from fed_reg.service.models import (
    BlockStorageService,
    ComputeService,
    IdentityService,
    NetworkService,
    ObjectStoreService,
    Service,
)
from tests.create_dict import flavor_model_dict, image_model_dict, network_model_dict


class CaseAttr:
    @case(tags=("attr", "mandatory"))
    @parametrize(value=("name", "endpoint"))
    def case_mandatory(self, value: str) -> str:
        return value

    @case(tags=("attr", "optional"))
    @parametrize(value=("description",))
    def case_optional(self, value: str) -> str:
        return value


class CaseClass:
    @case(tags="class")
    def case_service(self) -> type[Service]:
        return Service

    @case(tags=("class", "derived"))
    def case_block_storage_service(self) -> type[BlockStorageService]:
        return BlockStorageService

    @case(tags=("class", "derived"))
    def case_compute_service(self) -> type[ComputeService]:
        return ComputeService

    @case(tags=("class", "derived"))
    def case_identity_service(self) -> type[IdentityService]:
        return IdentityService

    @case(tags=("class", "derived"))
    def case_network_service(self) -> type[NetworkService]:
        return NetworkService

    @case(tags=("class", "derived"))
    def case_object_store_service(self) -> type[ObjectStoreService]:
        return ObjectStoreService


class CaseModel:
    @case(tags="model")
    def case_service(self, service_model: Service) -> Service:
        return service_model

    @case(tags=("model", "derived", "with_quotas"))
    def case_block_storage_service(
        self, block_storage_service_model: BlockStorageService
    ) -> BlockStorageService:
        return block_storage_service_model

    @case(tags=("model", "derived", "with_quotas"))
    def case_compute_service(
        self, compute_service_model: ComputeService
    ) -> ComputeService:
        return compute_service_model

    @case(tags=("model", "derived"))
    def case_identity_service(
        self, identity_service_model: IdentityService
    ) -> IdentityService:
        return identity_service_model

    @case(tags=("model", "derived", "with_quotas"))
    def case_network_service(
        self, network_service_model: NetworkService
    ) -> NetworkService:
        return network_service_model

    @case(tags=("model", "derived", "with_quotas"))
    def case_object_store_service(
        self, object_store_service_model: ObjectStoreService
    ) -> ObjectStoreService:
        return object_store_service_model


class CaseFlavor:
    @case(tags=("flavor", "single"))
    def case_flavor(self, flavor_model: Flavor) -> Flavor:
        return flavor_model

    @case(tags=("flavor", "single"))
    def case_private_flavor(
        self, private_flavor_model: PrivateFlavor, project_model: Project
    ) -> PrivateFlavor:
        private_flavor_model.projects.connect(project_model)
        return private_flavor_model

    @case(tags=("flavor", "single"))
    def case_shared_flavor(self, shared_flavor_model: SharedFlavor) -> SharedFlavor:
        return shared_flavor_model

    @case(tags=("flavor", "multi"))
    def case_shared_flavors(self) -> list[SharedFlavor]:
        return [
            SharedFlavor(**flavor_model_dict()).save(),
            SharedFlavor(**flavor_model_dict()).save(),
        ]

    @case(tags=("flavor", "multi"))
    def case_private_flavors(self, project_model: Project) -> list[PrivateFlavor]:
        items = [
            PrivateFlavor(**flavor_model_dict()).save(),
            PrivateFlavor(**flavor_model_dict()).save(),
        ]
        for item in items:
            item.projects.connect(project_model)
        return items

    @case(tags=("flavor", "multi"))
    def case_mixed_flavors(
        self,
        private_flavor_model: PrivateFlavor,
        shared_flavor_model: SharedFlavor,
        project_model: Project,
    ) -> list[PrivateFlavor | SharedFlavor]:
        private_flavor_model.projects.connect(project_model)
        return [private_flavor_model, shared_flavor_model]


class CaseImage:
    @case(tags=("image", "single"))
    def case_image(self, image_model: Image) -> Image:
        return image_model

    @case(tags=("image", "single"))
    def case_private_image(
        self, private_image_model: PrivateImage, project_model: Project
    ) -> PrivateImage:
        private_image_model.projects.connect(project_model)
        return private_image_model

    @case(tags=("image", "single"))
    def case_shared_image(self, shared_image_model: SharedImage) -> SharedImage:
        return shared_image_model

    @case(tags=("image", "multi"))
    def case_shared_images(self) -> list[SharedImage]:
        return [
            SharedImage(**image_model_dict()).save(),
            SharedImage(**image_model_dict()).save(),
        ]

    @case(tags=("image", "multi"))
    def case_private_images(self, project_model: Project) -> list[PrivateImage]:
        items = [
            PrivateImage(**image_model_dict()).save(),
            PrivateImage(**image_model_dict()).save(),
        ]
        for item in items:
            item.projects.connect(project_model)
        return items

    @case(tags=("image", "multi"))
    def case_mixed_images(
        self,
        private_image_model: PrivateImage,
        shared_image_model: SharedImage,
        project_model: Project,
    ) -> list[PrivateImage | SharedImage]:
        private_image_model.projects.connect(project_model)
        return [private_image_model, shared_image_model]


class CaseNetwork:
    @case(tags=("network", "single"))
    def case_network(self, network_model: Network) -> Network:
        return network_model

    @case(tags=("network", "single"))
    def case_private_network(
        self, private_network_model: PrivateNetwork, project_model: Project
    ) -> PrivateNetwork:
        private_network_model.project.connect(project_model)
        return private_network_model

    @case(tags=("network", "single"))
    def case_shared_network(self, shared_network_model: SharedNetwork) -> SharedNetwork:
        return shared_network_model

    @case(tags=("network", "multi"))
    def case_shared_networks(self) -> list[SharedNetwork]:
        return [
            SharedNetwork(**network_model_dict()).save(),
            SharedNetwork(**network_model_dict()).save(),
        ]

    @case(tags=("network", "multi"))
    def case_private_networks(self, project_model: Project) -> list[PrivateNetwork]:
        items = [
            PrivateNetwork(**network_model_dict()).save(),
            PrivateNetwork(**network_model_dict()).save(),
        ]
        for item in items:
            item.project.connect(project_model)
        return items

    @case(tags=("network", "multi"))
    def case_mixed_networks(
        self,
        private_network_model: PrivateNetwork,
        shared_network_model: SharedNetwork,
        project_model: Project,
    ) -> list[PrivateNetwork | SharedNetwork]:
        private_network_model.project.connect(project_model)
        return [private_network_model, shared_network_model]
