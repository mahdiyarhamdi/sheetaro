"""Add performance indexes for query optimization

Revision ID: 20260104_indexes
Revises: 20260103_enhanced_qt
Create Date: 2026-01-04

This migration adds composite indexes for frequently used queries:
- orders: status + created_at (for filtering and sorting)
- payments: status + created_at (for admin dashboard)
- validation_reports: order_id + created_at (for history)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260104_indexes'
down_revision: Union[str, None] = '20260103_enhanced_qt'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite indexes for better query performance."""
    
    # Orders: frequently queried by status and sorted by created_at
    # Used in: list user orders, printshop queue, admin dashboard
    op.create_index(
        'ix_orders_status_created_at',
        'orders',
        ['status', 'created_at'],
        unique=False
    )
    
    # Orders: user's orders sorted by date
    op.create_index(
        'ix_orders_user_id_created_at',
        'orders',
        ['user_id', 'created_at'],
        unique=False
    )
    
    # Payments: admin dashboard for pending approvals
    op.create_index(
        'ix_payments_status_created_at',
        'payments',
        ['status', 'created_at'],
        unique=False
    )
    
    # Payments: order's payment history
    op.create_index(
        'ix_payments_order_id_created_at',
        'payments',
        ['order_id', 'created_at'],
        unique=False
    )
    
    # Validation reports: order's validation history
    op.create_index(
        'ix_validation_reports_order_id_created_at',
        'validation_reports',
        ['order_id', 'created_at'],
        unique=False
    )
    
    # Invoices: user's invoices sorted by date
    op.create_index(
        'ix_invoices_user_id_created_at',
        'invoices',
        ['user_id', 'created_at'],
        unique=False
    )
    
    # Invoices: search by customer name (for subscription search)
    op.create_index(
        'ix_invoices_customer_name_search',
        'invoices',
        ['user_id', 'customer_name'],
        unique=False
    )
    
    # Users: admin lookup (for notifications)
    op.create_index(
        'ix_users_role_is_active',
        'users',
        ['role', 'is_active'],
        unique=False
    )


def downgrade() -> None:
    """Remove the composite indexes."""
    
    op.drop_index('ix_orders_status_created_at', table_name='orders')
    op.drop_index('ix_orders_user_id_created_at', table_name='orders')
    op.drop_index('ix_payments_status_created_at', table_name='payments')
    op.drop_index('ix_payments_order_id_created_at', table_name='payments')
    op.drop_index('ix_validation_reports_order_id_created_at', table_name='validation_reports')
    op.drop_index('ix_invoices_user_id_created_at', table_name='invoices')
    op.drop_index('ix_invoices_customer_name_search', table_name='invoices')
    op.drop_index('ix_users_role_is_active', table_name='users')

