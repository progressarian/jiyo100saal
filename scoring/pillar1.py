"""
Pillar 1 Scoring Tables - Movement & Strength
==============================================

Age/sex-adjusted scoring tables for all 8 tests.
STRICTER thresholds as per Jiyo100Saal specification.

Total: 20 points maximum (22 with balance bonus)
"""

from decimal import Decimal
from typing import Optional, Dict, Any, Tuple


# =============================================================================
# TEST 1: 30-SECOND CHAIR STAND (3 points max)
# =============================================================================

CHAIR_STAND_TABLES = {
    'male': {
        # Age 30-49
        (30, 49): [
            (25, float('inf'), 3.0, 'Excellent'),
            (22, 24, 2.7, 'Very Good'),
            (19, 21, 2.4, 'Good'),
            (16, 18, 2.0, 'Fair'),
            (13, 15, 1.5, 'Below Average'),
            (10, 12, 1.0, 'Poor'),
            (0, 9, 0.5, 'Very Poor'),
        ],
        # Age 50-64
        (50, 64): [
            (22, float('inf'), 3.0, 'Excellent'),
            (19, 21, 2.7, 'Very Good'),
            (16, 18, 2.4, 'Good'),
            (14, 15, 2.0, 'Fair'),
            (11, 13, 1.5, 'Below Average'),
            (8, 10, 1.0, 'Poor'),
            (0, 7, 0.5, 'Very Poor'),
        ],
        # Age 65-79
        (65, 79): [
            (19, float('inf'), 3.0, 'Excellent'),
            (16, 18, 2.7, 'Very Good'),
            (14, 15, 2.4, 'Good'),
            (12, 13, 2.0, 'Fair'),
            (10, 11, 1.5, 'Below Average'),
            (7, 9, 1.0, 'Poor'),
            (0, 6, 0.5, 'Very Poor'),
        ],
        # Age 80+
        (80, 120): [
            (15, float('inf'), 3.0, 'Excellent'),
            (13, 14, 2.7, 'Very Good'),
            (11, 12, 2.4, 'Good'),
            (9, 10, 2.0, 'Fair'),
            (7, 8, 1.5, 'Below Average'),
            (5, 6, 1.0, 'Poor'),
            (0, 4, 0.5, 'Very Poor'),
        ],
    },
    'female': {
        # Age 30-49
        (30, 49): [
            (22, float('inf'), 3.0, 'Excellent'),
            (19, 21, 2.7, 'Very Good'),
            (17, 18, 2.4, 'Good'),
            (14, 16, 2.0, 'Fair'),
            (11, 13, 1.5, 'Below Average'),
            (8, 10, 1.0, 'Poor'),
            (0, 7, 0.5, 'Very Poor'),
        ],
        # Age 50-64
        (50, 64): [
            (19, float('inf'), 3.0, 'Excellent'),
            (16, 18, 2.7, 'Very Good'),
            (14, 15, 2.4, 'Good'),
            (12, 13, 2.0, 'Fair'),
            (9, 11, 1.5, 'Below Average'),
            (7, 8, 1.0, 'Poor'),
            (0, 6, 0.5, 'Very Poor'),
        ],
        # Age 65-79
        (65, 79): [
            (16, float('inf'), 3.0, 'Excellent'),
            (14, 15, 2.7, 'Very Good'),
            (12, 13, 2.4, 'Good'),
            (10, 11, 2.0, 'Fair'),
            (8, 9, 1.5, 'Below Average'),
            (6, 7, 1.0, 'Poor'),
            (0, 5, 0.5, 'Very Poor'),
        ],
        # Age 80+
        (80, 120): [
            (13, float('inf'), 3.0, 'Excellent'),
            (11, 12, 2.7, 'Very Good'),
            (9, 10, 2.4, 'Good'),
            (7, 8, 2.0, 'Fair'),
            (5, 6, 1.5, 'Below Average'),
            (4, 5, 1.0, 'Poor'),
            (0, 3, 0.5, 'Very Poor'),
        ],
    },
}


