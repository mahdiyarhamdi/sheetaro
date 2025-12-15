"""Seed initial products data.

Revision ID: 20251214_seed_products
Revises: 20251214_set_initial_admin
Create Date: 2025-12-14
"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251214_seed_products'
down_revision: Union[str, None] = '20251214_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert initial products for testing and production use."""
    
    # Label products - Paper
    op.execute(f"""
        INSERT INTO products (id, type, name, name_fa, description, size, material, base_price, min_quantity, is_active, sort_order)
        VALUES 
        ('{uuid.uuid4()}', 'LABEL', 'Paper Label 5x5', 'لیبل کاغذی ۵×۵', 'لیبل کاغذی با کیفیت بالا', '5x5cm', 'PAPER', 2000, 100, true, 1),
        ('{uuid.uuid4()}', 'LABEL', 'Paper Label 7x7', 'لیبل کاغذی ۷×۷', 'لیبل کاغذی با کیفیت بالا', '7x7cm', 'PAPER', 3000, 100, true, 2),
        ('{uuid.uuid4()}', 'LABEL', 'Paper Label 10x10', 'لیبل کاغذی ۱۰×۱۰', 'لیبل کاغذی سایز بزرگ', '10x10cm', 'PAPER', 4500, 100, true, 3)
    """)
    
    # Label products - PVC
    op.execute(f"""
        INSERT INTO products (id, type, name, name_fa, description, size, material, base_price, min_quantity, is_active, sort_order)
        VALUES 
        ('{uuid.uuid4()}', 'LABEL', 'PVC Label 5x5', 'لیبل PVC ۵×۵', 'لیبل PVC ضدآب و مقاوم', '5x5cm', 'PVC', 3500, 100, true, 4),
        ('{uuid.uuid4()}', 'LABEL', 'PVC Label 7x7', 'لیبل PVC ۷×۷', 'لیبل PVC ضدآب و مقاوم', '7x7cm', 'PVC', 5000, 100, true, 5)
    """)
    
    # Label products - Metallic
    op.execute(f"""
        INSERT INTO products (id, type, name, name_fa, description, size, material, base_price, min_quantity, is_active, sort_order)
        VALUES 
        ('{uuid.uuid4()}', 'LABEL', 'Metallic Label 5x5', 'لیبل متالیک ۵×۵', 'لیبل متالیک براق و لوکس', '5x5cm', 'METALLIC', 5000, 100, true, 6),
        ('{uuid.uuid4()}', 'LABEL', 'Metallic Label 7x7', 'لیبل متالیک ۷×۷', 'لیبل متالیک براق و لوکس', '7x7cm', 'METALLIC', 7000, 100, true, 7)
    """)
    
    # Invoice templates
    op.execute(f"""
        INSERT INTO products (id, type, name, name_fa, description, size, material, base_price, min_quantity, is_active, sort_order)
        VALUES 
        ('{uuid.uuid4()}', 'INVOICE', 'Invoice A5', 'فاکتور A5', 'فاکتور سایز A5 دو برگی', 'A5', NULL, 15000, 50, true, 10),
        ('{uuid.uuid4()}', 'INVOICE', 'Invoice A4', 'فاکتور A4', 'فاکتور سایز A4 دو برگی', 'A4', NULL, 25000, 50, true, 11),
        ('{uuid.uuid4()}', 'INVOICE', 'Invoice A5 Triple', 'فاکتور A5 سه برگی', 'فاکتور سایز A5 سه برگی رسمی', 'A5', NULL, 22000, 50, true, 12)
    """)


def downgrade() -> None:
    """Remove seeded products."""
    op.execute("DELETE FROM products WHERE name IN ('Paper Label 5x5', 'Paper Label 7x7', 'Paper Label 10x10', 'PVC Label 5x5', 'PVC Label 7x7', 'Metallic Label 5x5', 'Metallic Label 7x7', 'Invoice A5', 'Invoice A4', 'Invoice A5 Triple')")

