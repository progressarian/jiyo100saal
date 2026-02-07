"""
Scoring Package
===============

Age/sex-adjusted scoring tables and functions.
"""

from scoring.section1 import (
    score_body_fat_pct,
    score_lmi,
    score_visceral_fat,
    score_fat_distribution_ag_ratio,
    score_fat_distribution_whr,
    assess_sarcopenia_risk,
    get_body_fat_category,
    get_lmi_category,
)

from scoring.pillar2 import (
    score_dsst,
    score_trails_a,
    score_trails_b,
    calculate_trails_ba_ratio,
    score_digit_span,
    score_verbal_fluency,
    calculate_pillar2_alerts,
    get_pillar2_category,
)

__all__ = [
    # Section 1
    'score_body_fat_pct',
    'score_lmi',
    'score_visceral_fat',
    'score_fat_distribution_ag_ratio',
    'score_fat_distribution_whr',
    'assess_sarcopenia_risk',
    'get_body_fat_category',
    'get_lmi_category',
    # Pillar 2
    'score_dsst',
    'score_trails_a',
    'score_trails_b',
    'calculate_trails_ba_ratio',
    'score_digit_span',
    'score_verbal_fluency',
    'calculate_pillar2_alerts',
    'get_pillar2_category',
]
