from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from seekerlab.db import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    __table_args__ = (
        CheckConstraint("reward_amount > 0", name="positive_reward"),
        CheckConstraint("capacity > 0", name="positive_capacity"),
        CheckConstraint("submitted_count >= 0 AND submitted_count <= capacity", name="valid_count"),
        CheckConstraint("currency IN ('USDC', 'SKR')", name="valid_currency"),
        CheckConstraint("status IN ('open', 'closed')", name="valid_campaign_status"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    instructions: Mapped[list[str]] = mapped_column(JSON)
    reward_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    currency: Mapped[str] = mapped_column(String(8), default="USDC")
    estimated_minutes: Mapped[int] = mapped_column(default=5)
    capacity: Mapped[int] = mapped_column(default=20)
    submitted_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(16), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("campaign_id", "tester_id", name="uq_campaign_tester"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    tester_id: Mapped[str] = mapped_column(String(128), index=True)
    feedback: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="pending_review")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
