"""Add dynamic template placeholders and system fonts.

Revision ID: 20260131_dynamic_templates
Revises: 20260121_web_auth
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260131_dynamic_templates'
down_revision: Union[str, None] = '20260121_web_auth'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types
    placeholdertype = postgresql.ENUM('IMAGE', 'TEXT', name='placeholdertype', create_type=False)
    placeholdertype.create(op.get_bind(), checkfirst=True)
    
    textalign = postgresql.ENUM('left', 'center', 'right', name='textalign', create_type=False)
    textalign.create(op.get_bind(), checkfirst=True)
    
    # Create system_fonts table
    op.create_table(
        'system_fonts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('name_fa', sa.String(100), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('variants', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('sample_text', sa.String(200), nullable=True, server_default='نمونه متن فارسی - Sample Text 123'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_system_fonts_name', 'system_fonts', ['name'])
    
    # Create template_placeholders table
    op.create_table(
        'template_placeholders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('design_templates.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type', placeholdertype, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('label_fa', sa.String(100), nullable=False),
        sa.Column('x', sa.Integer, nullable=False, server_default='0'),
        sa.Column('y', sa.Integer, nullable=False, server_default='0'),
        sa.Column('width', sa.Integer, nullable=False, server_default='100'),
        sa.Column('height', sa.Integer, nullable=False, server_default='100'),
        sa.Column('rotation', sa.Integer, nullable=False, server_default='0'),
        sa.Column('is_required', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer, nullable=False, server_default='0'),
        # Text-specific fields
        sa.Column('font_family', sa.String(100), nullable=True),
        sa.Column('font_size', sa.Integer, nullable=True, server_default='24'),
        sa.Column('font_weight', sa.Integer, nullable=True, server_default='400'),
        sa.Column('font_color', sa.String(9), nullable=True, server_default='#000000'),
        sa.Column('text_align', textalign, nullable=True, server_default='right'),
        sa.Column('max_length', sa.Integer, nullable=True),
        sa.Column('default_value', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Update design_templates table - make placeholder fields nullable and add rotation
    op.alter_column('design_templates', 'preview_url', existing_type=sa.String(500), nullable=True)
    op.alter_column('design_templates', 'file_url', existing_type=sa.String(500), nullable=True)
    op.alter_column('design_templates', 'placeholder_x', existing_type=sa.Integer, nullable=True)
    op.alter_column('design_templates', 'placeholder_y', existing_type=sa.Integer, nullable=True)
    op.alter_column('design_templates', 'placeholder_width', existing_type=sa.Integer, nullable=True)
    op.alter_column('design_templates', 'placeholder_height', existing_type=sa.Integer, nullable=True)
    
    # Add placeholder_rotation column if it doesn't exist
    op.add_column('design_templates', sa.Column('placeholder_rotation', sa.Integer, nullable=True, server_default='0'))
    
    # Seed some default Persian fonts
    op.execute("""
        INSERT INTO system_fonts (id, name, name_fa, file_url, variants, sample_text, is_active)
        VALUES 
        (gen_random_uuid(), 'IRANSans', 'ایران سنس', NULL, '[]', 'نمونه متن فارسی - Sample Text 123', true),
        (gen_random_uuid(), 'Vazirmatn', 'وزیر متن', NULL, '[]', 'نمونه متن فارسی - Sample Text 123', true),
        (gen_random_uuid(), 'Yekan', 'یکان', NULL, '[]', 'نمونه متن فارسی - Sample Text 123', true)
        ON CONFLICT (name) DO NOTHING;
    """)


def downgrade() -> None:
    # Drop template_placeholders table
    op.drop_table('template_placeholders')
    
    # Drop system_fonts table
    op.drop_index('ix_system_fonts_name', table_name='system_fonts')
    op.drop_table('system_fonts')
    
    # Revert design_templates changes
    op.drop_column('design_templates', 'placeholder_rotation')
    op.alter_column('design_templates', 'placeholder_height', existing_type=sa.Integer, nullable=False)
    op.alter_column('design_templates', 'placeholder_width', existing_type=sa.Integer, nullable=False)
    op.alter_column('design_templates', 'placeholder_y', existing_type=sa.Integer, nullable=False)
    op.alter_column('design_templates', 'placeholder_x', existing_type=sa.Integer, nullable=False)
    op.alter_column('design_templates', 'file_url', existing_type=sa.String(500), nullable=False)
    op.alter_column('design_templates', 'preview_url', existing_type=sa.String(500), nullable=False)
    
    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS textalign")
    op.execute("DROP TYPE IF EXISTS placeholdertype")

