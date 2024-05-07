from random import randint
from typing import Any, Union
from unittest.mock import patch

import pytest
from neomodel import (
    AttemptedCardinalityViolation,
    CardinalityViolation,
    RelationshipManager,
    RequiredProperty,
)
from pytest_cases import parametrize, parametrize_with_cases

from fed_reg.project.models import Project
from fed_reg.quota.models import BlockStorageQuota, ComputeQuota, NetworkQuota, Quota
from fed_reg.service.models import BlockStorageService, ComputeService, NetworkService
from tests.create_dict import (
    block_storage_service_model_dict,
    compute_service_model_dict,
    network_service_model_dict,
    project_model_dict,
    quota_model_dict,
)


class CaseQuotaEmpty:
    def case_block_storage_quota(self) -> BlockStorageQuota:
        return BlockStorageQuota()

    def case_compute_quota(self) -> ComputeQuota:
        return ComputeQuota()

    def case_network_quota(self) -> NetworkQuota:
        return NetworkQuota()


class CaseBlockStorageAttr:
    @parametrize(key=["gigabytes", "volumes", "per_volume_gigabytes"])
    def case_int(self, key: str) -> tuple[str, int]:
        return key, randint(0, 100)


class CaseComputeAttr:
    @parametrize(key=["cores", "instances", "ram"])
    def case_int(self, key: str) -> tuple[str, int]:
        return key, randint(0, 100)


class CaseNetworkAttr:
    @parametrize(
        key=[
            "public_ips",
            "networks",
            "ports",
            "security_groups",
            "security_group_rules",
        ]
    )
    def case_int(self, key: str) -> tuple[str, int]:
        return key, randint(0, 100)


class CaseQuotaModel:
    def case_block_storage_quota(
        self, block_storage_quota_model: BlockStorageQuota
    ) -> BlockStorageQuota:
        return block_storage_quota_model

    def case_compute_quota(self, compute_quota_model: ComputeQuota) -> ComputeQuota:
        return compute_quota_model

    def case_network_quota(self, network_quota_model: NetworkQuota) -> NetworkQuota:
        return network_quota_model


