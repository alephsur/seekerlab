from base64 import b64decode
from binascii import Error as Base64Error
from datetime import UTC, datetime
from hashlib import sha256

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58_VALUES = {character: index for index, character in enumerate(BASE58_ALPHABET)}


class IdentityError(Exception):
    pass


class InvalidSignIn(IdentityError):
    pass


class ChallengeUnavailable(IdentityError):
    pass


class InvalidSession(IdentityError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def format_siws_time(value: datetime) -> str:
    return as_utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_siws_message(
    *, address: str, domain: str, statement: str, uri: str, version: str,
    chain_id: str, nonce: str, issued_at: datetime, expires_at: datetime,
) -> bytes:
    return (
        f"{domain} wants you to sign in with your Solana account:\n"
        f"{address}\n\n"
        f"{statement}\n\n"
        f"URI: {uri}\n"
        f"Version: {version}\n"
        f"Chain ID: {chain_id}\n"
        f"Nonce: {nonce}\n"
        f"Issued At: {format_siws_time(issued_at)}\n"
        f"Expiration Time: {format_siws_time(expires_at)}"
    ).encode("utf-8")


def decode_base58(value: str) -> bytes:
    number = 0
    try:
        for character in value:
            number = number * 58 + BASE58_VALUES[character]
    except KeyError as exc:
        raise InvalidSignIn("Invalid Solana address") from exc
    decoded = number.to_bytes((number.bit_length() + 7) // 8, "big") if number else b""
    return b"\x00" * (len(value) - len(value.lstrip("1"))) + decoded


def decode_base64(value: str, field: str) -> bytes:
    try:
        return b64decode(value, validate=True)
    except (Base64Error, ValueError) as exc:
        raise InvalidSignIn(f"Invalid {field} encoding") from exc


def verify_siws_signature(*, address: str, signed_message: str, signature: str,
                          expected_message: bytes) -> None:
    public_key = decode_base58(address)
    if len(public_key) != 32:
        raise InvalidSignIn("Invalid Solana address")
    message_bytes = decode_base64(signed_message, "signed message")
    signature_bytes = decode_base64(signature, "signature")
    if message_bytes != expected_message:
        raise InvalidSignIn("The signed message does not match the issued challenge")
    if len(signature_bytes) != 64:
        raise InvalidSignIn("Invalid Ed25519 signature")
    try:
        VerifyKey(public_key).verify(message_bytes, signature_bytes)
    except (BadSignatureError, ValueError) as exc:
        raise InvalidSignIn("Invalid Ed25519 signature") from exc


def hash_token(token: str) -> str:
    return sha256(token.encode("ascii")).hexdigest()
