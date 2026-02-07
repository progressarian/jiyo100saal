"""Add Pillar 2 Cognitive Function table

Revision ID: add_pillar2_table
Revises: 99d54e2bdbf8
Create Date: 2026-02-03 04:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_pillar2_table'
down_revision = '99d54e2bdbf8'
branch_labels = None
depends_on = None


def upgrade():
    # Create pillar_2_results table
    op.create_table(
        'pillar_2_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=False),
        
        # DSST - Digital Symbol Substitution Test
        sa.Column('dsst_score', sa.Integer(), nullable=True),
        sa.Column('dsst_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('dsst_category', sa.String(20), nullable=True),
        sa.Column('dsst_percentile', sa.Integer(), nullable=True),
        
        # Trail Making Test A
        sa.Column('trails_a_time', sa.Numeric(5, 1), nullable=True),
        sa.Column('trails_a_errors', sa.Integer(), nullable=True),
        sa.Column('trails_a_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('trails_a_category', sa.String(20), nullable=True),
        
        # Trail Making Test B
        sa.Column('trails_b_time', sa.Numeric(5, 1), nullable=True),
        sa.Column('trails_b_errors', sa.Integer(), nullable=True),
        sa.Column('trails_b_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('trails_b_category', sa.String(20), nullable=True),
        
        # Trails combined
        sa.Column('trails_ba_ratio', sa.Numeric(4, 2), nullable=True),
        sa.Column('trails_total_points', sa.Numeric(3, 2), nullable=True),
        
        # Digit Span
        sa.Column('digit_span_forward', sa.Integer(), nullable=True),
        sa.Column('digit_span_backward', sa.Integer(), nullable=True),
        sa.Column('digit_span_total', sa.Integer(), nullable=True),
        sa.Column('digit_span_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('digit_span_category', sa.String(20), nullable=True),
        
        # Verbal Fluency
        sa.Column('verbal_fluency_animals', sa.Integer(), nullable=True),
        sa.Column('verbal_fluency_repetitions', sa.Integer(), nullable=True),
        sa.Column('verbal_fluency_intrusions', sa.Integer(), nullable=True),
        sa.Column('verbal_fluency_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('verbal_fluency_category', sa.String(20), nullable=True),
        
        # Totals
        sa.Column('pillar2_total', sa.Numeric(4, 2), nullable=True),
        sa.Column('pillar2_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('pillar2_category', sa.String(20), nullable=True),
        sa.Column('functional_age_modifier', sa.Numeric(4, 1), nullable=True),
        
        # Clinical alerts
        sa.Column('clinical_alerts', sa.JSON(), nullable=True),
        sa.Column('cognitive_concern_flag', sa.Boolean(), nullable=True),
        sa.Column('executive_dysfunction_flag', sa.Boolean(), nullable=True),
        sa.Column('memory_deficit_flag', sa.Boolean(), nullable=True),
        sa.Column('language_concern_flag', sa.Boolean(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('assessment_id'),
    )
    
    # Create index on assessment_id
    op.create_index('ix_pillar_2_results_assessment_id', 'pillar_2_results', ['assessment_id'])


def downgrade():
    op.drop_index('ix_pillar_2_results_assessment_id', table_name='pillar_2_results')
    op.drop_table('pillar_2_results')
