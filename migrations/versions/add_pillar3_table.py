"""Add Pillar 3 Results table

Revision ID: add_pillar3_table
Created: 2026-02-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers
revision = 'add_pillar3_table'
down_revision = 'expand_pillar2_20pts'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pillar_3_results table
    op.create_table(
        'pillar_3_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=False),
        
        # Glucose Metabolism (5 pts)
        sa.Column('glucose_input_mode', sa.String(20), nullable=True),
        sa.Column('fasting_glucose', sa.Numeric(5, 1), nullable=True),
        sa.Column('hba1c', sa.Numeric(4, 2), nullable=True),
        sa.Column('glucose_category', sa.String(50), nullable=True),
        sa.Column('glucose_blood_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('glucose_blood_category', sa.String(50), nullable=True),
        sa.Column('post_meal_feeling', sa.String(50), nullable=True),
        sa.Column('fasting_tolerance', sa.String(50), nullable=True),
        sa.Column('glucose_functional_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('glucose_total_points', sa.Numeric(3, 2), nullable=True),
        
        # Digestive Function (6 pts)
        sa.Column('bowel_frequency', sa.String(50), nullable=True),
        sa.Column('bowel_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('stool_consistency', sa.String(50), nullable=True),
        sa.Column('stool_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('reflux_frequency', sa.String(50), nullable=True),
        sa.Column('reflux_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('meal_comfort', sa.String(50), nullable=True),
        sa.Column('meal_comfort_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('digestive_total_points', sa.Numeric(3, 2), nullable=True),
        
        # Gut Symptoms (4 pts)
        sa.Column('bloating_frequency', sa.String(50), nullable=True),
        sa.Column('bloating_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('abdominal_pain', sa.String(50), nullable=True),
        sa.Column('pain_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('food_intolerances', sa.String(50), nullable=True),
        sa.Column('intolerance_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('gut_symptoms_total_points', sa.Numeric(3, 2), nullable=True),
        
        # Liver Function (3 pts)
        sa.Column('liver_input_mode', sa.String(20), nullable=True),
        sa.Column('alt_value', sa.Numeric(5, 1), nullable=True),
        sa.Column('ast_value', sa.Numeric(5, 1), nullable=True),
        sa.Column('liver_category_input', sa.String(50), nullable=True),
        sa.Column('liver_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('liver_category', sa.String(50), nullable=True),
        
        # Inflammation (2 pts)
        sa.Column('crp_input_mode', sa.String(20), nullable=True),
        sa.Column('hs_crp', sa.Numeric(5, 2), nullable=True),
        sa.Column('crp_category_input', sa.String(50), nullable=True),
        sa.Column('crp_points', sa.Numeric(3, 2), nullable=True),
        sa.Column('crp_risk_level', sa.String(50), nullable=True),
        
        # Totals
        sa.Column('pillar3_total', sa.Numeric(4, 2), nullable=True),
        sa.Column('pillar3_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('pillar3_category', sa.String(50), nullable=True),
        sa.Column('functional_age_modifier', sa.Numeric(3, 1), nullable=True),
        
        # Clinical flags
        sa.Column('clinical_alerts', sa.JSON(), nullable=True),
        sa.Column('diabetes_flag', sa.Boolean(), nullable=True, default=False),
        sa.Column('prediabetes_flag', sa.Boolean(), nullable=True, default=False),
        sa.Column('liver_concern_flag', sa.Boolean(), nullable=True, default=False),
        sa.Column('inflammation_flag', sa.Boolean(), nullable=True, default=False),
        sa.Column('digestive_disorder_flag', sa.Boolean(), nullable=True, default=False),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('assessment_id', name='uq_pillar3_assessment')
    )
    
    # Create index on assessment_id
    op.create_index('ix_pillar_3_results_assessment_id', 'pillar_3_results', ['assessment_id'])


def downgrade() -> None:
    op.drop_index('ix_pillar_3_results_assessment_id', table_name='pillar_3_results')
    op.drop_table('pillar_3_results')