def score_chair_stand(reps: int, age: int, sex: str) -> Dict[str, Any]:
    """
    Score 30-second chair stand test.
    
    Args:
        reps: Number of complete stands in 30 seconds
        age: Patient age in years
        sex: 'male' or 'female'
        
    Returns:
        Dict with score, category, and clinical notes
    """
    sex_key = sex.lower()
    if sex_key not in CHAIR_STAND_TABLES:
        raise ValueError(f"Invalid sex: {sex}")
    
    # Find appropriate age range
    age_table = None
    for (min_age, max_age), table in CHAIR_STAND_TABLES[sex_key].items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        # Default to youngest if under 30
        age_table = CHAIR_STAND_TABLES[sex_key][(30, 49)]
    
    # Find score based on reps
    for min_reps, max_reps, points, category in age_table:
        if min_reps <= reps <= max_reps:
            result = {
                'score': points,
                'category': category,
                'reps': reps,
                'age_group': f"{age} years",
            }
            
            # Add clinical alerts
            if reps < 10 and age < 65:
                result['alert'] = 'HIGH FALL RISK - Severely limited lower body strength'
            elif reps < 8 and age >= 65:
                result['alert'] = 'HIGH FALL RISK - Consider PT referral'
            
            return result
    
    # Fallback
    return {'score': 0.5, 'category': 'Very Poor', 'reps': reps}


# =============================================================================
# TEST 2: GRIP STRENGTH (3 points max)
# =============================================================================

GRIP_STRENGTH_TABLES = {
    'male': {
        # Age 30-49
        (30, 49): [
            (50, float('inf'), 3.0, 'Excellent'),
            (45, 49.9, 2.7, 'Very Good'),
            (40, 44.9, 2.4, 'Good'),
            (35, 39.9, 2.0, 'Fair'),
            (30, 34.9, 1.5, 'Below Average'),
            (27, 29.9, 1.0, 'Poor'),
            (0, 26.9, 0.5, 'Very Poor / Sarcopenia'),
        ],
        # Age 50-64
        (50, 64): [
            (45, float('inf'), 3.0, 'Excellent'),
            (41, 44.9, 2.7, 'Very Good'),
            (37, 40.9, 2.4, 'Good'),
            (33, 36.9, 2.0, 'Fair'),
            (29, 32.9, 1.5, 'Below Average'),
            (27, 28.9, 1.0, 'Poor'),
            (0, 26.9, 0.5, 'Very Poor / Sarcopenia'),
        ],
        # Age 65-79
        (65, 79): [
            (40, float('inf'), 3.0, 'Excellent'),
            (36, 39.9, 2.7, 'Very Good'),
            (32, 35.9, 2.4, 'Good'),
            (29, 31.9, 2.0, 'Fair'),
            (27, 28.9, 1.5, 'Below Average'),
            (0, 26.9, 0.5, 'Poor / Sarcopenia'),
        ],
        # Age 80+
        (80, 120): [
            (35, float('inf'), 3.0, 'Excellent'),
            (31, 34.9, 2.7, 'Very Good'),
            (27, 30.9, 2.4, 'Good'),
            (0, 26.9, 1.5, 'Fair / Sarcopenia'),
        ],
    },
    'female': {
        # Age 30-49
        (30, 49): [
            (32, float('inf'), 3.0, 'Excellent'),
            (28, 31.9, 2.7, 'Very Good'),
            (24, 27.9, 2.4, 'Good'),
            (20, 23.9, 2.0, 'Fair'),
            (16, 19.9, 1.5, 'Below Average'),
            (0, 15.9, 0.5, 'Poor / Sarcopenia'),
        ],
        # Age 50-64
        (50, 64): [
            (28, float('inf'), 3.0, 'Excellent'),
            (25, 27.9, 2.7, 'Very Good'),
            (21, 24.9, 2.4, 'Good'),
            (18, 20.9, 2.0, 'Fair'),
            (16, 17.9, 1.5, 'Below Average'),
            (0, 15.9, 0.5, 'Poor / Sarcopenia'),
        ],
        # Age 65-79
        (65, 79): [
            (24, float('inf'), 3.0, 'Excellent'),
            (21, 23.9, 2.7, 'Very Good'),
            (18, 20.9, 2.4, 'Good'),
            (16, 17.9, 2.0, 'Fair'),
            (0, 15.9, 1.0, 'Poor / Sarcopenia'),
        ],
        # Age 80+
        (80, 120): [
            (20, float('inf'), 3.0, 'Excellent'),
            (17, 19.9, 2.7, 'Very Good'),
            (16, 16.9, 2.4, 'Good'),
            (0, 15.9, 1.5, 'Fair / Sarcopenia'),
        ],
    },
}

# Sarcopenia cutoffs (EWGSOP2)
SARCOPENIA_CUTOFFS = {
    'male': 27.0,
    'female': 16.0,
}


