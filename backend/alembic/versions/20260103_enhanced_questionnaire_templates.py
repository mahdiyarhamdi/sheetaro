"""Enhanced questionnaire and template models.

Revision ID: 20260103_enhanced_qt
Revises: 20260103_base_price
Create Date: 2026-01-03

This migration adds:
- question_sections table for grouping questions
- Enhanced design_questions with validation_rules, conditional logic
- Enhanced question_options with image_url, price_modifier
- Enhanced design_templates with image dimensions
- processed_designs table for customer generated designs
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers
revision = '20260103_enhanced_qt'
down_revision = '20260103_base_price'
branch_labels = None
depends_on = None


def upgrade():
    # Create question_sections table
    op.create_table(
        'question_sections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('plan_id', UUID(as_uuid=True), sa.ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title_fa', sa.String(200), nullable=False),
        sa.Column('description_fa', sa.Text, nullable=True),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Add new columns to design_questions
    op.add_column('design_questions', sa.Column('section_id', UUID(as_uuid=True), sa.ForeignKey('question_sections.id', ondelete='SET NULL'), nullable=True, index=True))
    op.add_column('design_questions', sa.Column('validation_rules', JSONB, server_default='{}', nullable=False))
    op.add_column('design_questions', sa.Column('depends_on_question_id', UUID(as_uuid=True), sa.ForeignKey('design_questions.id', ondelete='SET NULL'), nullable=True))
    op.add_column('design_questions', sa.Column('depends_on_values', JSONB, server_default='[]', nullable=False))
    
    # Add new columns to question_options
    op.add_column('question_options', sa.Column('image_url', sa.String(500), nullable=True))
    op.add_column('question_options', sa.Column('price_modifier', sa.Integer, default=0, nullable=False, server_default='0'))
    
    # Add new columns to design_templates
    op.add_column('design_templates', sa.Column('image_width', sa.Integer, nullable=True))
    op.add_column('design_templates', sa.Column('image_height', sa.Integer, nullable=True))
    
    # Create processed_designs table
    op.create_table(
        'processed_designs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('order_id', UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('design_templates.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('logo_url', sa.String(500), nullable=False),
        sa.Column('preview_url', sa.String(500), nullable=False),
        sa.Column('final_url', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index('idx_questions_section', 'design_questions', ['section_id'])
    op.create_index('idx_sections_plan', 'question_sections', ['plan_id'])
    op.create_index('idx_processed_order', 'processed_designs', ['order_id'])
    op.create_index('idx_processed_template', 'processed_designs', ['template_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_processed_template', table_name='processed_designs')
    op.drop_index('idx_processed_order', table_name='processed_designs')
    op.drop_index('idx_sections_plan', table_name='question_sections')
    op.drop_index('idx_questions_section', table_name='design_questions')
    
    # Drop processed_designs table
    op.drop_table('processed_designs')
    
    # Remove columns from design_templates
    op.drop_column('design_templates', 'image_height')
    op.drop_column('design_templates', 'image_width')
    
    # Remove columns from question_options
    op.drop_column('question_options', 'price_modifier')
    op.drop_column('question_options', 'image_url')
    
    # Remove columns from design_questions
    op.drop_column('design_questions', 'depends_on_values')
    op.drop_column('design_questions', 'depends_on_question_id')
    op.drop_column('design_questions', 'validation_rules')
    op.drop_column('design_questions', 'section_id')
    
    # Drop question_sections table
    op.drop_table('question_sections')

