"""
Section 1 Scoring - Body Composition
====================================

Age/sex-adjusted scoring tables per specification Part 3.4.
"""

from typing import Tuple, Optional


# =============================================================================
# BODY FAT PERCENTAGE SCORING (Spec 3.4.2)
# =============================================================================

# Body fat % thresholds: (upper_bound, score_pct, category)
# Score is percentage (100 = Excellent, 25 = Very Poor)

BODY_FAT_THRESHOLDS = {
    'male': {
        '30-49': [
            (14, 100, 'Excellent'),
            (17, 85, 'Good'),
            (21, 70, 'Fair'),
            (24, 50, 'Poor'),
            (float('inf'), 25, 'Very Poor'),
        ],
        '50-69': [
            (16, 100, 'Excellent'),
            (19, 85, 'Good'),
            (23, 70, 'Fair'),
            (26, 50, 'Poor'),
            (float('inf'), 25, 'Very Poor'),
        ],
        '70+': [
            (18, 100, 'Excellent'),
            (21, 85, 'Good'),
            (25, 70, 'Fair'),
            (28, 50, 'Poor'),
            (float('inf'), 25, 'Very Poor'),
        ],
    },
    'female': {
        '30-49': [
            (20, 100, 'Excellent'),
            (24, 85, 'Good'),
            (29, 70, 'Fair'),
            (32, 50, 'Poor'),
            (float('inf'), 25, 'Very Poor'),
        ],
        '50-69': [
            (22, 100, 'Excellent'),
            (26, 85, 'Good'),
            (31, 70, 'Fair'),
            (34, 50, 'Poor'),
            (float('inf'), 25, 'Very Poor'),
        ],
        '70+': [
            (24, 100, 'Excellent'),
            (28, 85, 'Good'),
            (33, 70, 'Fair'),
            (36, 50, 'Poor'),
            (float('inf'), 25, 'Very Poor'),
        ],
    }
}


def get_age_group_body_fat(age: int) -> str:
    """Get age group key for body fat scoring."""
    if age < 50:
        return '30-49'
    elif age < 70:
        return '50-69'
    else:
        return '70+'


def score_body_fat_pct(body_fat_pct: float, age: int, sex: str) -> Tuple[int, str]:
    """
    Score body fat percentage using age/sex-adjusted tables.
    
    Args:
        body_fat_pct: Body fat percentage
        age: Age in years
        sex: 'male' or 'female'
        
    Returns:
        Tuple of (score percentage 0-100, category string)
    """
    if sex not in ('male', 'female'):
        return 0, 'Unknown'
    
    age_group = get_age_group_body_fat(age)
    thresholds = BODY_FAT_THRESHOLDS[sex][age_group]
    
    for upper, score, category in thresholds:
        if body_fat_pct < upper:
            return score, category
    
    # Fallback
    return 25, 'Very Poor'


def get_body_fat_category(body_fat_pct: float, age: int, sex: str) -> str:
    """Get just the category for body fat percentage."""
    _, category = score_body_fat_pct(body_fat_pct, age, sex)
    return category


# =============================================================================
# LEAN MASS INDEX SCORING (Spec 3.4.3)
# =============================================================================

# LMI thresholds: (lower_bound, score_pct, category)
# Different from body fat - HIGHER is better

LMI_THRESHOLDS = {
    'male': [
        (20, 100, 'Excellent'),
        (18, 85, 'Good'),
        (16, 70, 'Fair'),
        (14, 50, 'Low'),
        (0, 25, 'Sarcopenia'),  # Below 14
    ],
    'female': [
        (17, 100, 'Excellent'),
        (15, 85, 'Good'),
        (13, 70, 'Fair'),
        (11, 50, 'Low'),
        (0, 25, 'Sarcopenia'),  # Below 11
    ]
}


def score_lmi(lmi: float, sex: str) -> Tuple[int, str]:
    """
    Score Lean Mass Index.
    
    Args:
        lmi: Lean Mass Index (kg/m²)
        sex: 'male' or 'female'
        
    Returns:
        Tuple of (score percentage 0-100, category string)
    """
    if sex not in ('male', 'female'):
        return 0, 'Unknown'
    
    thresholds = LMI_THRESHOLDS[sex]
    
    # LMI is HIGHER = better, so we find the first threshold that LMI is >= to
    for lower, score, category in thresholds:
        if lmi >= lower:
            return score, category
    
    # Below all thresholds
    return 25, 'Sarcopenia'


def get_lmi_category(lmi: float, sex: str) -> str:
    """Get just the category for LMI."""
    _, category = score_lmi(lmi, sex)
    return category


# =============================================================================
# VISCERAL FAT SCORING (Spec 3.4.4)
# =============================================================================

# VFA thresholds in cm² (DEXA)
VFA_THRESHOLDS = [
    (100, 100, 'Low Risk'),
    (130, 85, 'Borderline'),
    (160, 70, 'Elevated'),
    (200, 50, 'High'),
    (float('inf'), 25, 'Very High'),
]

# BIA visceral fat level (proprietary 1-30 scale)
VFA_BIA_THRESHOLDS = [
    (10, 100, 'Healthy'),
    (15, 70, 'Elevated'),
    (float('inf'), 40, 'High'),
]