def score_grip_strength(grip_kg: float, age: int, sex: str) -> Dict[str, Any]:
    """
    Score grip strength test.
    
    Args:
        grip_kg: Dominant hand best grip in kg
        age: Patient age in years
        sex: 'male' or 'female'
        
    Returns:
        Dict with score, category, and clinical notes
    """
    sex_key = sex.lower()
    if sex_key not in GRIP_STRENGTH_TABLES:
        raise ValueError(f"Invalid sex: {sex}")
    
    # Find appropriate age range
    age_table = None
    for (min_age, max_age), table in GRIP_STRENGTH_TABLES[sex_key].items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = GRIP_STRENGTH_TABLES[sex_key][(30, 49)]
    
    # Find score based on grip strength
    for min_grip, max_grip, points, category in age_table:
        if min_grip <= grip_kg <= max_grip:
            result = {
                'score': points,
                'category': category,
                'grip_kg': grip_kg,
            }
            
            # Check sarcopenia cutoff
            sarcopenia_cutoff = SARCOPENIA_CUTOFFS[sex_key]
            if grip_kg < sarcopenia_cutoff:
                result['sarcopenia_flag'] = True
                result['alert'] = f'SARCOPENIA WARNING - Grip strength below {sarcopenia_cutoff} kg'
            else:
                result['sarcopenia_flag'] = False
            
            return result
    
    return {'score': 0.5, 'category': 'Very Poor', 'grip_kg': grip_kg, 'sarcopenia_flag': True}


# =============================================================================
# TEST 3: GAIT SPEED (2 points max)
# =============================================================================

GAIT_SPEED_TABLE = [
    # (min_speed, max_speed, points, category, clinical_significance)
    (1.3, float('inf'), 2.0, 'Excellent', 'Low risk, excellent mobility'),
    (1.1, 1.29, 1.8, 'Good', 'Good functional status'),
    (1.0, 1.09, 1.5, 'Fair', 'Average for age'),
    (0.8, 0.99, 1.2, 'Below Average', 'Mild limitation'),
    (0.6, 0.79, 0.8, 'Poor', 'High risk of disability'),
    (0, 0.59, 0.3, 'Very Poor', 'Severe mobility limitation'),
]


def score_gait_speed(speed_ms: float, age: int) -> Dict[str, Any]:
    """
    Score 4-meter gait speed test.
    
    Args:
        speed_ms: Gait speed in m/s
        age: Patient age (for clinical context)
        
    Returns:
        Dict with score, category, and clinical notes
    """
    for min_speed, max_speed, points, category, significance in GAIT_SPEED_TABLE:
        if min_speed <= speed_ms <= max_speed:
            result = {
                'score': points,
                'category': category,
                'speed_ms': speed_ms,
                'clinical_significance': significance,
            }
            
            # Clinical alerts for elderly
            if age >= 65:
                if speed_ms < 0.6:
                    result['alert'] = 'SEVERE MOBILITY LIMITATION - Very high mortality risk'
                elif speed_ms < 0.8:
                    result['fall_risk'] = 'HIGH'
                    result['alert'] = 'HIGH FALL RISK - May need assistive device'
            
            return result
    
    return {'score': 0.3, 'category': 'Very Poor', 'speed_ms': speed_ms}


# =============================================================================
# TEST 4: BALANCE ASSESSMENT (3 points max: 1 Romberg + 2 Single-leg)
# =============================================================================

SINGLE_LEG_STANCE_TABLES = {
    # Age 30-49
    (30, 49): [
        (40, float('inf'), 2.0, 'Excellent'),
        (30, 39, 1.7, 'Good'),
        (20, 29, 1.4, 'Fair'),
        (10, 19, 1.0, 'Below Average'),
        (5, 9, 0.5, 'Poor'),
        (0, 4, 0.2, 'Very Poor'),
    ],
    # Age 50-64
    (50, 64): [
        (30, float('inf'), 2.0, 'Excellent'),
        (20, 29, 1.7, 'Good'),
        (15, 19, 1.4, 'Fair'),
        (8, 14, 1.0, 'Below Average'),
        (4, 7, 0.5, 'Poor'),
        (0, 3, 0.2, 'Very Poor'),
    ],
    # Age 65-79
    (65, 79): [
        (20, float('inf'), 2.0, 'Excellent'),
        (12, 19, 1.7, 'Good'),
        (8, 11, 1.4, 'Fair'),
        (5, 7, 1.0, 'Below Average'),
        (3, 4, 0.5, 'Poor'),
        (0, 2, 0.2, 'Very Poor'),
    ],
    # Age 80+
    (80, 120): [
        (10, float('inf'), 2.0, 'Excellent'),
        (6, 9, 1.7, 'Good'),
        (4, 5, 1.4, 'Fair'),
        (2, 3, 1.0, 'Below Average'),
        (0, 1, 0.3, 'Poor'),
    ],
}


