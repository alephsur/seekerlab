from dataclasses import dataclass
from secrets import compare_digest
from typing import Annotated, Literal

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from seekerlab.config import Settings, get_settings
from seekerlab.db import get_session
from seekerlab.modules.identity.domain import InvalidSession
from seekerlab.modules.identity.service import IdentityService

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    id: str
    role: Literal["builder", "tester"]
    wallet_address: str | None = None
    session_id: str | None = None


def current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_session)],
) -> Principal:
    if credentials is None:
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    token = credentials.credentials
    if not token.isascii():
        raise HTTPException(401, "Invalid token")
    try:
        auth_session = IdentityService(session, settings).authenticate_access_token(token)
        return Principal(
            str(auth_session.identity.id),
            "tester",
            wallet_address=auth_session.identity.wallet_address,
            session_id=str(auth_session.id),
        )
    except InvalidSession:
        pass
    if settings.dev_auth_enabled:
        if compare_digest(token, settings.dev_builder_token):
            return Principal("local-builder", "builder")
        if compare_digest(token, settings.dev_tester_token):
            return Principal("local-tester", "tester")
    raise HTTPException(401, "Invalid token", headers={"WWW-Authenticate": "Bearer"})


def require_builder(principal: Annotated[Principal, Depends(current_principal)]) -> Principal:
    if principal.role != "builder":
        raise HTTPException(403, "Builder role required")
    return principal


def require_tester(principal: Annotated[Principal, Depends(current_principal)]) -> Principal:
    if principal.role != "tester":
        raise HTTPException(403, "Tester role required")
    return principal


def require_wallet_session(
    principal: Annotated[Principal, Depends(current_principal)],
) -> Principal:
    if principal.session_id is None or principal.wallet_address is None:
        raise HTTPException(403, "A wallet session is required")
    return principal
