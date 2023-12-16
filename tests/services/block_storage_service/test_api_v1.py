from typing import Any, Dict, Optional

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.region.models import Region
from app.service.enum import ServiceType
from app.service.models import BlockStorageService
from app.service.schemas import BlockStorageServiceBase, BlockStorageServiceUpdate
from tests.common.utils import random_url
from tests.fixtures.client import CLIENTS_READ_WRITE
from tests.services.utils import random_block_storage_service_name
from tests.utils.api_v1 import BaseAPI, TestBaseAPI


class BlockStorageServiceAPI(
    BaseAPI[
        BlockStorageService,
        BlockStorageServiceBase,
        BlockStorageServiceBase,
        BlockStorageServiceUpdate,
    ]
):
    def _validate_relationships(
        self, *, obj: Dict[str, Any], db_item: BlockStorageService, public: bool = False
    ) -> None:
        db_region: Region = db_item.region.single()
        assert db_region
        assert db_region.uid == obj.pop("region").get("uid")

        quotas = obj.pop("quotas")
        assert len(db_item.quotas) == len(quotas)
        for db_quota, quota_dict in zip(
            sorted(db_item.quotas, key=lambda x: x.uid),
            sorted(quotas, key=lambda x: x.get("uid")),
        ):
            assert db_quota.uid == quota_dict.get("uid")

        return super()._validate_relationships(obj=obj, db_item=db_item, public=public)

    def random_patch_item(
        self, *, default: bool = False, from_item: Optional[BlockStorageService] = None
    ) -> BlockStorageServiceUpdate:
        item = super().random_patch_item(default=default, from_item=from_item)
        item.endpoint = random_url()
        item.name = random_block_storage_service_name()
        return item


@pytest.fixture(scope="class")
def block_storage_service_api() -> BlockStorageServiceAPI:
    return BlockStorageServiceAPI(
        base_schema=BlockStorageServiceBase,
        base_public_schema=BlockStorageServiceBase,
        update_schema=BlockStorageServiceUpdate,
        endpoint_group="block_storage_services",
        item_name="Block Storage Service",
    )


class TestBlockStorageServiceTest(TestBaseAPI):
    """Class with the basic API calls to BlockStorageService endpoints."""

    __test__ = True
    api = "block_storage_service_api"
    db_item1 = "db_block_storage_serv"
    db_item2 = "db_block_storage_serv2"
    db_item3 = "db_block_storage_serv3"

    @pytest.mark.parametrize("client, public", CLIENTS_READ_WRITE)
    def test_patch_item_with_duplicated_endpoint(
        self, request: pytest.FixtureRequest, client: TestClient, public: bool
    ) -> None:
        """Execute PATCH operations to try to update a specific item.

        Assign the endpoint of an already existing identity provider to a different
        identity provider. This is possible.
        """
        api: BaseAPI = request.getfixturevalue(self.api)
        db_item: BlockStorageService = request.getfixturevalue(self.db_item1)
        new_data: BlockStorageServiceUpdate = api.random_patch_item(from_item=db_item)
        api.patch(
            client=request.getfixturevalue(client),
            db_item=request.getfixturevalue(self.db_item2),
            new_data=new_data,
        )

    @pytest.mark.parametrize("client, public", CLIENTS_READ_WRITE)
    def test_patch_item_changing_type(
        self, request: pytest.FixtureRequest, client: TestClient, public: bool
    ) -> None:
        """Execute PATCH operation to try to change the type of a block storage service.

        At first this should not be allowed by schema construction. In any case, if a
        request arrives, it is discarded since the payload is not a block storage
        service object.
        """
        api: BaseAPI = request.getfixturevalue(self.api)
        db_item: BlockStorageService = request.getfixturevalue(self.db_item1)
        new_data: BlockStorageServiceUpdate = api.random_patch_item(from_item=db_item)
        for t in [i.value for i in ServiceType]:
            if t != ServiceType.BLOCK_STORAGE.value:
                d = new_data.dict(exclude_unset=True)
                d["type"] = t
                api.patch(
                    client=request.getfixturevalue(client),
                    db_item=request.getfixturevalue(self.db_item2),
                    new_data=d,
                    target_status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