def score_balance(
    romberg_eyes_open: bool,
    romberg_eyes_closed: bool,
    single_leg_time: float,
    age: int
) -> Dict[str, Any]:
    """
    Score combined balance assessment.
    
    Args:
        romberg_eyes_open: Pass/fail for eyes open
        romberg_eyes_closed: Pass/fail for eyes closed
        single_leg_time: Worse leg time in seconds
        age: Patient age
        
    Returns:
        Dict with total balance score and breakdown
    """
    # Romberg scoring (1 point max)
    if romberg_eyes_open and romberg_eyes_closed:
        romberg_score = 1.0
        romberg_result = 'Normal'
    elif romberg_eyes_open:
        romberg_score = 0.5
        romberg_result = 'Positive Romberg (proprioceptive deficit)'
    else:
        romberg_score = 0.0
        romberg_result = 'Severely abnormal'
    
    # Single-leg stance scoring (2 points max)
    age_table = None
    for (min_age, max_age), table in SINGLE_LEG_STANCE_TABLES.items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = SINGLE_LEG_STANCE_TABLES[(30, 49)]
    
    single_leg_score = 0.2
    single_leg_category = 'Very Poor'
    
    for min_time, max_time, points, category in age_table:
        if min_time <= single_leg_time <= max_time:
            single_leg_score = points
            single_leg_category = category
            break
    
    total_score = romberg_score + single_leg_score
    
    result = {
        'total_score': total_score,
        'romberg_score': romberg_score,
        'romberg_result': romberg_result,
        'single_leg_score': single_leg_score,
        'single_leg_category': single_leg_category,
        'single_leg_time': single_leg_time,
    }
    
    # Fall risk alerts
    if age >= 65 and single_leg_time < 5:
        result['alert'] = 'HIGH FALL RISK - Single-leg stance <5 seconds'
        result['fall_risk'] = 'HIGH'
    elif single_leg_time < 3:
        result['alert'] = 'SEVERE BALANCE IMPAIRMENT'
        result['fall_risk'] = 'VERY HIGH'
    
    return result


# =============================================================================
# TEST 5: TIMED UP AND GO (2 points max)
# =============================================================================

TUG_TABLE = [
    # (min_time, max_time, base_points, category, clinical_significance)
    (0, 9.9, 2.0, 'Excellent', 'Fully independent, low risk'),
    (10, 11.9, 1.9, 'Very Good', 'Independent, minimal risk'),
    (12, 13.9, 1.7, 'Good', 'Independent, normal risk'),
    (14, 19.9, 1.4, 'Fair', 'Mild difficulty, monitor'),
    (20, 29.9, 1.0, 'Below Average', 'Moderate limitation, fall risk'),
    (30, float('inf'), 0.5, 'Poor', 'Severe limitation, high risk'),
]


def score_tug(
    time_seconds: float,
    age: int,
    unsteady_gait: bool = False,
    unsteady_turn: bool = False,
    used_arms: bool = False,
    plopped_down: bool = False
) -> Dict[str, Any]:
    """
    Score Timed Up and Go test with qualitative modifiers.
    
    Args:
        time_seconds: TUG completion time
        age: Patient age
        unsteady_gait: Gait was unsteady (-0.2)
        unsteady_turn: Turn was unsteady/paused (-0.2)
        used_arms: Used arms to push up (-0.1)
        plopped_down: Poor sitting control (-0.2)
        
    Returns:
        Dict with score and clinical notes
    """
    # Find base score
    base_points = 0.5
    category = 'Poor'
    significance = 'Severe limitation'
    
    for min_time, max_time, points, cat, sig in TUG_TABLE:
        if min_time <= time_seconds <= max_time:
            base_points = points
            category = cat
            significance = sig
            break
    
    # Apply qualitative modifiers
    modifier_total = 0.0
    modifiers = []
    
    if unsteady_gait:
        modifier_total -= 0.2
        modifiers.append('Unsteady gait (-0.2)')
    if unsteady_turn:
        modifier_total -= 0.2
        modifiers.append('Unsteady turn (-0.2)')
    if used_arms:
        modifier_total -= 0.1
        modifiers.append('Used arms to stand (-0.1)')
    if plopped_down:
        modifier_total -= 0.2
        modifiers.append('Poor sitting control (-0.2)')
    
    final_score = max(0, base_points + modifier_total)
    
    result = {
        'score': round(final_score, 2),
        'base_score': base_points,
        'modifier': modifier_total,
        'modifiers_applied': modifiers,
        'category': category,
        'time_seconds': time_seconds,
        'clinical_significance': significance,
    }
    
    # Fall risk stratification for age 65+
    if age >= 65:
        if time_seconds >= 30:
            result['fall_risk'] = 'VERY HIGH'
            result['alert'] = 'URGENT INTERVENTION NEEDED'
        elif time_seconds >= 20:
            result['fall_risk'] = 'HIGH'
            result['alert'] = 'PT referral, assistive device consideration'
        elif time_seconds >= 12 or modifiers:
            result['fall_risk'] = 'MODERATE'
    
    return result


