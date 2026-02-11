"""Add PRINTED order status and settlements table for print shop panel.

Revision ID: a1b2c3d4e5f6
Revises: add_full_payment_type
Create Date: 2026-02-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'add_full_payment_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add PRINTED to orderstatus enum (idempotent)
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PRINTED' AFTER 'PRINTING'")

    # Create settlementstatus enum (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE settlementstatus AS ENUM ('PENDING', 'PAID');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Create settlements table (idempotent)
    op.execute("""
        CREATE TABLE IF NOT EXISTS settlements (
            id UUID PRIMARY KEY,
            printshop_id UUID NOT NULL REFERENCES users(id),
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            total_orders INTEGER NOT NULL DEFAULT 0,
            total_revenue NUMERIC(12, 0) NOT NULL DEFAULT 0,
            platform_commission NUMERIC(12, 0) NOT NULL DEFAULT 0,
            net_amount NUMERIC(12, 0) NOT NULL DEFAULT 0,
            status settlementstatus NOT NULL DEFAULT 'PENDING',
            paid_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_settlements_printshop_id ON settlements(printshop_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS settlements")
    op.execute("DROP TYPE IF EXISTS settlementstatus")
    # Note: Cannot remove enum value from PostgreSQL in downgrade
