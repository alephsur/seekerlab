from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SiwsChallengeRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    domain: str
    statement: str
    uri: str
    version: Literal["1"]
    chain_id: str = Field(serialization_alias="chainId")
    nonce: str
    issued_at: str = Field(serialization_alias="issuedAt")
    expiration_time: str = Field(serialization_alias="expirationTime")


class SiwsAccount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    address: str = Field(min_length=32, max_length=44)


class SiwsVerify(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    nonce: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9]+$")
    account: SiwsAccount
    signed_message: str = Field(alias="signedMessage", max_length=4096)
    signature: str = Field(max_length=256)
    signature_type: Literal["ed25519"] | None = Field(default=None, alias="signatureType")


class SessionRefresh(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    refresh_token: str = Field(alias="refreshToken", min_length=32, max_length=256)


class IdentityRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    wallet_address: str = Field(serialization_alias="walletAddress")
    role: Literal["tester"]


class SessionRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(serialization_alias="accessToken")
    refresh_token: str = Field(serialization_alias="refreshToken")
    token_type: Literal["bearer"] = Field(default="bearer", serialization_alias="tokenType")
    expires_in: int = Field(serialization_alias="expiresIn")
    refresh_expires_in: int = Field(serialization_alias="refreshExpiresIn")
    identity: IdentityRead


class CurrentIdentityRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    wallet_address: str = Field(serialization_alias="walletAddress")
    role: Literal["tester"]