def score_visceral_fat(
    vfa_cm2: Optional[float] = None,
    bia_level: Optional[int] = None
) -> Tuple[int, str]:
    """
    Score visceral fat.
    
    Args:
        vfa_cm2: Visceral fat area in cm² (from DEXA)
        bia_level: BIA visceral fat level (1-30 scale)
        
    Returns:
        Tuple of (score percentage 0-100, category string)
    """
    # Prefer DEXA measurement
    if vfa_cm2 is not None:
        for upper, score, category in VFA_THRESHOLDS:
            if vfa_cm2 < upper:
                return score, category
        return 25, 'Very High'
    
    # Fall back to BIA level
    if bia_level is not None:
        for upper, score, category in VFA_BIA_THRESHOLDS:
            if bia_level < upper:
                return score, category
        return 40, 'High'
    
    return 0, 'Unknown'


# =============================================================================
# FAT DISTRIBUTION SCORING (Spec 3.4.5)
# =============================================================================

# Android/Gynoid ratio thresholds
AG_RATIO_THRESHOLDS = {
    'male': [
        (0.90, 100, 'Excellent'),
        (1.00, 85, 'Good'),
        (1.10, 70, 'Fair'),
        (1.20, 50, 'Poor'),
        (float('inf'), 25, 'Very Poor'),
    ],
    'female': [
        (0.70, 100, 'Excellent'),
        (0.80, 85, 'Good'),
        (0.90, 70, 'Fair'),
        (1.00, 50, 'Poor'),
        (float('inf'), 25, 'Very Poor'),
    ]
}

# Waist-to-Hip Ratio thresholds
WHR_THRESHOLDS = {
    'male': [
        (0.85, 100, 'Excellent'),
        (0.90, 85, 'Good'),
        (0.95, 70, 'Fair'),
        (1.00, 50, 'High Risk'),
        (float('inf'), 25, 'Very High Risk'),
    ],
    'female': [
        (0.75, 100, 'Excellent'),
        (0.80, 85, 'Good'),
        (0.85, 70, 'Fair'),
        (0.90, 50, 'High Risk'),
        (float('inf'), 25, 'Very High Risk'),
    ]
}


def score_fat_distribution_ag_ratio(ag_ratio: float, sex: str) -> Tuple[int, str]:
    """
    Score fat distribution using Android/Gynoid ratio (from DEXA).
    
    Args:
        ag_ratio: Android/Gynoid fat ratio
        sex: 'male' or 'female'
        
    Returns:
        Tuple of (score percentage 0-100, category string)
    """
    if sex not in ('male', 'female'):
        return 0, 'Unknown'
    
    thresholds = AG_RATIO_THRESHOLDS[sex]
    
    for upper, score, category in thresholds:
        if ag_ratio < upper:
            return score, category
    
    return 25, 'Very Poor'


def score_fat_distribution_whr(whr: float, sex: str) -> Tuple[int, str]:
    """
    Score fat distribution using Waist-to-Hip Ratio.
    
    Args:
        whr: Waist-to-hip ratio
        sex: 'male' or 'female'
        
    Returns:
        Tuple of (score percentage 0-100, category string)
    """
    if sex not in ('male', 'female'):
        return 0, 'Unknown'
    
    thresholds = WHR_THRESHOLDS[sex]
    
    for upper, score, category in thresholds:
        if whr < upper:
            return score, category
    
    return 25, 'Very High Risk'


# =============================================================================
# SARCOPENIA ASSESSMENT
# =============================================================================

# EWGSOP2 cutoffs
SARCOPENIA_LMI_CUTOFFS = {
    'male': 14,     # LMI < 14 kg/m²
    'female': 11,   # LMI < 11 kg/m²
}

SARCOPENIA_ASMI_CUTOFFS = {
    'male': 7.0,    # ASMI < 7.0 kg/m²
    'female': 5.4,  # ASMI < 5.4 kg/m²
}


def assess_sarcopenia_risk(
    sex: str,
    lmi: Optional[float] = None,
    asmi: Optional[float] = None
) -> Tuple[bool, str]:
    """
    Assess sarcopenia risk based on muscle mass.
    
    Per EWGSOP2 criteria, sarcopenia is probable with low muscle mass.
    
    Args:
        sex: 'male' or 'female'
        lmi: Lean Mass Index (kg/m²), optional
        asmi: Appendicular Skeletal Muscle Mass Index (kg/m²), optional
        
    Returns:
        Tuple of (is_at_risk: bool, reason: str)
    """
    if sex not in ('male', 'female'):
        return False, 'Unknown sex'
    
    # Prefer ASMI if available (more specific for sarcopenia)
    if asmi is not None:
        cutoff = SARCOPENIA_ASMI_CUTOFFS[sex]
        if asmi < cutoff:
            return True, f'ASMI {asmi:.1f} < {cutoff} kg/m² (EWGSOP2 cutoff)'
        return False, f'ASMI {asmi:.1f} ≥ {cutoff} kg/m² (normal)'
    
    # Fall back to LMI
    if lmi is not None:
        cutoff = SARCOPENIA_LMI_CUTOFFS[sex]
        if lmi < cutoff:
            return True, f'LMI {lmi:.1f} < {cutoff} kg/m² (low muscle mass)'
        return False, f'LMI {lmi:.1f} ≥ {cutoff} kg/m² (normal)'
    
    return False, 'Insufficient data'


# =============================================================================
# BONE DENSITY (T-SCORE) CATEGORIES
# =============================================================================

def get_bone_density_category(t_score: float) -> str:
    """
    Get bone density category from T-score.
    
    Per WHO criteria:
    - T-score ≥ -1.0: Normal
    - T-score -1.0 to -2.5: Osteopenia
    - T-score ≤ -2.5: Osteoporosis
    
    Args:
        t_score: Bone mineral density T-score
        
    Returns:
        Category string
    """
    if t_score >= -1.0:
        return 'Normal'
    elif t_score > -2.5:
        return 'Osteopenia'
    else:
        return 'Osteoporosis'
