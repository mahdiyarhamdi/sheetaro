"""Add price_type to category_attributes table

Revision ID: add_price_type
Revises: 809d2121d5dc
Create Date: 2026-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_price_type'
down_revision: Union[str, None] = '809d2121d5dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type for attribute price type
    attributepricetype = postgresql.ENUM('FIXED', 'MULTIPLIER', name='attributepricetype', create_type=False)
    attributepricetype.create(op.get_bind(), checkfirst=True)
    
    # Add price_type column to category_attributes table with default FIXED
    op.add_column(
        'category_attributes',
        sa.Column(
            'price_type',
            attributepricetype,
            nullable=False,
            server_default='FIXED'
        )
    )


def downgrade() -> None:
    # Remove the price_type column
    op.drop_column('category_attributes', 'price_type')
    
    # Drop the ENUM type
    op.execute("DROP TYPE IF EXISTS attributepricetype")
