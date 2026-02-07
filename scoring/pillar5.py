"""
Pillar 5 Scoring Functions - Disease Prevention & Clinical Biomarkers
======================================================================

18+ scoring functions for Pillar 5 tests.
Stricter thresholds for longevity focus.
"""

from decimal import Decimal
from typing import Tuple, Optional


# ==============================================================================
# TEST 1: STANDARD LIPID PANEL (4 POINTS)
# ==============================================================================

def score_ldl(ldl: float) -> Tuple[Decimal, str]:
    """Score LDL cholesterol - stricter thresholds."""
    if ldl < 70:
        return Decimal('1.0'), 'Optimal'
    elif ldl < 100:
        return Decimal('0.85'), 'Very Good'
    elif ldl < 130:
        return Decimal('0.65'), 'Acceptable'
    elif ldl < 160:
        return Decimal('0.35'), 'High'
    else:
        return Decimal('0.0'), 'Very High'


def score_hdl(hdl: float, sex: str) -> Tuple[Decimal, str]:
    """Score HDL cholesterol - sex-adjusted."""
    if sex == 'male':
        if hdl >= 60:
            return Decimal('1.5'), 'Optimal'
        elif hdl >= 50:
            return Decimal('1.0'), 'Good'
        elif hdl >= 40:
            return Decimal('0.5'), 'Acceptable'
        else:
            return Decimal('0.0'), 'Low'
    else:  # female
        if hdl >= 70:
            return Decimal('1.5'), 'Optimal'
        elif hdl >= 60:
            return Decimal('1.0'), 'Good'
        elif hdl >= 50:
            return Decimal('0.5'), 'Acceptable'
        else:
            return Decimal('0.0'), 'Low'


def score_triglycerides(tg: float) -> Tuple[Decimal, str]:
    """Score triglycerides - stricter."""
    if tg < 100:
        return Decimal('1.0'), 'Optimal'
    elif tg < 150:
        return Decimal('0.7'), 'Good'
    elif tg < 200:
        return Decimal('0.4'), 'Borderline High'
    elif tg < 500:
        return Decimal('0.1'), 'High'
    else:
        return Decimal('0.0'), 'Very High'


def score_ratio(ratio: float) -> Tuple[Decimal, str]:
    """Score Total/HDL ratio."""
    if ratio < 3.0:
        return Decimal('0.5'), 'Optimal'
    elif ratio < 4.0:
        return Decimal('0.35'), 'Good'
    elif ratio < 5.0:
        return Decimal('0.2'), 'Acceptable'
    else:
        return Decimal('0.0'), 'High Risk'


# ==============================================================================
# TEST 2: ADVANCED LIPIDS (2 POINTS)
# ==============================================================================

def score_apob(apob: float) -> Tuple[Decimal, str]:
    """Score ApoB."""
    if apob < 80:
        return Decimal('1.0'), 'Optimal'
    elif apob < 100:
        return Decimal('0.7'), 'Good'
    elif apob < 120:
        return Decimal('0.4'), 'Acceptable'
    else:
        return Decimal('0.0'), 'High'


def score_lp_a(lp_a: float) -> Tuple[Decimal, str]:
    """Score Lp(a)."""
    if lp_a < 30:
        return Decimal('1.0'), 'Optimal'
    elif lp_a < 50:
        return Decimal('0.7'), 'Good'
    elif lp_a < 100:
        return Decimal('0.4'), 'Elevated'
    else:
        return Decimal('0.0'), 'Very High'


# ==============================================================================
# TEST 3: CARDIAC IMAGING (3 POINTS)
# ==============================================================================

def score_cac(cac: float) -> Tuple[Decimal, str]:
    """Score CAC (Agatston score)."""
    if cac == 0:
        return Decimal('1.0'), 'Zero (Optimal)'
    elif cac < 10:
        return Decimal('0.9'), 'Minimal'
    elif cac < 100:
        return Decimal('0.7'), 'Mild'
    elif cac < 400:
        return Decimal('0.4'), 'Moderate'
    else:
        return Decimal('0.0'), 'Extensive'


def score_tmt(result: str) -> Tuple[Decimal, str]:
    """Score TMT result."""
    if result == 'negative':
        return Decimal('1.0'), 'Negative'
    elif result == 'positive':
        return Decimal('0.3'), 'Positive - further workup'
    elif result == 'abnormal':
        return Decimal('0.0'), 'Abnormal - significant'
    else:  # notPerformed
        return Decimal('0.6'), 'Not Performed'


