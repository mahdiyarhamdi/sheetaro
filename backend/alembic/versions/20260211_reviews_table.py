"""Add reviews table for customer order reviews and ratings.

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reviews table (idempotent)
    op.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id UUID PRIMARY KEY,
            order_id UUID NOT NULL REFERENCES orders(id),
            user_id UUID NOT NULL REFERENCES users(id),
            printshop_id UUID NOT NULL REFERENCES users(id),
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            is_approved BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT uq_reviews_order_id UNIQUE (order_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_order_id ON reviews(order_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_user_id ON reviews(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reviews_printshop_id ON reviews(printshop_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS reviews")