# =============================================================================
# TEST 6: VO2 MAX (4 points max)
# =============================================================================

VO2MAX_TABLES = {
    'male': {
        # Age 30-49
        (30, 49): [
            (50, float('inf'), 4.0, 'Superior', '>90th percentile'),
            (45, 49.9, 3.7, 'Excellent', '75-90th percentile'),
            (40, 44.9, 3.3, 'Good', '50-74th percentile'),
            (35, 39.9, 2.7, 'Fair', '25-49th percentile'),
            (30, 34.9, 2.0, 'Below Average', '10-24th percentile'),
            (25, 29.9, 1.3, 'Poor', '<10th percentile'),
            (0, 24.9, 0.7, 'Very Poor', 'Very low'),
        ],
        # Age 50-64
        (50, 64): [
            (45, float('inf'), 4.0, 'Superior', '>90th percentile'),
            (40, 44.9, 3.7, 'Excellent', '75-90th percentile'),
            (35, 39.9, 3.3, 'Good', '50-74th percentile'),
            (30, 34.9, 2.7, 'Fair', '25-49th percentile'),
            (25, 29.9, 2.0, 'Below Average', '10-24th percentile'),
            (20, 24.9, 1.3, 'Poor', '<10th percentile'),
            (0, 19.9, 0.7, 'Very Poor', 'Very low - high mortality risk'),
        ],
        # Age 65+
        (65, 120): [
            (37, float('inf'), 4.0, 'Superior', '>90th percentile'),
            (32, 36.9, 3.7, 'Excellent', '75-90th percentile'),
            (28, 31.9, 3.3, 'Good', '50-74th percentile'),
            (24, 27.9, 2.7, 'Fair', '25-49th percentile'),
            (20, 23.9, 2.0, 'Below Average', '10-24th percentile'),
            (0, 19.9, 1.0, 'Poor', '<10th percentile - high mortality risk'),
        ],
    },
    'female': {
        # Age 30-49
        (30, 49): [
            (45, float('inf'), 4.0, 'Superior', '>90th percentile'),
            (40, 44.9, 3.7, 'Excellent', '75-90th percentile'),
            (35, 39.9, 3.3, 'Good', '50-74th percentile'),
            (30, 34.9, 2.7, 'Fair', '25-49th percentile'),
            (25, 29.9, 2.0, 'Below Average', '10-24th percentile'),
            (20, 24.9, 1.3, 'Poor', '<10th percentile'),
            (0, 19.9, 0.7, 'Very Poor', 'Very low'),
        ],
        # Age 50-64
        (50, 64): [
            (40, float('inf'), 4.0, 'Superior', '>90th percentile'),
            (35, 39.9, 3.7, 'Excellent', '75-90th percentile'),
            (30, 34.9, 3.3, 'Good', '50-74th percentile'),
            (25, 29.9, 2.7, 'Fair', '25-49th percentile'),
            (22, 24.9, 2.0, 'Below Average', '10-24th percentile'),
            (18, 21.9, 1.3, 'Poor', '<10th percentile'),
            (0, 17.9, 0.7, 'Very Poor', 'Very low - high mortality risk'),
        ],
        # Age 65+
        (65, 120): [
            (32, float('inf'), 4.0, 'Superior', '>90th percentile'),
            (28, 31.9, 3.7, 'Excellent', '75-90th percentile'),
            (24, 27.9, 3.3, 'Good', '50-74th percentile'),
            (20, 23.9, 2.7, 'Fair', '25-49th percentile'),
            (18, 19.9, 2.0, 'Below Average', '10-24th percentile'),
            (0, 17.9, 1.0, 'Poor', '<10th percentile - high mortality risk'),
        ],
    },
}