def score_echo_ct(result: str) -> Tuple[Decimal, str]:
    """Score Echo/CT result."""
    if result == 'normal':
        return Decimal('1.0'), 'Normal'
    elif result == 'mild':
        return Decimal('0.7'), 'Mild abnormality'
    elif result == 'moderate':
        return Decimal('0.4'), 'Moderate abnormality'
    elif result == 'severe':
        return Decimal('0.0'), 'Severe abnormality'
    else:  # notPerformed
        return Decimal('0.6'), 'Not Performed'


# ==============================================================================
# TEST 4: KIDNEY FUNCTION (2 POINTS)
# ==============================================================================

def score_kidney_exact(egfr: float) -> Tuple[Decimal, str]:
    """Score kidney function from eGFR."""
    if egfr >= 90:
        return Decimal('2.0'), 'Normal'
    elif egfr >= 60:
        return Decimal('1.5'), 'Mild decrease'
    elif egfr >= 45:
        return Decimal('1.0'), 'CKD Stage 3a'
    elif egfr >= 30:
        return Decimal('0.5'), 'CKD Stage 3b'
    elif egfr >= 15:
        return Decimal('0.2'), 'CKD Stage 4'
    else:
        return Decimal('0.0'), 'CKD Stage 5 (Kidney Failure)'


def score_kidney_category(category: str) -> Tuple[Decimal, str]:
    """Score kidney from category."""
    if category == 'normal':
        return Decimal('2.0'), 'Normal'
    elif category == 'mildDecrease':
        return Decimal('1.5'), 'Mild decrease'
    elif category == 'moderateDecrease':
        return Decimal('1.0'), 'Moderate decrease'
    elif category == 'severeDecrease':
        return Decimal('0.5'), 'Severe decrease'
    else:
        return Decimal('0.0'), 'Kidney Failure'


# ==============================================================================
# TEST 5: CANCER SCREENING (4 POINTS)
# ==============================================================================

def score_cancer_screening(compliance_pct: float) -> Tuple[Decimal, str]:
    """Score cancer screening compliance."""
    if compliance_pct >= 100:
        return Decimal('4.0'), 'Complete'
    elif compliance_pct >= 80:
        return Decimal('3.2'), 'Good'
    elif compliance_pct >= 60:
        return Decimal('2.4'), 'Acceptable'
    elif compliance_pct >= 40:
        return Decimal('1.6'), 'Poor'
    else:
        return Decimal('0.8'), 'Very Poor'


# ==============================================================================
# TEST 6: ORGAN IMAGING (2 POINTS)
# ==============================================================================

def score_organ_imaging(result: str) -> Tuple[Decimal, str]:
    """Score organ imaging result."""
    if result == 'normal':
        return Decimal('1.0'), 'Normal'
    elif result == 'abnormal':
        return Decimal('0.0'), 'Abnormal findings'
    else:  # notPerformed
        return Decimal('0.6'), 'Not Performed'


# ==============================================================================
# TEST 7: BONE HEALTH (1 POINT)
# ==============================================================================

def score_bone(t_score: float) -> Tuple[Decimal, str]:
    """Score bone density from T-score."""
    if t_score >= -1.0:
        return Decimal('1.0'), 'Normal'
    elif t_score >= -2.5:
        return Decimal('0.5'), 'Osteopenia'
    else:
        return Decimal('0.0'), 'Osteoporosis'


# ==============================================================================
# TEST 8: SENSORY HEALTH (1 POINT)
# ==============================================================================

def score_vision(status: str) -> Tuple[Decimal, str]:
    """Score vision status."""
    if status == 'excellent':
        return Decimal('0.5'), 'Excellent'
    elif status == 'good':
        return Decimal('0.35'), 'Good'
    elif status == 'fair':
        return Decimal('0.2'), 'Fair'
    else:  # poor
        return Decimal('0.0'), 'Poor'


def score_hearing(status: str) -> Tuple[Decimal, str]:
    """Score hearing status."""
    if status == 'excellent':
        return Decimal('0.5'), 'Excellent'
    elif status == 'good':
        return Decimal('0.35'), 'Good'
    elif status == 'fair':
        return Decimal('0.2'), 'Fair'
    else:  # poor
        return Decimal('0.0'), 'Poor'


# ==============================================================================
# TEST 9: CHRONIC DISEASE MANAGEMENT (1 POINT)
# ==============================================================================

def score_chronic_disease(has_disease: bool, management: str) -> Tuple[Decimal, str]:
    """Score chronic disease management."""
    if not has_disease:
        return Decimal('1.0'), 'No chronic disease'
    
    if management == 'excellent':
        return Decimal('1.0'), 'Excellent management'
    elif management == 'good':
        return Decimal('0.7'), 'Good management'
    elif management == 'fair':
        return Decimal('0.4'), 'Fair management'
    elif management == 'poor':
        return Decimal('0.1'), 'Poor management'
    else:  # none
        return Decimal('0.0'), 'Unmanaged'
