"""Add printshop_profiles table for printshop-specific data.

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS printshop_profiles (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id),
            description TEXT,
            capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
            max_daily_capacity INTEGER,
            service_areas JSONB NOT NULL DEFAULT '[]'::jsonb,
            is_featured BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_printshop_profiles_user_id UNIQUE (user_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_printshop_profiles_user_id ON printshop_profiles(user_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS printshop_profiles")