def score_vo2max(vo2max: float, age: int, sex: str) -> Dict[str, Any]:
    """
    Score VO2 Max.
    
    Args:
        vo2max: VO2 max in mL/kg/min
        age: Patient age
        sex: 'male' or 'female'
        
    Returns:
        Dict with score and clinical notes
    """
    sex_key = sex.lower()
    if sex_key not in VO2MAX_TABLES:
        raise ValueError(f"Invalid sex: {sex}")
    
    # Find appropriate age range
    age_table = None
    for (min_age, max_age), table in VO2MAX_TABLES[sex_key].items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = VO2MAX_TABLES[sex_key][(30, 49)]
    
    # Find score
    for min_vo2, max_vo2, points, category, percentile in age_table:
        if min_vo2 <= vo2max <= max_vo2:
            result = {
                'score': points,
                'category': category,
                'percentile': percentile,
                'vo2max': vo2max,
                'mets': round(vo2max / 3.5, 1),
            }
            
            # Clinical alerts
            if vo2max < 20:
                result['alert'] = 'VERY LOW VO2 MAX - High mortality risk, medical evaluation needed'
            
            return result
    
    return {'score': 0.7, 'category': 'Very Poor', 'vo2max': vo2max}


# =============================================================================
# TEST 7: SIT-AND-REACH FLEXIBILITY (2 points max)
# =============================================================================

FLEXIBILITY_TABLES = {
    'male': {
        # Age 30-49
        (30, 49): [
            (15, float('inf'), 2.0, 'Excellent'),
            (10, 14.9, 1.8, 'Good'),
            (5, 9.9, 1.5, 'Fair'),
            (0, 4.9, 1.2, 'Below Average'),
            (-5, -0.1, 0.8, 'Poor'),
            (-10, -5.1, 0.5, 'Very Poor'),
            (float('-inf'), -10.1, 0.2, 'Extremely Limited'),
        ],
        # Age 50-64
        (50, 64): [
            (10, float('inf'), 2.0, 'Excellent'),
            (5, 9.9, 1.8, 'Good'),
            (0, 4.9, 1.5, 'Fair'),
            (-5, -0.1, 1.2, 'Below Average'),
            (-10, -5.1, 0.8, 'Poor'),
            (float('-inf'), -10.1, 0.5, 'Very Poor'),
        ],
        # Age 65+
        (65, 120): [
            (5, float('inf'), 2.0, 'Excellent'),
            (0, 4.9, 1.8, 'Good'),
            (-5, -0.1, 1.5, 'Fair'),
            (-10, -5.1, 1.2, 'Below Average'),
            (float('-inf'), -10.1, 0.8, 'Poor'),
        ],
    },
    'female': {
        # Age 30-49
        (30, 49): [
            (18, float('inf'), 2.0, 'Excellent'),
            (13, 17.9, 1.8, 'Good'),
            (8, 12.9, 1.5, 'Fair'),
            (3, 7.9, 1.2, 'Below Average'),
            (-2, 2.9, 0.8, 'Poor'),
            (-7, -2.1, 0.5, 'Very Poor'),
            (float('-inf'), -7.1, 0.2, 'Extremely Limited'),
        ],
        # Age 50-64
        (50, 64): [
            (13, float('inf'), 2.0, 'Excellent'),
            (8, 12.9, 1.8, 'Good'),
            (3, 7.9, 1.5, 'Fair'),
            (-2, 2.9, 1.2, 'Below Average'),
            (-7, -2.1, 0.8, 'Poor'),
            (float('-inf'), -7.1, 0.5, 'Very Poor'),
        ],
        # Age 65+
        (65, 120): [
            (8, float('inf'), 2.0, 'Excellent'),
            (3, 7.9, 1.8, 'Good'),
            (-2, 2.9, 1.5, 'Fair'),
            (-7, -2.1, 1.2, 'Below Average'),
            (float('-inf'), -7.1, 0.8, 'Poor'),
        ],
    },
}


