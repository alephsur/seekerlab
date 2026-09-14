from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from seekerlab.config import Settings, get_settings
from seekerlab.db import get_session
from seekerlab.modules.identity.dependencies import Principal, require_wallet_session
from seekerlab.modules.identity.models import AuthSession
from seekerlab.modules.identity.schemas import (
    CurrentIdentityRead,
    SessionRead,
    SessionRefresh,
    SiwsChallengeRead,
    SiwsVerify,
)
from seekerlab.modules.identity.service import IdentityService

router = APIRouter(prefix="/api/v1/auth", tags=["identity"])
Db = Annotated[Session, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]
WalletPrincipal = Annotated[Principal, Depends(require_wallet_session)]


@router.post("/siws/challenge", response_model=SiwsChallengeRead, status_code=201)
def create_siws_challenge(session: Db, settings: AppSettings):
    return IdentityService(session, settings).create_challenge()


@router.post("/siws/verify", response_model=SessionRead)
def verify_siws(data: SiwsVerify, session: Db, settings: AppSettings):
    return IdentityService(session, settings).verify(data)


@router.post("/session/refresh", response_model=SessionRead)
def refresh_session(data: SessionRefresh, session: Db, settings: AppSettings):
    return IdentityService(session, settings).refresh(data.refresh_token)


@router.post("/session/revoke", status_code=204)
def revoke_session(principal: WalletPrincipal, session: Db, settings: AppSettings):
    auth_session = session.scalar(
        select(AuthSession).where(AuthSession.id == UUID(principal.session_id))
    )
    if auth_session is not None:
        IdentityService(session, settings).revoke(auth_session)
    return Response(status_code=204)


@router.get("/me", response_model=CurrentIdentityRead)
def current_identity(principal: WalletPrincipal):
    return CurrentIdentityRead(
        id=UUID(principal.id),
        wallet_address=principal.wallet_address,
        role="tester",
    )
