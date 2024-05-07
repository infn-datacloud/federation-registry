"""Authentication and authorization rules."""
from fastapi.security import HTTPBearer
from flaat import AuthWorkflow
from flaat.config import AccessLevel
from flaat.fastapi import Flaat
from flaat.requirements import AllOf, HasSubIss, IsTrue
from flaat.user_infos import UserInfos

from fed_reg.config import get_settings

security = HTTPBearer()
lazy_security = HTTPBearer(auto_error=False)


def has_write_access(user_infos: UserInfos) -> bool:
    """Target user has write access on Federation-Registry."""
    settings = get_settings()
    return user_infos.user_info.get("email") in settings.ADMIN_EMAIL_LIST


flaat = Flaat()
flaat.set_access_levels(
    [AccessLevel("write", AllOf(HasSubIss(), IsTrue(has_write_access)))]
)
flaat.set_trusted_OP_list(get_settings().TRUSTED_IDP_LIST)
flaat.set_request_timeout(30)


custom = AuthWorkflow(flaat=flaat, ignore_no_authn=True)
