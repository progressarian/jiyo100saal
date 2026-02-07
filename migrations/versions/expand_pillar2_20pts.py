"""Expand Pillar 2 to 20 points with Memory, Clock Drawing, and Mental Health

Revision ID: expand_pillar2_20pts
Revises: add_pillar2_table
Create Date: 2026-02-03 09:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'expand_pillar2_20pts'
down_revision = 'add_pillar2_table'
branch_labels = None
depends_on = None


def upgrade():
    # Word Recall Memory - Immediate
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word1', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word2', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word3', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word4', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word5', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word6', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word7', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word8', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word9', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_word10', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_count', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_immediate_category', sa.String(20), nullable=True))
    
    # Word Recall Memory - Delayed
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word1', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word2', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word3', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word4', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word5', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word6', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word7', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word8', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word9', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_word10', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_count', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_delayed_category', sa.String(20), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_retention_pct', sa.Numeric(5, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('memory_retention_flag', sa.Boolean(), nullable=True))
    
    # Digit Span - Split scoring
    op.add_column('pillar_2_results', sa.Column('digit_span_forward_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('digit_span_forward_category', sa.String(20), nullable=True))
    op.add_column('pillar_2_results', sa.Column('digit_span_backward_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('digit_span_backward_category', sa.String(20), nullable=True))
    
    # Clock Drawing Test
    op.add_column('pillar_2_results', sa.Column('clock_circle_intact', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_numbers_present', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_numbers_sequence', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_numbers_position', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_hands_present', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_hands_correct_time', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_hands_proportion', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_score_raw', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_category', sa.String(20), nullable=True))
    op.add_column('pillar_2_results', sa.Column('clock_notes', sa.String(500), nullable=True))
    
    # PHQ-2 Depression Screen
    op.add_column('pillar_2_results', sa.Column('phq2_interest', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('phq2_depressed', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('phq2_total', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('phq2_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('phq2_category', sa.String(20), nullable=True))
    op.add_column('pillar_2_results', sa.Column('phq2_followup_flag', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('phq2_urgent_flag', sa.Boolean(), nullable=True))
    
    # GAD-2 Anxiety Screen
    op.add_column('pillar_2_results', sa.Column('gad2_nervous', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('gad2_worry', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('gad2_total', sa.Integer(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('gad2_points', sa.Numeric(3, 2), nullable=True))
    op.add_column('pillar_2_results', sa.Column('gad2_category', sa.String(20), nullable=True))
    op.add_column('pillar_2_results', sa.Column('gad2_followup_flag', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('gad2_urgent_flag', sa.Boolean(), nullable=True))
    
    # Additional clinical flags
    op.add_column('pillar_2_results', sa.Column('depression_flag', sa.Boolean(), nullable=True))
    op.add_column('pillar_2_results', sa.Column('anxiety_flag', sa.Boolean(), nullable=True))


def downgrade():
    # Remove additional clinical flags
    op.drop_column('pillar_2_results', 'anxiety_flag')
    op.drop_column('pillar_2_results', 'depression_flag')
    
    # Remove GAD-2
    op.drop_column('pillar_2_results', 'gad2_urgent_flag')
    op.drop_column('pillar_2_results', 'gad2_followup_flag')
    op.drop_column('pillar_2_results', 'gad2_category')
    op.drop_column('pillar_2_results', 'gad2_points')
    op.drop_column('pillar_2_results', 'gad2_total')
    op.drop_column('pillar_2_results', 'gad2_worry')
    op.drop_column('pillar_2_results', 'gad2_nervous')
    
    # Remove PHQ-2
    op.drop_column('pillar_2_results', 'phq2_urgent_flag')
    op.drop_column('pillar_2_results', 'phq2_followup_flag')
    op.drop_column('pillar_2_results', 'phq2_category')
    op.drop_column('pillar_2_results', 'phq2_points')
    op.drop_column('pillar_2_results', 'phq2_total')
    op.drop_column('pillar_2_results', 'phq2_depressed')
    op.drop_column('pillar_2_results', 'phq2_interest')
    
    # Remove Clock Drawing
    op.drop_column('pillar_2_results', 'clock_notes')
    op.drop_column('pillar_2_results', 'clock_category')
    op.drop_column('pillar_2_results', 'clock_points')
    op.drop_column('pillar_2_results', 'clock_score_raw')
    op.drop_column('pillar_2_results', 'clock_hands_proportion')
    op.drop_column('pillar_2_results', 'clock_hands_correct_time')
    op.drop_column('pillar_2_results', 'clock_hands_present')
    op.drop_column('pillar_2_results', 'clock_numbers_position')
    op.drop_column('pillar_2_results', 'clock_numbers_sequence')
    op.drop_column('pillar_2_results', 'clock_numbers_present')
    op.drop_column('pillar_2_results', 'clock_circle_intact')
    
    # Remove Digit Span split scoring
    op.drop_column('pillar_2_results', 'digit_span_backward_category')
    op.drop_column('pillar_2_results', 'digit_span_backward_points')
    op.drop_column('pillar_2_results', 'digit_span_forward_category')
    op.drop_column('pillar_2_results', 'digit_span_forward_points')
    
    # Remove Memory Delayed
    op.drop_column('pillar_2_results', 'memory_retention_flag')
    op.drop_column('pillar_2_results', 'memory_retention_pct')
    op.drop_column('pillar_2_results', 'memory_delayed_category')
    op.drop_column('pillar_2_results', 'memory_delayed_points')
    op.drop_column('pillar_2_results', 'memory_delayed_count')
    op.drop_column('pillar_2_results', 'memory_delayed_word10')
    op.drop_column('pillar_2_results', 'memory_delayed_word9')
    op.drop_column('pillar_2_results', 'memory_delayed_word8')
    op.drop_column('pillar_2_results', 'memory_delayed_word7')
    op.drop_column('pillar_2_results', 'memory_delayed_word6')
    op.drop_column('pillar_2_results', 'memory_delayed_word5')
    op.drop_column('pillar_2_results', 'memory_delayed_word4')
    op.drop_column('pillar_2_results', 'memory_delayed_word3')
    op.drop_column('pillar_2_results', 'memory_delayed_word2')
    op.drop_column('pillar_2_results', 'memory_delayed_word1')
    
    # Remove Memory Immediate
    op.drop_column('pillar_2_results', 'memory_immediate_category')
    op.drop_column('pillar_2_results', 'memory_immediate_points')
    op.drop_column('pillar_2_results', 'memory_immediate_count')
    op.drop_column('pillar_2_results', 'memory_immediate_word10')
    op.drop_column('pillar_2_results', 'memory_immediate_word9')
    op.drop_column('pillar_2_results', 'memory_immediate_word8')
    op.drop_column('pillar_2_results', 'memory_immediate_word7')
    op.drop_column('pillar_2_results', 'memory_immediate_word6')
    op.drop_column('pillar_2_results', 'memory_immediate_word5')
    op.drop_column('pillar_2_results', 'memory_immediate_word4')
    op.drop_column('pillar_2_results', 'memory_immediate_word3')
    op.drop_column('pillar_2_results', 'memory_immediate_word2')
    op.drop_column('pillar_2_results', 'memory_immediate_word1')
