"""Add base_price column to categories table.

Revision ID: 20260103_base_price
Revises: 20251231_dynamic
Create Date: 2026-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20260103_base_price'
down_revision: Union[str, None] = '20251231_dynamic'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add base_price column to categories table."""
    op.add_column(
        'categories',
        sa.Column('base_price', sa.Numeric(12, 0), nullable=False, server_default='0')
    )


def downgrade() -> None:
    """Remove base_price column from categories table."""
    op.drop_column('categories', 'base_price')