def score_flexibility(distance_cm: float, age: int, sex: str) -> Dict[str, Any]:
    """
    Score sit-and-reach flexibility test.
    
    Args:
        distance_cm: Distance reached in cm (can be negative)
        age: Patient age
        sex: 'male' or 'female'
        
    Returns:
        Dict with score and clinical notes
    """
    sex_key = sex.lower()
    if sex_key not in FLEXIBILITY_TABLES:
        raise ValueError(f"Invalid sex: {sex}")
    
    # Find appropriate age range
    age_table = None
    for (min_age, max_age), table in FLEXIBILITY_TABLES[sex_key].items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = FLEXIBILITY_TABLES[sex_key][(30, 49)]
    
    # Find score
    for min_dist, max_dist, points, category in age_table:
        if min_dist <= distance_cm <= max_dist:
            return {
                'score': points,
                'category': category,
                'distance_cm': distance_cm,
            }
    
    return {'score': 0.2, 'category': 'Extremely Limited', 'distance_cm': distance_cm}


# =============================================================================
# TEST 8: 6-MINUTE WALK TEST (3 points max)
# =============================================================================

WALK_6MIN_TABLES = {
    'male': {
        # Age 30-49
        (30, 49): [
            (700, float('inf'), 3.0, 'Excellent'),
            (650, 699, 2.7, 'Very Good'),
            (600, 649, 2.4, 'Good'),
            (550, 599, 2.0, 'Fair'),
            (500, 549, 1.5, 'Below Average'),
            (450, 499, 1.0, 'Poor'),
            (0, 449, 0.5, 'Very Poor'),
        ],
        # Age 50-64
        (50, 64): [
            (650, float('inf'), 3.0, 'Excellent'),
            (600, 649, 2.7, 'Very Good'),
            (550, 599, 2.4, 'Good'),
            (500, 549, 2.0, 'Fair'),
            (450, 499, 1.5, 'Below Average'),
            (400, 449, 1.0, 'Poor'),
            (0, 399, 0.5, 'Very Poor'),
        ],
        # Age 65-79
        (65, 79): [
            (600, float('inf'), 3.0, 'Excellent'),
            (550, 599, 2.7, 'Very Good'),
            (500, 549, 2.4, 'Good'),
            (450, 499, 2.0, 'Fair'),
            (400, 449, 1.5, 'Below Average'),
            (350, 399, 1.0, 'Poor'),
            (0, 349, 0.5, 'Very Poor'),
        ],
        # Age 80+
        (80, 120): [
            (500, float('inf'), 3.0, 'Excellent'),
            (450, 499, 2.7, 'Very Good'),
            (400, 449, 2.4, 'Good'),
            (350, 399, 2.0, 'Fair'),
            (300, 349, 1.5, 'Below Average'),
            (0, 299, 0.8, 'Poor'),
        ],
    },
    'female': {
        # Age 30-49
        (30, 49): [
            (650, float('inf'), 3.0, 'Excellent'),
            (600, 649, 2.7, 'Very Good'),
            (550, 599, 2.4, 'Good'),
            (500, 549, 2.0, 'Fair'),
            (450, 499, 1.5, 'Below Average'),
            (400, 449, 1.0, 'Poor'),
            (0, 399, 0.5, 'Very Poor'),
        ],
        # Age 50-64
        (50, 64): [
            (600, float('inf'), 3.0, 'Excellent'),
            (550, 599, 2.7, 'Very Good'),
            (500, 549, 2.4, 'Good'),
            (450, 499, 2.0, 'Fair'),
            (400, 449, 1.5, 'Below Average'),
            (350, 399, 1.0, 'Poor'),
            (0, 349, 0.5, 'Very Poor'),
        ],
        # Age 65-79
        (65, 79): [
            (550, float('inf'), 3.0, 'Excellent'),
            (500, 549, 2.7, 'Very Good'),
            (450, 499, 2.4, 'Good'),
            (400, 449, 2.0, 'Fair'),
            (350, 399, 1.5, 'Below Average'),
            (300, 349, 1.0, 'Poor'),
            (0, 299, 0.5, 'Very Poor'),
        ],
        # Age 80+
        (80, 120): [
            (450, float('inf'), 3.0, 'Excellent'),
            (400, 449, 2.7, 'Very Good'),
            (350, 399, 2.4, 'Good'),
            (300, 349, 2.0, 'Fair'),
            (250, 299, 1.5, 'Below Average'),
            (0, 249, 0.8, 'Poor'),
        ],
    },
}


