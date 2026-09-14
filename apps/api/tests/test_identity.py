from base64 import b64encode
from datetime import UTC, datetime, timedelta

import pytest
from nacl.signing import SigningKey
from pydantic import ValidationError

from seekerlab.config import Settings


BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_encode(value: bytes) -> str:
    number = int.from_bytes(value, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = BASE58_ALPHABET[remainder] + encoded
    leading_zeroes = len(value) - len(value.lstrip(b"\x00"))
    return "1" * leading_zeroes + encoded


def message_for(challenge: dict, address: str) -> bytes:
    return (
        f"{challenge['domain']} wants you to sign in with your Solana account:\n"
        f"{address}\n\n"
        f"{challenge['statement']}\n\n"
        f"URI: {challenge['uri']}\n"
        f"Version: {challenge['version']}\n"
        f"Chain ID: {challenge['chainId']}\n"
        f"Nonce: {challenge['nonce']}\n"
        f"Issued At: {challenge['issuedAt']}\n"
        f"Expiration Time: {challenge['expirationTime']}"
    ).encode()


def sign_in_payload(challenge: dict, signing_key: SigningKey) -> dict:
    address = base58_encode(bytes(signing_key.verify_key))
    message = message_for(challenge, address)
    return {
        "nonce": challenge["nonce"],
        "account": {"address": address},
        "signedMessage": b64encode(message).decode(),
        "signature": b64encode(signing_key.sign(message).signature).decode(),
        "signatureType": "ed25519",
    }


def authenticate(client, signing_key: SigningKey | None = None):
    signing_key = signing_key or SigningKey.generate()
    challenge_response = client.post("/api/v1/auth/siws/challenge")
    assert challenge_response.status_code == 201
    challenge = challenge_response.json()
    response = client.post(
        "/api/v1/auth/siws/verify", json=sign_in_payload(challenge, signing_key)
    )
    assert response.status_code == 200
    return challenge, response.json(), signing_key


def test_siws_session_authenticates_tester_requests(client, builder_headers, campaign_payload):
    challenge, session, signing_key = authenticate(client)
    assert challenge["version"] == "1"
    assert challenge["chainId"] == "solana:devnet"
    assert session["identity"]["walletAddress"] == base58_encode(bytes(signing_key.verify_key))
    headers = {"Authorization": f"Bearer {session['accessToken']}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    campaign = client.post(
        "/api/v1/campaigns", json=campaign_payload, headers=builder_headers
    ).json()
    response = client.post(
        f"/api/v1/campaigns/{campaign['id']}/submissions",
        json={"feedback": "This feedback was submitted through a verified wallet session."},
        headers=headers,
    )
    assert response.status_code == 201


def test_challenge_cannot_be_reused(client):
    challenge = client.post("/api/v1/auth/siws/challenge").json()
    payload = sign_in_payload(challenge, SigningKey.generate())
    assert client.post("/api/v1/auth/siws/verify", json=payload).status_code == 200
    assert client.post("/api/v1/auth/siws/verify", json=payload).status_code == 409


def test_invalid_signature_does_not_consume_challenge(client):
    challenge = client.post("/api/v1/auth/siws/challenge").json()
    correct_key = SigningKey.generate()
    payload = sign_in_payload(challenge, correct_key)
    other_key = SigningKey.generate()
    message = message_for(challenge, payload["account"]["address"])
    payload["signature"] = b64encode(other_key.sign(message).signature).decode()
    assert client.post("/api/v1/auth/siws/verify", json=payload).status_code == 401
    assert client.post(
        "/api/v1/auth/siws/verify", json=sign_in_payload(challenge, correct_key)
    ).status_code == 200


def test_signed_message_is_bound_to_configured_domain(client):
    challenge = client.post("/api/v1/auth/siws/challenge").json()
    signing_key = SigningKey.generate()
    payload = sign_in_payload(challenge, signing_key)
    forged = {**challenge, "domain": "attacker.example"}
    message = message_for(forged, payload["account"]["address"])
    payload["signedMessage"] = b64encode(message).decode()
    payload["signature"] = b64encode(signing_key.sign(message).signature).decode()
    assert client.post("/api/v1/auth/siws/verify", json=payload).status_code == 401


def test_expired_challenge_is_rejected(client, monkeypatch):
    challenge = client.post("/api/v1/auth/siws/challenge").json()
    future = datetime.now(UTC) + timedelta(hours=1)
    monkeypatch.setattr("seekerlab.modules.identity.service.utc_now", lambda: future)
    response = client.post(
        "/api/v1/auth/siws/verify",
        json=sign_in_payload(challenge, SigningKey.generate()),
    )
    assert response.status_code == 409


def test_refresh_rotates_tokens_and_revoke_ends_session(client):
    _, first, _ = authenticate(client)
    refreshed_response = client.post(
        "/api/v1/auth/session/refresh", json={"refreshToken": first["refreshToken"]}
    )
    assert refreshed_response.status_code == 200
    refreshed = refreshed_response.json()
    assert refreshed["accessToken"] != first["accessToken"]
    assert refreshed["refreshToken"] != first["refreshToken"]
    assert client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {first['accessToken']}"},
    ).status_code == 401
    assert client.post(
        "/api/v1/auth/session/refresh", json={"refreshToken": first["refreshToken"]}
    ).status_code == 401

    headers = {"Authorization": f"Bearer {refreshed['accessToken']}"}
    assert client.post("/api/v1/auth/session/revoke", headers=headers).status_code == 204
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_different_wallets_receive_distinct_identities(client):
    _, first, _ = authenticate(client, SigningKey.generate())
    _, second, _ = authenticate(client, SigningKey.generate())
    assert first["identity"]["id"] != second["identity"]["id"]
    assert first["identity"]["walletAddress"] != second["identity"]["walletAddress"]


def test_siws_configuration_requires_matching_safe_authority():
    with pytest.raises(ValidationError):
        Settings(siws_domain="app.example", siws_uri="https://other.example")
    with pytest.raises(ValidationError):
        Settings(siws_domain="app.example", siws_uri="https://user@app.example")
    with pytest.raises(ValidationError):
        Settings(siws_statement="Sign in\nApprove something else")
