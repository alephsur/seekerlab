"""SIWS challenges, wallet identities, and renewable sessions."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "identities",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("wallet_address", sa.String(44), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('tester')", name="valid_identity_role"),
        sa.UniqueConstraint("wallet_address"),
    )
    op.create_table(
        "siws_challenges",
        sa.Column("nonce", sa.String(64), primary_key=True),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("uri", sa.String(512), nullable=False),
        sa.Column("statement", sa.String(255), nullable=False),
        sa.Column("version", sa.String(8), nullable=False),
        sa.Column("chain_id", sa.String(32), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_siws_challenges_expires_at", "siws_challenges", ["expires_at"])
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("identity_id", sa.Uuid(), sa.ForeignKey("identities.id"), nullable=False),
        sa.Column("access_token_hash", sa.String(64), nullable=False),
        sa.Column("refresh_token_hash", sa.String(64), nullable=False),
        sa.Column("access_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refresh_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("access_token_hash"),
        sa.UniqueConstraint("refresh_token_hash"),
    )
    op.create_index("ix_auth_sessions_identity_id", "auth_sessions", ["identity_id"])
    op.create_index("ix_auth_sessions_access_expires_at", "auth_sessions", ["access_expires_at"])
    op.create_index("ix_auth_sessions_refresh_expires_at", "auth_sessions", ["refresh_expires_at"])


def downgrade() -> None:
    op.drop_table("auth_sessions")
    op.drop_table("siws_challenges")
    op.drop_table("identities")
