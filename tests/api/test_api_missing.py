import os
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from flaat.user_infos import UserInfos
from pytest_cases import case, parametrize, parametrize_with_cases

from fed_reg.main import settings


class CaseEndpoint:
    @parametrize(
        endpoint=(
            "flavors",
            "identity_providers",
            "images",
            "locations",
            "networks",
            "projects",
            "block_storage_quotas",
            "compute_quotas",
            "network_quotas",
            "object_store_quotas",
            "regions",
            "block_storage_services",
            "compute_services",
            "identity_services",
            "network_services",
            "object_store_services",
            "slas",
            "user_groups",
        )
    )
    def case_endpoint(self, endpoint: str) -> str:
        return endpoint

    @case(tags="provider")
    def case_provider(self) -> str:
        return "providers"


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint", cases=CaseEndpoint)
def test_get_missing(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint", cases=CaseEndpoint)
def test_get_multi_missing(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint)
    resp = client_with_token.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 0


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint", cases=CaseEndpoint)
def test_delete_missing(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint", cases=CaseEndpoint)
def test_patch_missing(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.patch(url, json={})
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@patch("fed_reg.auth.flaat.get_user_infos_from_request")
@parametrize_with_cases("endpoint", cases=CaseEndpoint, has_tag="provider")
def test_put_missing(
    mock_user_infos: MagicMock,
    client_with_token: TestClient,
    user_infos: UserInfos,
    endpoint: str,
) -> None:
    mock_user_infos.return_value = user_infos
    url = os.path.join(settings.API_V1_STR, endpoint, str(uuid4()))
    resp = client_with_token.put(url, json={})
    assert resp.status_code == status.HTTP_404_NOT_FOUND
