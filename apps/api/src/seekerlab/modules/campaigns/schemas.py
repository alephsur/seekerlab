from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from seekerlab.modules.campaigns.domain import CampaignStatus, Currency

Instruction = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]


class CampaignCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=20, max_length=4000)
    instructions: list[Instruction] = Field(min_length=1, max_length=10)
    reward_amount: Decimal = Field(gt=0, le=100000, max_digits=18, decimal_places=6)
    currency: Currency = Currency.USDC
    estimated_minutes: int = Field(default=5, ge=1, le=120)
    capacity: int = Field(default=20, ge=1, le=10000)


class CampaignRead(CampaignCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: CampaignStatus
    submitted_count: int
    created_at: datetime


class SubmissionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    feedback: str = Field(min_length=20, max_length=5000)


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    campaign_id: UUID
    feedback: str
    status: str
    created_at: datetime
