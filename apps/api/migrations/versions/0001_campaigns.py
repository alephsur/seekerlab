"""Campaigns and submissions. No wallets, deposits or payments in this revision."""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("campaigns",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.String(128), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("instructions", sa.JSON(), nullable=False),
        sa.Column("reward_amount", sa.Numeric(18, 6), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("submitted_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("reward_amount > 0", name="positive_reward"),
        sa.CheckConstraint("capacity > 0", name="positive_capacity"),
        sa.CheckConstraint("submitted_count >= 0 AND submitted_count <= capacity", name="valid_count"),
        sa.CheckConstraint("currency IN ('USDC', 'SKR')", name="valid_currency"),
        sa.CheckConstraint("status IN ('open', 'closed')", name="valid_campaign_status"),
    )
    op.create_index("ix_campaigns_owner_id", "campaigns", ["owner_id"])
    op.create_table("submissions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("campaign_id", sa.Uuid(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("tester_id", sa.String(128), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("campaign_id", "tester_id", name="uq_campaign_tester"),
    )
    op.create_index("ix_submissions_campaign_id", "submissions", ["campaign_id"])
    op.create_index("ix_submissions_tester_id", "submissions", ["tester_id"])


def downgrade() -> None:
    op.drop_table("submissions")
    op.drop_table("campaigns")
