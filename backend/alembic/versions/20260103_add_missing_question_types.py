"""Add missing question input types to enum.

Revision ID: 20260103_question_types
Revises: 20260103_enhanced_questionnaire_templates
Create Date: 2026-01-03 12:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260103_question_types'
down_revision = '20260103_enhanced_questionnaire_templates'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing enum values to questioninputtype."""
    # Add TEXTAREA type
    op.execute("ALTER TYPE questioninputtype ADD VALUE IF NOT EXISTS 'TEXTAREA'")
    # Add NUMBER type
    op.execute("ALTER TYPE questioninputtype ADD VALUE IF NOT EXISTS 'NUMBER'")
    # Add FILE_UPLOAD type
    op.execute("ALTER TYPE questioninputtype ADD VALUE IF NOT EXISTS 'FILE_UPLOAD'")
    # Add DATE_PICKER type
    op.execute("ALTER TYPE questioninputtype ADD VALUE IF NOT EXISTS 'DATE_PICKER'")
    # Add SCALE type
    op.execute("ALTER TYPE questioninputtype ADD VALUE IF NOT EXISTS 'SCALE'")


def downgrade():
    """Note: PostgreSQL doesn't support removing enum values easily.
    
    To fully downgrade, you would need to:
    1. Create a new enum without the values
    2. Update all existing data
    3. Drop the old enum and rename the new one
    
    For safety, we don't implement this.
    """
    pass

