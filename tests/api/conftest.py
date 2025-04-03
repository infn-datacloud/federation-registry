"""File to set tests configuration parameters and common fixtures."""

import pytest
from fastapi.testclient import TestClient
from flaat.user_infos import UserInfos

from fed_reg.config import get_settings
from fed_reg.main import app
from tests.utils import random_lower_string, random_url

MOCK_ADMIN_EMAL = "admin@test.it"


@pytest.fixture
def client_without_token():
    return TestClient(app)


@pytest.fixture
def client_with_token():
    return TestClient(app, headers={"Authorization": "Bearer fake"})


@pytest.fixture
def user_infos() -> UserInfos:
    settings = get_settings()
    settings.ADMIN_EMAIL_LIST = [MOCK_ADMIN_EMAL]
    return UserInfos(
        access_token_info=None,
        user_info={
            "email": MOCK_ADMIN_EMAL,
            "iss": random_url(),
            "sub": random_lower_string(),
        },
        introspection_info=None,
    )
