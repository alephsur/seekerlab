import os
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from nacl.signing import SigningKey
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from seekerlab.config import Settings
from seekerlab.db import Base
from seekerlab.modules.campaigns.domain import Conflict
from seekerlab.modules.campaigns.schemas import CampaignCreate
from seekerlab.modules.campaigns.service import CampaignService
from seekerlab.modules.identity.domain import ChallengeUnavailable, build_siws_message
from seekerlab.modules.identity.models import AuthSession, Identity, SiwsChallenge  # noqa: F401
from seekerlab.modules.identity.schemas import SiwsVerify
from seekerlab.modules.identity.service import IdentityService


BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
POSTGRES_URL = os.getenv("POSTGRES_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not POSTGRES_URL, reason="PostgreSQL test database not configured")


def base58_encode(value: bytes) -> str:
    number = int.from_bytes(value, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = BASE58_ALPHABET[remainder] + encoded
    return "1" * (len(value) - len(value.lstrip(b"\x00"))) + encoded


@pytest.fixture
def postgres_engine():
    engine = create_engine(POSTGRES_URL, pool_size=8)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_single_remaining_slot_is_claimed_once(postgres_engine):
    payload = CampaignCreate(
        title="One remaining tester slot",
        description="A campaign used to verify PostgreSQL row locking.",
        instructions=["Submit useful feedback"],
        reward_amount="1",
        capacity=1,
    )
    with Session(postgres_engine, expire_on_commit=False) as session:
        campaign = CampaignService(session).create(payload, "builder")
        campaign_id = campaign.id

    barrier = Barrier(2)

    def submit(tester_id: str) -> str:
        with Session(postgres_engine, expire_on_commit=False) as session:
            barrier.wait()
            try:
                CampaignService(session).submit(
                    campaign_id, tester_id, "Feedback from a concurrent PostgreSQL request."
                )
                return "accepted"
            except Conflict:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(submit, ["tester-a", "tester-b"]))
    assert sorted(outcomes) == ["accepted", "rejected"]


def test_siws_nonce_is_consumed_once_under_concurrency(postgres_engine):
    settings = Settings(dev_auth_enabled=False)
    with Session(postgres_engine, expire_on_commit=False) as session:
        service = IdentityService(session, settings)
        challenge_read = service.create_challenge()
        challenge = service.repo.challenge(challenge_read.nonce)
        assert challenge is not None
        signing_key = SigningKey.generate()
        address = base58_encode(bytes(signing_key.verify_key))
        message = build_siws_message(
            address=address,
            domain=challenge.domain,
            statement=challenge.statement,
            uri=challenge.uri,
            version=challenge.version,
            chain_id=challenge.chain_id,
            nonce=challenge.nonce,
            issued_at=challenge.issued_at,
            expires_at=challenge.expires_at,
        )
        payload = SiwsVerify(
            nonce=challenge.nonce,
            account={"address": address},
            signed_message=b64encode(message).decode(),
            signature=b64encode(signing_key.sign(message).signature).decode(),
            signature_type="ed25519",
        )

    barrier = Barrier(2)

    def verify() -> str:
        with Session(postgres_engine, expire_on_commit=False) as session:
            barrier.wait()
            try:
                IdentityService(session, settings).verify(payload)
                return "accepted"
            except ChallengeUnavailable:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: verify(), range(2)))
    assert sorted(outcomes) == ["accepted", "rejected"]