def score_6mwt(distance_meters: float, age: int, sex: str) -> Dict[str, Any]:
    """
    Score 6-Minute Walk Test.
    
    Args:
        distance_meters: Distance walked in 6 minutes
        age: Patient age
        sex: 'male' or 'female'
        
    Returns:
        Dict with score and clinical notes
    """
    sex_key = sex.lower()
    if sex_key not in WALK_6MIN_TABLES:
        raise ValueError(f"Invalid sex: {sex}")
    
    # Find appropriate age range
    age_table = None
    for (min_age, max_age), table in WALK_6MIN_TABLES[sex_key].items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = WALK_6MIN_TABLES[sex_key][(30, 49)]
    
    # Find score
    for min_dist, max_dist, points, category in age_table:
        if min_dist <= distance_meters <= max_dist:
            result = {
                'score': points,
                'category': category,
                'distance_meters': distance_meters,
            }
            
            # Clinical alerts for elderly
            if age >= 65:
                if distance_meters < 300:
                    result['alert'] = 'VERY HIGH MORTALITY RISK - Distance <300m'
                elif distance_meters < 400:
                    result['alert'] = 'HIGH MORTALITY RISK - Significant functional limitation'
            
            return result
    
    return {'score': 0.5, 'category': 'Very Poor', 'distance_meters': distance_meters}


# =============================================================================
# COMPOSITE SCORING & CLINICAL ALERTS
# =============================================================================

def calculate_pillar1_alerts(
    grip_result: Dict,
    gait_result: Dict,
    balance_result: Dict,
    tug_result: Dict,
    vo2max_result: Dict,
    chair_result: Dict,
    age: int,
    sex: str
) -> list[Dict[str, Any]]:
    """
    Generate comprehensive clinical alerts from all Pillar 1 tests.
    
    Returns:
        List of alert dictionaries with severity and recommendations
    """
    alerts = []
    
    # HIGH FALL RISK composite
    fall_risk_factors = 0
    if gait_result.get('speed_ms', 1.0) < 0.8:
        fall_risk_factors += 1
    if balance_result.get('single_leg_time', 30) < 5:
        fall_risk_factors += 1
    if tug_result.get('time_seconds', 10) > 20:
        fall_risk_factors += 1
    
    if fall_risk_factors >= 2:
        alerts.append({
            'type': 'HIGH_FALL_RISK',
            'severity': 'URGENT',
            'message': 'HIGH FALL RISK - Multiple deficits detected',
            'factors': [
                'Gait speed <0.8 m/s' if gait_result.get('speed_ms', 1.0) < 0.8 else None,
                'Single-leg stance <5 sec' if balance_result.get('single_leg_time', 30) < 5 else None,
                'TUG >20 seconds' if tug_result.get('time_seconds', 10) > 20 else None,
            ],
            'recommendations': [
                'Physical therapy referral',
                'Home safety assessment',
                'Consider assistive device',
                'Fall prevention education',
            ],
        })
    
    # Sarcopenia
    if grip_result.get('sarcopenia_flag'):
        alerts.append({
            'type': 'SARCOPENIA_WARNING',
            'severity': 'HIGH',
            'message': f"Low muscle strength (Grip <{SARCOPENIA_CUTOFFS[sex.lower()]} kg)",
            'recommendations': [
                'Resistance training program',
                'Protein supplementation (1.6-2.0 g/kg/day)',
                'Consider creatine monohydrate',
                'Check vitamin D, testosterone levels',
            ],
        })
    
    # Very low VO2 max
    if vo2max_result.get('vo2max', 40) < 20:
        alerts.append({
            'type': 'VERY_LOW_VO2MAX',
            'severity': 'HIGH',
            'message': 'Very low cardiovascular fitness - High mortality risk',
            'recommendations': [
                'Medical evaluation before exercise',
                'Cardiac stress test recommended',
                'Supervised exercise program',
                'Start with very low intensity',
            ],
        })
    
    # Severe functional limitation (chair stands)
    if chair_result.get('reps', 20) < 8 and age < 70:
        alerts.append({
            'type': 'SEVERE_FUNCTIONAL_LIMITATION',
            'severity': 'MODERATE',
            'message': 'Severely limited lower body strength for age',
            'recommendations': [
                'Physical therapy evaluation',
                'Structured leg strengthening program',
                'Daily chair stand practice',
            ],
        })
    
    return [a for a in alerts if a]  # Remove None entries


def get_pillar1_category(total_score: float) -> str:
    """
    Get overall Pillar 1 category based on total score.
    
    Args:
        total_score: Total Pillar 1 score (out of 20)
        
    Returns:
        Category string
    """
    percentage = (total_score / 20.0) * 100
    
    if percentage >= 85:
        return 'Excellent'
    elif percentage >= 70:
        return 'Very Good'
    elif percentage >= 55:
        return 'Good'
    elif percentage >= 40:
        return 'Fair'
    elif percentage >= 25:
        return 'Below Average'
    else:
        return 'Poor'
