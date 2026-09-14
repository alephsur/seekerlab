from dataclasses import dataclass
from secrets import compare_digest
from typing import Annotated, Literal

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from seekerlab.config import Settings, get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    id: str
    role: Literal["builder", "tester"]


def current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Principal:
    if not settings.dev_auth_enabled:
        raise HTTPException(503, "SIWS is not implemented yet; development authentication is disabled")
    if credentials is None:
        raise HTTPException(401, "Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    token = credentials.credentials
    if not token.isascii():
        raise HTTPException(401, "Invalid token")
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
