"""Authentication and authorization rules."""

from typing import Annotated

from fastapi import HTTPException, Request, Security, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasicCredentials,
    HTTPBearer,
)
from flaat import AuthWorkflow
from flaat.config import AccessLevel
from flaat.exceptions import FlaatForbidden, FlaatUnauthenticated
from flaat.fastapi import Flaat
from flaat.requirements import AllOf, HasSubIss, IsTrue
from flaat.user_infos import UserInfos

from fed_reg.config import get_settings

security = HTTPBearer()
lazy_security = HTTPBearer(auto_error=False)


def has_write_access(user_infos: UserInfos) -> bool:
    """Target user has write access on Federation-Registry."""
    settings = get_settings()
    email = user_infos.user_info.get("email", None)
    if email is not None:
        return email in settings.ADMIN_EMAIL_LIST
    return False


flaat = Flaat()
flaat.set_access_levels(
    [AccessLevel("write", AllOf(HasSubIss(), IsTrue(has_write_access)))]
)
flaat.set_trusted_OP_list(get_settings().TRUSTED_IDP_LIST)
flaat.set_request_timeout(30)


custom = AuthWorkflow(flaat=flaat, ignore_no_authn=True)


def get_user_infos(
    request: Request,
    client_credentials: HTTPAuthorizationCredentials = Security(lazy_security),
) -> UserInfos | None:
    """Return user infos credentials."""
    if client_credentials:
        try:
            return flaat.get_user_infos_from_request(request)
        except FlaatUnauthenticated as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.render()) from e
    return None


def strict_security(
    request: Request,
    client_credentials: Annotated[HTTPBasicCredentials, Security(security)],
):
    """Check security"""
    user_infos = flaat.get_user_infos_from_request(request)
    if user_infos is None:
        msg = "Invalid token. Empty user infos"
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=msg)

    auth_workflow = AuthWorkflow(flaat, flaat._get_access_level_requirement("write"))
    try:
        auth_workflow.check_user_authorization(user_infos=user_infos)
    except FlaatForbidden as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=e.render()) from e
