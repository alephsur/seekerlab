from datetime import datetime, timedelta
from secrets import token_hex, token_urlsafe

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from seekerlab.config import Settings
from seekerlab.modules.identity.domain import (
    ChallengeUnavailable,
    InvalidSession,
    as_utc,
    build_siws_message,
    format_siws_time,
    hash_token,
    utc_now,
    verify_siws_signature,
)
from seekerlab.modules.identity.models import AuthSession, Identity, SiwsChallenge
from seekerlab.modules.identity.repository import IdentityRepository
from seekerlab.modules.identity.schemas import IdentityRead, SessionRead, SiwsChallengeRead, SiwsVerify


class IdentityService:
    def __init__(self, session: Session, settings: Settings):
        self.session = session
        self.settings = settings
        self.repo = IdentityRepository(session)

    def create_challenge(self) -> SiwsChallengeRead:
        issued_at = utc_now().replace(microsecond=0)
        expires_at = issued_at + timedelta(seconds=self.settings.siws_challenge_ttl_seconds)
        challenge = SiwsChallenge(
            nonce=token_hex(24),
            domain=self.settings.siws_domain,
            uri=self.settings.siws_uri,
            statement=self.settings.siws_statement,
            version="1",
            chain_id=self.settings.siws_chain_id,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        self.session.add(challenge)
        self.session.commit()
        return self._challenge_read(challenge)

    def verify(self, data: SiwsVerify) -> SessionRead:
        now = utc_now()
        challenge = self.repo.challenge(data.nonce, lock=True)
        if challenge is None or challenge.consumed_at is not None:
            raise ChallengeUnavailable("Challenge not found or already used")
        if as_utc(challenge.expires_at) <= now:
            raise ChallengeUnavailable("Challenge expired")
        expected_message = build_siws_message(
            address=data.account.address,
            domain=challenge.domain,
            statement=challenge.statement,
            uri=challenge.uri,
            version=challenge.version,
            chain_id=challenge.chain_id,
            nonce=challenge.nonce,
            issued_at=challenge.issued_at,
            expires_at=challenge.expires_at,
        )
        verify_siws_signature(
            address=data.account.address,
            signed_message=data.signed_message,
            signature=data.signature,
            expected_message=expected_message,
        )
        identity = self._get_or_create_identity(data.account.address)
        challenge.consumed_at = now
        access_token, refresh_token, auth_session = self._new_session(identity, now)
        self.session.add(auth_session)
        self.session.commit()
        return self._session_read(access_token, refresh_token, auth_session)

    def authenticate_access_token(self, token: str) -> AuthSession:
        auth_session = self.repo.session_for_access_token(token)
        now = utc_now()
        if (
            auth_session is None
            or auth_session.revoked_at is not None
            or as_utc(auth_session.access_expires_at) <= now
        ):
            raise InvalidSession("Invalid or expired session")
        return auth_session

    def refresh(self, refresh_token: str) -> SessionRead:
        now = utc_now()
        auth_session = self.repo.session_for_refresh_token(refresh_token, lock=True)
        if (
            auth_session is None
            or auth_session.revoked_at is not None
            or as_utc(auth_session.refresh_expires_at) <= now
        ):
            raise InvalidSession("Invalid or expired refresh token")
        access_token = self._token("access")
        new_refresh_token = self._token("refresh")
        auth_session.access_token_hash = hash_token(access_token)
        auth_session.refresh_token_hash = hash_token(new_refresh_token)
        auth_session.access_expires_at = now + timedelta(
            seconds=self.settings.session_access_ttl_seconds
        )
        auth_session.refresh_expires_at = now + timedelta(
            seconds=self.settings.session_refresh_ttl_seconds
        )
        auth_session.updated_at = now
        self.session.commit()
        return self._session_read(access_token, new_refresh_token, auth_session)

    def revoke(self, auth_session: AuthSession) -> None:
        if auth_session.revoked_at is None:
            auth_session.revoked_at = utc_now()
            auth_session.updated_at = auth_session.revoked_at
            self.session.commit()

    def _get_or_create_identity(self, wallet_address: str) -> Identity:
        identity = self.repo.identity_for_wallet(wallet_address)
        if identity is not None:
            return identity
        identity = Identity(wallet_address=wallet_address, role="tester")
        try:
            with self.session.begin_nested():
                self.session.add(identity)
                self.session.flush()
            return identity
        except IntegrityError:
            existing = self.repo.identity_for_wallet(wallet_address)
            if existing is None:
                raise
            return existing

    def _new_session(self, identity: Identity, now: datetime):
        access_token = self._token("access")
        refresh_token = self._token("refresh")
        auth_session = AuthSession(
            identity=identity,
            access_token_hash=hash_token(access_token),
            refresh_token_hash=hash_token(refresh_token),
            access_expires_at=now + timedelta(seconds=self.settings.session_access_ttl_seconds),
            refresh_expires_at=now + timedelta(seconds=self.settings.session_refresh_ttl_seconds),
            updated_at=now,
        )
        return access_token, refresh_token, auth_session

    def _session_read(self, access_token: str, refresh_token: str,
                      auth_session: AuthSession) -> SessionRead:
        return SessionRead(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.settings.session_access_ttl_seconds,
            refresh_expires_in=self.settings.session_refresh_ttl_seconds,
            identity=IdentityRead(
                id=auth_session.identity.id,
                wallet_address=auth_session.identity.wallet_address,
                role="tester",
            ),
        )

    @staticmethod
    def _token(kind: str) -> str:
        return f"sl_{kind}_{token_urlsafe(32)}"

    @staticmethod
    def _challenge_read(challenge: SiwsChallenge) -> SiwsChallengeRead:
        return SiwsChallengeRead(
            domain=challenge.domain,
            statement=challenge.statement,
            uri=challenge.uri,
            version="1",
            chain_id=challenge.chain_id,
            nonce=challenge.nonce,
            issued_at=format_siws_time(challenge.issued_at),
            expiration_time=format_siws_time(challenge.expires_at),
        )
