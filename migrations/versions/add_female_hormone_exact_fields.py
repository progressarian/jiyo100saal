"""Add female hormone exact fields to Pillar 4

Revision ID: add_female_hormone_exact_fields
Created: 2026-02-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers
revision = 'add_female_hormone_exact_fields'
down_revision = 'add_pillar3_table'  # Update this to the latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add female hormone exact value fields to pillar_4_results table."""
    
    # Add female hormone input mode field
    with op.batch_alter_table('pillar_4_results', schema=None) as batch_op:
        batch_op.add_column(sa.Column('female_hormone_input_mode', sa.String(20), nullable=True))
        
        # Add female exact hormone value fields
        batch_op.add_column(sa.Column('estradiol_female', sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column('progesterone', sa.Numeric(5, 2), nullable=True))
        batch_op.add_column(sa.Column('fsh', sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column('lh', sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column('testosterone_female', sa.Numeric(5, 1), nullable=True))
        batch_op.add_column(sa.Column('amh', sa.Numeric(5, 2), nullable=True))


def downgrade() -> None:
    """Remove female hormone exact value fields from pillar_4_results table."""
    
    with op.batch_alter_table('pillar_4_results', schema=None) as batch_op:
        batch_op.drop_column('amh')
        batch_op.drop_column('testosterone_female')
        batch_op.drop_column('lh')
        batch_op.drop_column('fsh')
        batch_op.drop_column('progesterone')
        batch_op.drop_column('estradiol_female')
        batch_op.drop_column('female_hormone_input_mode')
