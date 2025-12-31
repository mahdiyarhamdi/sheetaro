"""Add dynamic categories, attributes, plans, questions, templates.

Revision ID: 20251231_dynamic
Revises: 20251214_seed_products
Create Date: 2025-12-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251231_dynamic'
down_revision: Union[str, None] = '20251214_seed_products'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE attributeinputtype AS ENUM ('SELECT', 'MULTI_SELECT', 'NUMBER', 'TEXT')")
    op.execute("CREATE TYPE questioninputtype AS ENUM ('TEXT', 'SINGLE_CHOICE', 'MULTI_CHOICE', 'IMAGE_UPLOAD', 'COLOR_PICKER')")
    op.execute("CREATE TYPE steptype AS ENUM ('SELECT_ATTRIBUTE', 'ENTER_VALUE', 'UPLOAD_FILE', 'SELECT_PLAN', 'SELECT_TEMPLATE', 'UPLOAD_LOGO', 'QUESTIONNAIRE', 'VALIDATION', 'PAYMENT', 'CONFIRMATION')")
    
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name_fa', sa.String(100), nullable=False),
        sa.Column('description_fa', sa.String(500), nullable=True),
        sa.Column('icon', sa.String(10), nullable=True),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create category_attributes table
    op.create_table(
        'category_attributes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('name_fa', sa.String(100), nullable=False),
        sa.Column('input_type', postgresql.ENUM('SELECT', 'MULTI_SELECT', 'NUMBER', 'TEXT', name='attributeinputtype', create_type=False), nullable=False),
        sa.Column('is_required', sa.Boolean, default=True, nullable=False),
        sa.Column('min_value', sa.Integer, nullable=True),
        sa.Column('max_value', sa.Integer, nullable=True),
        sa.Column('default_value', sa.String(255), nullable=True),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create attribute_options table
    op.create_table(
        'attribute_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('attribute_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category_attributes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('value', sa.String(100), nullable=False),
        sa.Column('label_fa', sa.String(100), nullable=False),
        sa.Column('price_modifier', sa.Numeric(12, 0), default=0, nullable=False),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create category_design_plans table
    op.create_table(
        'category_design_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('name_fa', sa.String(100), nullable=False),
        sa.Column('description_fa', sa.Text, nullable=True),
        sa.Column('price', sa.Numeric(12, 0), default=0, nullable=False),
        sa.Column('max_revisions', sa.Integer, nullable=True),
        sa.Column('revision_price', sa.Numeric(12, 0), default=0, nullable=False),
        sa.Column('has_questionnaire', sa.Boolean, default=False, nullable=False),
        sa.Column('has_templates', sa.Boolean, default=False, nullable=False),
        sa.Column('has_file_upload', sa.Boolean, default=False, nullable=False),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create design_questions table
    op.create_table(
        'design_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('question_fa', sa.Text, nullable=False),
        sa.Column('input_type', postgresql.ENUM('TEXT', 'SINGLE_CHOICE', 'MULTI_CHOICE', 'IMAGE_UPLOAD', 'COLOR_PICKER', name='questioninputtype', create_type=False), nullable=False),
        sa.Column('is_required', sa.Boolean, default=True, nullable=False),
        sa.Column('placeholder_fa', sa.String(255), nullable=True),
        sa.Column('help_text_fa', sa.Text, nullable=True),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create question_options table
    op.create_table(
        'question_options',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('design_questions.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('value', sa.String(100), nullable=False),
        sa.Column('label_fa', sa.String(200), nullable=False),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create design_templates table
    op.create_table(
        'design_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category_design_plans.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name_fa', sa.String(100), nullable=False),
        sa.Column('description_fa', sa.String(500), nullable=True),
        sa.Column('preview_url', sa.String(500), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('placeholder_x', sa.Integer, nullable=False),
        sa.Column('placeholder_y', sa.Integer, nullable=False),
        sa.Column('placeholder_width', sa.Integer, nullable=False),
        sa.Column('placeholder_height', sa.Integer, nullable=False),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create order_step_templates table
    op.create_table(
        'order_step_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('slug', sa.String(50), nullable=False),
        sa.Column('name_fa', sa.String(100), nullable=False),
        sa.Column('step_type', postgresql.ENUM('SELECT_ATTRIBUTE', 'ENTER_VALUE', 'UPLOAD_FILE', 'SELECT_PLAN', 'SELECT_TEMPLATE', 'UPLOAD_LOGO', 'QUESTIONNAIRE', 'VALIDATION', 'PAYMENT', 'CONFIRMATION', name='steptype', create_type=False), nullable=False),
        sa.Column('config', postgresql.JSONB, nullable=True),
        sa.Column('conditions', postgresql.JSONB, nullable=True),
        sa.Column('is_required', sa.Boolean, default=True, nullable=False),
        sa.Column('sort_order', sa.Integer, default=0, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create order_steps table
    op.create_table(
        'order_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('order_step_templates.id'), nullable=True),
        sa.Column('step_type', postgresql.ENUM('SELECT_ATTRIBUTE', 'ENTER_VALUE', 'UPLOAD_FILE', 'SELECT_PLAN', 'SELECT_TEMPLATE', 'UPLOAD_LOGO', 'QUESTIONNAIRE', 'VALIDATION', 'PAYMENT', 'CONFIRMATION', name='steptype', create_type=False), nullable=False),
        sa.Column('status', sa.String(50), default='pending', nullable=False),
        sa.Column('value', sa.Text, nullable=True),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create question_answers table
    op.create_table(
        'question_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('design_questions.id'), nullable=False, index=True),
        sa.Column('answer_text', sa.Text, nullable=True),
        sa.Column('answer_values', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('answer_file_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('question_answers')
    op.drop_table('order_steps')
    op.drop_table('order_step_templates')
    op.drop_table('design_templates')
    op.drop_table('question_options')
    op.drop_table('design_questions')
    op.drop_table('category_design_plans')
    op.drop_table('attribute_options')
    op.drop_table('category_attributes')
    op.drop_table('categories')
    
    op.execute("DROP TYPE IF EXISTS steptype")
    op.execute("DROP TYPE IF EXISTS questioninputtype")
    op.execute("DROP TYPE IF EXISTS attributeinputtype")