def test_block_storage_default_attr() -> None:
    d = quota_model_dict()
    item = BlockStorageQuota(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.type == d.get("type")
    assert item.per_user is False
    assert item.gigabytes is None
    assert item.per_volume_gigabytes is None
    assert item.volumes is None
    assert isinstance(item.service, RelationshipManager)


def test_compute_default_attr() -> None:
    d = quota_model_dict()
    item = ComputeQuota(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.type == d.get("type")
    assert item.per_user is False
    assert item.cores is None
    assert item.instances is None
    assert item.ram is None
    assert isinstance(item.service, RelationshipManager)


def test_network_default_attr() -> None:
    d = quota_model_dict()
    item = NetworkQuota(**d)
    assert item.uid is not None
    assert item.description == ""
    assert item.type == d.get("type")
    assert item.per_user is False
    assert item.public_ips is None
    assert item.networks is None
    assert item.ports is None
    assert item.security_groups is None
    assert item.security_group_rules is None
    assert isinstance(item.service, RelationshipManager)


@parametrize_with_cases("item", cases=CaseQuotaEmpty)
def test_missing_attr(
    item: Union[BlockStorageQuota, ComputeQuota, NetworkQuota],
) -> None:
    with pytest.raises(RequiredProperty):
        item.save()


@parametrize_with_cases("key, value", cases=CaseBlockStorageAttr)
def test_block_storage_attr(key: str, value: Any) -> None:
    d = quota_model_dict()
    d[key] = value

    item = BlockStorageQuota(**d)
    saved = item.save()

    assert saved.element_id_property
    assert saved.uid == item.uid
    assert saved.__getattribute__(key) == value


@parametrize_with_cases("key, value", cases=CaseComputeAttr)
def test_compute_attr(key: str, value: Any) -> None:
    d = quota_model_dict()
    d[key] = value

    item = ComputeQuota(**d)
    saved = item.save()

    assert saved.element_id_property
    assert saved.uid == item.uid
    assert saved.__getattribute__(key) == value


@parametrize_with_cases("key, value", cases=CaseNetworkAttr)
def test_network_attr(key: str, value: Any) -> None:
    d = quota_model_dict()
    d[key] = value

    item = NetworkQuota(**d)
    saved = item.save()

    assert saved.element_id_property
    assert saved.uid == item.uid
    assert saved.__getattribute__(key) == value


@parametrize_with_cases("quota_model", cases=CaseQuotaModel)
def test_required_rel(
    quota_model: Union[BlockStorageQuota, ComputeQuota, NetworkQuota],
) -> None:
    with pytest.raises(CardinalityViolation):
        quota_model.service.all()
    with pytest.raises(CardinalityViolation):
        quota_model.service.single()
    with pytest.raises(CardinalityViolation):
        quota_model.project.all()
    with pytest.raises(CardinalityViolation):
        quota_model.project.single()


@parametrize_with_cases("quota_model", cases=CaseQuotaModel)
def test_linked_project(
    quota_model: Union[BlockStorageQuota, ComputeQuota, NetworkQuota],
    project_model: Project,
) -> None:
    assert quota_model.project.name
    assert quota_model.project.source
    assert isinstance(quota_model.project.source, Quota)
    assert quota_model.project.source.uid == quota_model.uid
    assert quota_model.project.definition
    assert quota_model.project.definition["node_class"] == Project

    r = quota_model.project.connect(project_model)
    assert r is True

    assert len(quota_model.project.all()) == 1
    project = quota_model.project.single()
    assert isinstance(project, Project)
    assert project.uid == project_model.uid


@parametrize_with_cases("quota_model", cases=CaseQuotaModel)
def test_multiple_linked_projects(
    quota_model: Union[BlockStorageQuota, ComputeQuota, NetworkQuota],
) -> None:
    item = Project(**project_model_dict()).save()
    quota_model.project.connect(item)
    item = Project(**project_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        quota_model.project.connect(item)

    with patch("neomodel.match.QueryBuilder._count", return_value=0):
        quota_model.project.connect(item)
        with pytest.raises(CardinalityViolation):
            quota_model.project.all()


def test_linked_block_storage_service(
    block_storage_quota_model: BlockStorageQuota,
    block_storage_service_model: BlockStorageService,
) -> None:
    assert block_storage_quota_model.service.name
    assert block_storage_quota_model.service.source
    assert isinstance(block_storage_quota_model.service.source, Quota)
    assert block_storage_quota_model.service.source.uid == block_storage_quota_model.uid
    assert block_storage_quota_model.service.definition
    assert (
        block_storage_quota_model.service.definition["node_class"]
        == BlockStorageService
    )

    r = block_storage_quota_model.service.connect(block_storage_service_model)
    assert r is True

    assert len(block_storage_quota_model.service.all()) == 1
    service = block_storage_quota_model.service.single()
    assert isinstance(service, BlockStorageService)
    assert service.uid == block_storage_service_model.uid


def test_linked_compute_service(
    compute_quota_model: ComputeQuota, compute_service_model: ComputeService
) -> None:
    assert compute_quota_model.service.name
    assert compute_quota_model.service.source
    assert isinstance(compute_quota_model.service.source, Quota)
    assert compute_quota_model.service.source.uid == compute_quota_model.uid
    assert compute_quota_model.service.definition
    assert compute_quota_model.service.definition["node_class"] == ComputeService

    r = compute_quota_model.service.connect(compute_service_model)
    assert r is True

    assert len(compute_quota_model.service.all()) == 1
    service = compute_quota_model.service.single()
    assert isinstance(service, ComputeService)
    assert service.uid == compute_service_model.uid


def test_linked_network_service(
    network_quota_model: NetworkQuota, network_service_model: NetworkService
) -> None:
    assert network_quota_model.service.name
    assert network_quota_model.service.source
    assert isinstance(network_quota_model.service.source, Quota)
    assert network_quota_model.service.source.uid == network_quota_model.uid
    assert network_quota_model.service.definition
    assert network_quota_model.service.definition["node_class"] == NetworkService

    r = network_quota_model.service.connect(network_service_model)
    assert r is True

    assert len(network_quota_model.service.all()) == 1
    service = network_quota_model.service.single()
    assert isinstance(service, NetworkService)
    assert service.uid == network_service_model.uid


def test_multiple_linked_block_storage_services(
    block_storage_quota_model: BlockStorageQuota,
) -> None:
    item = BlockStorageService(**block_storage_service_model_dict()).save()
    block_storage_quota_model.service.connect(item)
    item = BlockStorageService(**block_storage_service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        block_storage_quota_model.service.connect(item)

    with patch("neomodel.match.QueryBuilder._count", return_value=0):
        block_storage_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            block_storage_quota_model.service.all()


def test_multiple_linked_compute_services(compute_quota_model: ComputeQuota) -> None:
    item = ComputeService(**compute_service_model_dict()).save()
    compute_quota_model.service.connect(item)
    item = ComputeService(**compute_service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        compute_quota_model.service.connect(item)

    with patch("neomodel.match.QueryBuilder._count", return_value=0):
        compute_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            compute_quota_model.service.all()


def test_multiple_linked_network_services(network_quota_model: NetworkQuota) -> None:
    item = NetworkService(**network_service_model_dict()).save()
    network_quota_model.service.connect(item)
    item = NetworkService(**network_service_model_dict()).save()
    with pytest.raises(AttemptedCardinalityViolation):
        network_quota_model.service.connect(item)

    with patch("neomodel.match.QueryBuilder._count", return_value=0):
        network_quota_model.service.connect(item)
        with pytest.raises(CardinalityViolation):
            network_quota_model.service.all()
