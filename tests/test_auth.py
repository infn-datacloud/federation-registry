"""Test custom  authentication functions."""

from flaat.user_infos import UserInfos
from pytest_cases import case, parametrize_with_cases

from fed_reg.auth import has_write_access
from fed_reg.main import settings
from tests.utils import random_email

MOCK_WRITE_EMAIL = "admin@test.it"


class CaseUserInfo:
    @case(tags="write")
    def case_user_infos_with_write_email(self) -> UserInfos:
        """Fake user with email. It has write access rights."""
        return UserInfos(
            access_token_info=None,
            user_info={"email": MOCK_WRITE_EMAIL},
            introspection_info=None,
        )

    @case(tags="read")
    def case_user_infos_with_read_email(self) -> UserInfos:
        """Fake user with email. It has only read access rights."""
        return UserInfos(
            access_token_info=None,
            user_info={"email": random_email()},
            introspection_info=None,
        )

    @case(tags="read")
    def case_user_infos_without_email(self) -> UserInfos:
        """Fake user without email."""
        return UserInfos(access_token_info=None, user_info={}, introspection_info=None)


@parametrize_with_cases("user_infos", cases=CaseUserInfo, has_tag="write")
def test_check_write_access(user_infos: UserInfos) -> None:
    """Test user has write access rights."""
    settings.ADMIN_EMAIL_LIST = [MOCK_WRITE_EMAIL]
    assert has_write_access(user_infos)


@parametrize_with_cases("user_infos", cases=CaseUserInfo, has_tag="read")
def test_check_not_write_access(user_infos: UserInfos) -> None:
    """Test user has no write access rights."""
    settings.ADMIN_EMAIL_LIST = [MOCK_WRITE_EMAIL]
    assert not has_write_access(user_infos)


# TODO: test get_user_info
