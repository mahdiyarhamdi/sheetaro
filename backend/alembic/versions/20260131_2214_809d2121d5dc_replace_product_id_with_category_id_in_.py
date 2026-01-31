"""Replace product_id with category_id in orders

Revision ID: 809d2121d5dc
Revises: fix_text_align_col
Create Date: 2026-01-31 22:14:37.761746

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '809d2121d5dc'
down_revision = 'fix_text_align_col'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to orders table
    op.add_column('orders', sa.Column('category_id', sa.UUID(), nullable=True))  # Temporarily nullable
    op.add_column('orders', sa.Column('selected_attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'))
    op.add_column('orders', sa.Column('base_price', sa.Numeric(precision=12, scale=0), nullable=False, server_default='0'))
    op.add_column('orders', sa.Column('attributes_price', sa.Numeric(precision=12, scale=0), nullable=False, server_default='0'))
    
    # Create index on category_id
    op.create_index(op.f('ix_orders_category_id'), 'orders', ['category_id'], unique=False)
    
    # Add foreign key constraint for category_id
    op.create_foreign_key('orders_category_id_fkey', 'orders', 'categories', ['category_id'], ['id'])
    
    # Note: product_id column is kept for now to preserve existing data
    # It can be dropped in a future migration after data migration is complete
    # op.drop_constraint('orders_product_id_fkey', 'orders', type_='foreignkey')
    # op.drop_index('ix_orders_product_id', table_name='orders')
    # op.drop_column('orders', 'product_id')


def downgrade() -> None:
    # Remove the new columns and constraints
    op.drop_constraint('orders_category_id_fkey', 'orders', type_='foreignkey')
    op.drop_index(op.f('ix_orders_category_id'), table_name='orders')
    op.drop_column('orders', 'attributes_price')
    op.drop_column('orders', 'base_price')
    op.drop_column('orders', 'selected_attributes')
    op.drop_column('orders', 'category_id')
