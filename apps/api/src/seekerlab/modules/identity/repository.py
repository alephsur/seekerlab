from sqlalchemy import select
from sqlalchemy.orm import Session

from seekerlab.modules.identity.domain import hash_token
from seekerlab.modules.identity.models import AuthSession, Identity, SiwsChallenge


class IdentityRepository:
    def __init__(self, session: Session):
        self.session = session

    def challenge(self, nonce: str, *, lock: bool = False) -> SiwsChallenge | None:
        query = select(SiwsChallenge).where(SiwsChallenge.nonce == nonce)
        if lock:
            query = query.with_for_update()
        return self.session.scalar(query)

    def identity_for_wallet(self, wallet_address: str) -> Identity | None:
        return self.session.scalar(
            select(Identity).where(Identity.wallet_address == wallet_address)
        )

    def session_for_access_token(self, token: str, *, lock: bool = False) -> AuthSession | None:
        query = select(AuthSession).where(AuthSession.access_token_hash == hash_token(token))
        if lock:
            query = query.with_for_update()
        return self.session.scalar(query)

    def session_for_refresh_token(self, token: str, *, lock: bool = False) -> AuthSession | None:
        query = select(AuthSession).where(AuthSession.refresh_token_hash == hash_token(token))
        if lock:
            query = query.with_for_update()
        return self.session.scalar(query)
