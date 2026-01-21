"""Add web authentication fields to users table.

Revision ID: 20260121_web_auth
Revises: 20260104_indexes
Create Date: 2026-01-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260121_web_auth'
down_revision: Union[str, None] = '20260104_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make telegram_id nullable for web-only users
    op.alter_column(
        'users',
        'telegram_id',
        existing_type=sa.BigInteger(),
        nullable=True,
    )
    
    # Add web authentication fields
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(255), nullable=True)
    )
    op.add_column(
        'users',
        sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'users',
        sa.Column('web_linked', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'users',
        sa.Column('full_name', sa.String(511), nullable=True)
    )
    
    # Create unique index on phone_number for web login
    op.create_index(
        'ix_users_phone_number_unique',
        'users',
        ['phone_number'],
        unique=True,
        postgresql_where=sa.text('phone_number IS NOT NULL')
    )
    
    # Update existing users to have full_name populated
    op.execute("""
        UPDATE users 
        SET full_name = CONCAT(first_name, ' ', COALESCE(last_name, ''))
        WHERE full_name IS NULL
    """)


def downgrade() -> None:
    # Remove new columns
    op.drop_index('ix_users_phone_number_unique', table_name='users')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'web_linked')
    op.drop_column('users', 'phone_verified')
    op.drop_column('users', 'password_hash')
    
    # Make telegram_id not nullable again
    op.alter_column(
        'users',
        'telegram_id',
        existing_type=sa.BigInteger(),
        nullable=False,
    )

