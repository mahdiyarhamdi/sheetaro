"""Fix text_align column - change from enum to VARCHAR

Revision ID: fix_text_align_col
Revises: 20260131_dynamic_template_placeholders
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_text_align_col'
down_revision = '20260131_dynamic_templates'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change text_align column from textalign enum to VARCHAR(10)
    # This fixes the issue where SQLAlchemy sends uppercase enum names
    # but PostgreSQL enum expects lowercase values
    op.execute("""
        ALTER TABLE template_placeholders 
        ALTER COLUMN text_align DROP DEFAULT;
    """)
    op.execute("""
        ALTER TABLE template_placeholders 
        ALTER COLUMN text_align TYPE VARCHAR(10) USING text_align::TEXT;
    """)


def downgrade() -> None:
    # Revert back to enum type
    op.execute("""
        ALTER TABLE template_placeholders 
        ALTER COLUMN text_align TYPE textalign USING text_align::textalign;
    """)
    op.execute("""
        ALTER TABLE template_placeholders 
        ALTER COLUMN text_align SET DEFAULT 'right'::textalign;
    """)

