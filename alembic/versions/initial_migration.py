"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create brawlers table
    op.create_table(
        'brawlers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('rarity', sa.Enum('common', 'rare', 'super_rare', 'epic', 'mythic', 'legendary', 'chromatic', name='brawlerrarity'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('attack_description', sa.Text(), nullable=True),
        sa.Column('super_description', sa.Text(), nullable=True),
        sa.Column('visual_characteristics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brawlers_name'), 'brawlers', ['name'], unique=True)
    
    # Create generated_images table
    op.create_table(
        'generated_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('original_prompt', sa.Text(), nullable=True),
        sa.Column('enhanced_prompt', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('generation_params', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create prompt_templates table
    op.create_table(
        'prompt_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('template', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompt_templates_name'), 'prompt_templates', ['name'], unique=True)
    op.create_index(op.f('ix_prompt_templates_category'), 'prompt_templates', ['category'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_prompt_templates_category'), table_name='prompt_templates')
    op.drop_index(op.f('ix_prompt_templates_name'), table_name='prompt_templates')
    op.drop_table('prompt_templates')
    op.drop_table('generated_images')
    op.drop_index(op.f('ix_brawlers_name'), table_name='brawlers')
    op.drop_table('brawlers')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users') 