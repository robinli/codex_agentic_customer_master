"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("customer_code", sa.String(length=50), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=20), nullable=True),
        sa.Column("customer_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("payment_terms", sa.String(length=100), nullable=True),
        sa.Column("credit_limit", sa.Numeric(12, 2), nullable=True),
        sa.Column("sales_owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("customer_code", name="uq_customers_customer_code"),
        sa.UniqueConstraint("tax_id", name="uq_customers_tax_id"),
    )
    op.create_index("ix_customers_customer_name", "customers", ["customer_name"])
    op.create_index("ix_customers_tax_id", "customers", ["tax_id"])
    op.create_table(
        "customer_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("mobile", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "customer_addresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("address_type", sa.String(length=32), nullable=False),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("city", sa.String(length=50), nullable=True),
        sa.Column("district", sa.String(length=50), nullable=True),
        sa.Column("address_line", sa.Text(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "approval_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("before_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("before_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_table(
        "agent_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "agent_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_name", sa.String(length=64), nullable=True),
        sa.Column("tool_args", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tool_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("agent_messages")
    op.drop_table("agent_sessions")
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("approval_requests")
    op.drop_table("customer_addresses")
    op.drop_table("customer_contacts")
    op.drop_index("ix_customers_tax_id", table_name="customers")
    op.drop_index("ix_customers_customer_name", table_name="customers")
    op.drop_table("customers")

