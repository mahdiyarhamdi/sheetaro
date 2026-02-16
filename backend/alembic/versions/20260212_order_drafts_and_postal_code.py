"""Add order_drafts table and postal_code to users.

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-02-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add postal_code to users table
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20);
    """)

    # Create order_drafts table
    op.execute("""
        CREATE TABLE IF NOT EXISTS order_drafts (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            current_step VARCHAR(50) NOT NULL DEFAULT 'category',
            data JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_order_drafts_user_id UNIQUE (user_id)
        );
    """)

    # Index for fast lookups by user
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_order_drafts_user_id ON order_drafts(user_id);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS order_drafts;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS postal_code;")
