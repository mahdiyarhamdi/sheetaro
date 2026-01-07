"""Full schema for Sheetaro MVP.

Revision ID: 20251213_full
Revises: 226f2634a9c9
Create Date: 2025-12-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251213_full'
down_revision: Union[str, None] = '226f2634a9c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create all enum types
    op.execute("CREATE TYPE userrole AS ENUM ('CUSTOMER', 'DESIGNER', 'VALIDATOR', 'PRINT_SHOP', 'ADMIN')")
    op.execute("CREATE TYPE producttype AS ENUM ('LABEL', 'INVOICE')")
    op.execute("CREATE TYPE materialtype AS ENUM ('PAPER', 'PVC', 'METALLIC')")
    op.execute("CREATE TYPE designplan AS ENUM ('PUBLIC', 'SEMI_PRIVATE', 'PRIVATE', 'OWN_DESIGN')")
    op.execute("CREATE TYPE orderstatus AS ENUM ('PENDING', 'AWAITING_VALIDATION', 'NEEDS_ACTION', 'DESIGNING', 'READY_FOR_PRINT', 'PRINTING', 'SHIPPED', 'DELIVERED', 'CANCELLED')")
    op.execute("CREATE TYPE validationstatus AS ENUM ('PENDING', 'PASSED', 'FAILED', 'FIXED')")
    op.execute("CREATE TYPE paymenttype AS ENUM ('VALIDATION', 'DESIGN', 'FIX', 'PRINT', 'SUBSCRIPTION')")
    op.execute("CREATE TYPE paymentstatus AS ENUM ('PENDING', 'SUCCESS', 'FAILED')")
    op.execute("CREATE TYPE subscriptionplan AS ENUM ('ADVANCED_SEARCH')")
    
    # Add city and role columns to users table
    op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('role', postgresql.ENUM('CUSTOMER', 'DESIGNER', 'VALIDATOR', 'PRINT_SHOP', 'ADMIN', name='userrole', create_type=False), nullable=False, server_default='CUSTOMER'))
    
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('type', postgresql.ENUM('LABEL', 'INVOICE', name='producttype', create_type=False), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('name_fa', sa.String(255), nullable=True),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('size', sa.String(50), nullable=False),
        sa.Column('material', postgresql.ENUM('PAPER', 'PVC', 'METALLIC', name='materialtype', create_type=False), nullable=True),
        sa.Column('base_price', sa.Numeric(12, 0), nullable=False),
        sa.Column('min_quantity', sa.Numeric(10, 0), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Numeric(5, 0), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_type', 'products', ['type'])
    
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('design_plan', postgresql.ENUM('PUBLIC', 'SEMI_PRIVATE', 'PRIVATE', 'OWN_DESIGN', name='designplan', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'AWAITING_VALIDATION', 'NEEDS_ACTION', 'DESIGNING', 'READY_FOR_PRINT', 'PRINTING', 'SHIPPED', 'DELIVERED', 'CANCELLED', name='orderstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('design_file_url', sa.String(500), nullable=True),
        sa.Column('validation_status', postgresql.ENUM('PENDING', 'PASSED', 'FAILED', 'FIXED', name='validationstatus', create_type=False), nullable=True),
        sa.Column('validation_requested', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('assigned_designer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_validator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_printshop_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('revision_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_revisions', sa.Integer(), nullable=True),
        sa.Column('design_price', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('validation_price', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('fix_price', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('print_price', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('total_price', sa.Numeric(12, 0), nullable=False),
        sa.Column('tracking_code', sa.String(100), nullable=True),
        sa.Column('shipping_address', sa.Text(), nullable=True),
        sa.Column('customer_notes', sa.Text(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('printed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('shipped_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_orders_id', 'orders', ['id'])
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_product_id', 'orders', ['product_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', postgresql.ENUM('VALIDATION', 'DESIGN', 'FIX', 'PRINT', 'SUBSCRIPTION', name='paymenttype', create_type=False), nullable=False),
        sa.Column('amount', sa.Numeric(12, 0), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'SUCCESS', 'FAILED', name='paymentstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('transaction_id', sa.String(100), nullable=True, unique=True),
        sa.Column('authority', sa.String(100), nullable=True),
        sa.Column('ref_id', sa.String(100), nullable=True),
        sa.Column('card_pan', sa.String(20), nullable=True),
        sa.Column('callback_data', sa.String(1000), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_payments_id', 'payments', ['id'])
    op.create_index('ix_payments_order_id', 'payments', ['order_id'])
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    
    # Create validation_reports table
    op.create_table(
        'validation_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('validator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('issues', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('fix_cost', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('passed', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_validation_reports_id', 'validation_reports', ['id'])
    op.create_index('ix_validation_reports_order_id', 'validation_reports', ['order_id'])
    op.create_index('ix_validation_reports_validator_id', 'validation_reports', ['validator_id'])
    
    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('customer_code', sa.String(50), nullable=True),
        sa.Column('customer_address', sa.Text(), nullable=True),
        sa.Column('customer_phone', sa.String(20), nullable=True),
        sa.Column('customer_national_id', sa.String(20), nullable=True),
        sa.Column('items', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('subtotal', sa.Numeric(12, 0), nullable=False),
        sa.Column('tax_amount', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(12, 0), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('pdf_file_url', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_invoices_id', 'invoices', ['id'])
    op.create_index('ix_invoices_order_id', 'invoices', ['order_id'])
    op.create_index('ix_invoices_user_id', 'invoices', ['user_id'])
    op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'])
    
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan', postgresql.ENUM('ADVANCED_SEARCH', name='subscriptionplan', create_type=False), nullable=False),
        sa.Column('price', sa.Numeric(12, 0), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payments.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('subscriptions')
    op.drop_table('invoices')
    op.drop_table('validation_reports')
    op.drop_table('payments')
    op.drop_table('orders')
    op.drop_table('products')
    
    # Remove columns from users
    op.drop_column('users', 'role')
    op.drop_column('users', 'city')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS subscriptionplan")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS paymenttype")
    op.execute("DROP TYPE IF EXISTS validationstatus")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS designplan")
    op.execute("DROP TYPE IF EXISTS materialtype")
    op.execute("DROP TYPE IF EXISTS producttype")
    op.execute("DROP TYPE IF EXISTS userrole")





