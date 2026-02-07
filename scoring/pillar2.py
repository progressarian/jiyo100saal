"""
Pillar 2 Scoring Tables - Cognitive Function
=============================================

Age/sex-adjusted scoring tables for all 11 cognitive test components.
Based on research-validated normative data.

Total: 18 points maximum
- Memory (2+2=4 pts)
- Digit Span (1+1=2 pts)  
- Trail Making (1.5+1.5=3 pts)
- DSST (3 pts)
- Clock Drawing (2 pts)
- Verbal Fluency (2 pts)
- PHQ-2 (1 pt)
- GAD-2 (1 pt)
"""

from decimal import Decimal
from typing import Optional, Dict, Any, Tuple


# Word list for memory tests
MEMORY_WORD_LIST = ['Face', 'Velvet', 'Church', 'Daisy', 'Red', 
                    'Salt', 'Button', 'Cabin', 'Pole', 'Ticket']


# =============================================================================
# TEST 1 & 2: WORD RECALL MEMORY (2 pts each = 4 pts total)
# =============================================================================

MEMORY_RECALL_TABLES = {
    # Age <60
    (0, 59): [
        (9, 10, 2.0, 'Excellent'),
        (7, 8, 1.5, 'Good'),
        (5, 6, 1.0, 'Fair'),
        (3, 4, 0.5, 'Poor'),
        (0, 2, 0.0, 'Very Poor'),
    ],
    # Age 60-79
    (60, 79): [
        (8, 10, 2.0, 'Excellent'),
        (6, 7, 1.5, 'Good'),
        (4, 5, 1.0, 'Fair'),
        (2, 3, 0.5, 'Poor'),
        (0, 1, 0.0, 'Very Poor'),
    ],
    # Age 80+
    (80, 120): [
        (7, 10, 2.0, 'Excellent'),
        (5, 6, 1.5, 'Good'),
        (3, 4, 1.0, 'Fair'),
        (1, 2, 0.5, 'Poor'),
        (0, 0, 0.0, 'Very Poor'),
    ],
}


def score_memory_recall(words_recalled: int, age: int) -> Dict[str, Any]:
    """
    Score immediate or delayed word recall test.
    
    Args:
        words_recalled: Number of words correctly recalled (0-10)
        age: Patient age in years
        
    Returns:
        Dict with points, category, and clinical notes
    """
    # Find appropriate age range
    age_table = None
    for (min_age, max_age), table in MEMORY_RECALL_TABLES.items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = MEMORY_RECALL_TABLES[(0, 59)]
    
    for min_words, max_words, points, category in age_table:
        if min_words <= words_recalled <= max_words:
            # Cap at maximum 2.0 points
            capped_points = min(points, 2.0)
            result = {
                'points': capped_points,
                'category': category,
                'words_recalled': words_recalled,
            }
            
            if category in ('Poor', 'Very Poor'):
                result['alert'] = 'Memory concern - consider formal evaluation'
            
            return result
    
    return {'points': 0.0, 'category': 'Very Poor', 'words_recalled': words_recalled}


def calculate_retention_rate(immediate: int, delayed: int) -> Dict[str, Any]:
    """
    Calculate memory retention rate.
    
    Args:
        immediate: Words recalled immediately
        delayed: Words recalled after delay
        
    Returns:
        Dict with rate and clinical interpretation
    """
    if immediate <= 0:
        return {'rate': None, 'interpretation': 'Cannot calculate - no immediate recall'}
    
    rate = (delayed / immediate) * 100
    
    result = {
        'rate': round(rate, 1),
        'immediate': immediate,
        'delayed': delayed,
    }
    
    if rate >= 80:
        result['interpretation'] = 'Normal retention'
        result['level'] = 'normal'
    elif rate >= 50:
        result['interpretation'] = 'Mild retention difficulty'
        result['level'] = 'mild'
    else:
        result['interpretation'] = 'Significant retention difficulty - hippocampal concern'
        result['level'] = 'severe'
        result['flag'] = True
        result['alert'] = 'LOW RETENTION - Consider neurological evaluation'
    
    return result


# =============================================================================
# TEST 3 & 4: DIGIT SPAN (1 pt each = 2 pts total)
# =============================================================================

DIGIT_SPAN_FORWARD_TABLE = [
    (8, 15, 1.0, 'Excellent'),
    (7, 7, 0.8, 'Good'),
    (6, 6, 0.6, 'Fair'),
    (5, 5, 0.4, 'Below Average'),
    (4, 4, 0.2, 'Poor'),
    (0, 3, 0.0, 'Very Poor'),
]

DIGIT_SPAN_BACKWARD_TABLE = [
    (7, 12, 1.0, 'Excellent'),
    (6, 6, 0.8, 'Good'),
    (5, 5, 0.6, 'Fair'),
    (4, 4, 0.4, 'Below Average'),
    (3, 3, 0.2, 'Poor'),
    (0, 2, 0.0, 'Very Poor'),
]


def score_digit_span_forward(forward: int) -> Dict[str, Any]:
    """Score digit span forward (1 pt max)."""
    for min_span, max_span, points, category in DIGIT_SPAN_FORWARD_TABLE:
        if min_span <= forward <= max_span:
            # Cap at maximum 1.0 point
            capped_points = min(points, 1.0)
            return {
                'points': capped_points,
                'category': category,
                'forward': forward,
            }
    return {'points': 0.0, 'category': 'Very Poor', 'forward': forward}


def score_digit_span_backward(backward: int) -> Dict[str, Any]:
    """Score digit span backward (1 pt max)."""
    for min_span, max_span, points, category in DIGIT_SPAN_BACKWARD_TABLE:
        if min_span <= backward <= max_span:
            # Cap at maximum 1.0 point
            capped_points = min(points, 1.0)
            return {
                'points': capped_points,
                'category': category,
                'backward': backward,
            }
    return {'points': 0.0, 'category': 'Very Poor', 'backward': backward}


def score_digit_span(forward: int, backward: int, age: int) -> Dict[str, Any]:
    """
    Score combined digit span (for backward compatibility).
    Returns total of forward + backward points.
    """
    fwd_result = score_digit_span_forward(forward)
    bwd_result = score_digit_span_backward(backward)
    
    total_points = fwd_result['points'] + bwd_result['points']
    total = forward + backward
    
    # Determine overall category
    if total_points >= 1.6:
        category = 'Excellent'
    elif total_points >= 1.2:
        category = 'Good'
    elif total_points >= 0.8:
        category = 'Fair'
    elif total_points >= 0.4:
        category = 'Below Average'
    else:
        category = 'Poor'
    
    result = {
        'points': total_points,
        'forward_points': fwd_result['points'],
        'backward_points': bwd_result['points'],
        'category': category,
        'forward': forward,
        'backward': backward,
        'total': total,
    }
    
    if total < 10:
        result['alert'] = 'Working memory deficit - Total digit span <10'
    
    return result


# =============================================================================
# TEST 5 & 6: TRAIL MAKING TESTS (1.5 pts each = 3 pts total)
# =============================================================================

TRAILS_A_TABLES = {
    (18, 49): [
        (0, 24, 3.0, 'Excellent'),
        (25, 32, 2.5, 'Good'),
        (33, 40, 2.0, 'Fair'),
        (41, 55, 1.5, 'Below Average'),
        (56, 80, 1.0, 'Poor'),
        (81, float('inf'), 0.5, 'Very Poor'),
    ],
    (50, 59): [
        (0, 28, 3.0, 'Excellent'),
        (29, 36, 2.5, 'Good'),
        (37, 45, 2.0, 'Fair'),
        (46, 60, 1.5, 'Below Average'),
        (61, 90, 1.0, 'Poor'),
        (91, float('inf'), 0.5, 'Very Poor'),
    ],
    (60, 69): [
        (0, 32, 3.0, 'Excellent'),
        (33, 42, 2.5, 'Good'),
        (43, 52, 2.0, 'Fair'),
        (53, 70, 1.5, 'Below Average'),
        (71, 100, 1.0, 'Poor'),
        (101, float('inf'), 0.5, 'Very Poor'),
    ],
    (70, 79): [
        (0, 40, 3.0, 'Excellent'),
        (41, 52, 2.5, 'Good'),
        (53, 65, 2.0, 'Fair'),
        (66, 85, 1.5, 'Below Average'),
        (86, 120, 1.0, 'Poor'),
        (121, float('inf'), 0.5, 'Very Poor'),
    ],
    (80, 120): [
        (0, 50, 3.0, 'Excellent'),
        (51, 65, 2.5, 'Good'),
        (66, 80, 2.0, 'Fair'),
        (81, 105, 1.5, 'Below Average'),
        (106, 150, 1.0, 'Poor'),
        (151, float('inf'), 0.5, 'Very Poor'),
    ],
}

TRAILS_B_TABLES = {
    (18, 49): [
        (0, 55, 3.0, 'Excellent'),
        (56, 75, 2.5, 'Good'),
        (76, 95, 2.0, 'Fair'),
        (96, 120, 1.5, 'Below Average'),
        (121, 160, 1.0, 'Poor'),
        (161, float('inf'), 0.5, 'Very Poor'),
    ],
    (50, 59): [
        (0, 65, 3.0, 'Excellent'),
        (66, 85, 2.5, 'Good'),
        (86, 110, 2.0, 'Fair'),
        (111, 140, 1.5, 'Below Average'),
        (141, 190, 1.0, 'Poor'),
        (191, float('inf'), 0.5, 'Very Poor'),
    ],
    (60, 69): [
        (0, 75, 3.0, 'Excellent'),
        (76, 100, 2.5, 'Good'),
        (101, 130, 2.0, 'Fair'),
        (131, 165, 1.5, 'Below Average'),
        (166, 220, 1.0, 'Poor'),
        (221, float('inf'), 0.5, 'Very Poor'),
    ],
    (70, 79): [
        (0, 95, 3.0, 'Excellent'),
        (96, 130, 2.5, 'Good'),
        (131, 170, 2.0, 'Fair'),
        (171, 220, 1.5, 'Below Average'),
        (221, 300, 1.0, 'Poor'),
        (301, float('inf'), 0.5, 'Very Poor'),
    ],
    (80, 120): [
        (0, 115, 3.0, 'Excellent'),
        (116, 160, 2.5, 'Good'),
        (161, 210, 2.0, 'Fair'),
        (211, 280, 1.5, 'Below Average'),
        (281, 380, 1.0, 'Poor'),
        (381, float('inf'), 0.5, 'Very Poor'),
    ],
}


def score_trails_a(time_seconds: float, age: int) -> Dict[str, Any]:
    """Score Trail Making Test A (1.5 pts max)."""
    age_table = None
    for (min_age, max_age), table in TRAILS_A_TABLES.items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = TRAILS_A_TABLES[(18, 49)]
    
    time_int = int(time_seconds)
    for min_time, max_time, points, category in age_table:
        if min_time <= time_int <= max_time:
            # Cap at maximum 1.5 points for Trail A
            capped_points = min(points, 1.5)
            result = {
                'points': capped_points,
                'category': category,
                'time_seconds': time_seconds,
            }
            if category in ('Poor', 'Very Poor'):
                result['alert'] = 'Slow processing speed on Trails A'
            return result
    
    return {'points': 0.5, 'category': 'Very Poor', 'time_seconds': time_seconds}


def score_trails_b(time_seconds: float, age: int) -> Dict[str, Any]:
    """Score Trail Making Test B (1.5 pts max)."""
    age_table = None
    for (min_age, max_age), table in TRAILS_B_TABLES.items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = TRAILS_B_TABLES[(18, 49)]
    
    time_int = int(time_seconds)
    for min_time, max_time, points, category in age_table:
        if min_time <= time_int <= max_time:
            # Cap at maximum 1.5 points for Trail B
            capped_points = min(points, 1.5)
            result = {
                'points': capped_points,
                'category': category,
                'time_seconds': time_seconds,
            }
            if category in ('Poor', 'Very Poor'):
                result['alert'] = 'Executive function concern - Slow Trails B'
            return result
    
    return {'points': 0.5, 'category': 'Very Poor', 'time_seconds': time_seconds}


def calculate_trails_ba_ratio(trails_a_time: float, trails_b_time: float) -> Dict[str, Any]:
    """Calculate B/A ratio for executive control assessment."""
    if trails_a_time <= 0:
        return {'ratio': None, 'interpretation': 'Cannot calculate'}
    
    ratio = trails_b_time / trails_a_time
    
    result = {'ratio': round(ratio, 2)}
    
    if ratio <= 2.0:
        result['interpretation'] = 'Normal'
        result['level'] = 'normal'
    elif ratio <= 3.0:
        result['interpretation'] = 'Mildly elevated'
        result['level'] = 'mild'
    elif ratio <= 3.5:
        result['interpretation'] = 'Moderately elevated - possible executive dysfunction'
        result['level'] = 'moderate'
    else:
        result['interpretation'] = 'Significantly elevated - likely executive dysfunction'
        result['level'] = 'severe'
        result['alert'] = 'HIGH B/A RATIO - Executive dysfunction indicated'
    
    return result


# =============================================================================
# TEST 7: DSST (3 points max)
# =============================================================================

DSST_TABLES = {
    'male': {
        (18, 29): [(70, float('inf'), 3.0, 'Excellent'), (60, 69, 2.5, 'Good'), (50, 59, 2.0, 'Fair'), (40, 49, 1.5, 'Below Average'), (30, 39, 1.0, 'Poor'), (0, 29, 0.5, 'Very Poor')],
        (30, 39): [(65, float('inf'), 3.0, 'Excellent'), (55, 64, 2.5, 'Good'), (45, 54, 2.0, 'Fair'), (35, 44, 1.5, 'Below Average'), (25, 34, 1.0, 'Poor'), (0, 24, 0.5, 'Very Poor')],
        (40, 49): [(58, float('inf'), 3.0, 'Excellent'), (48, 57, 2.5, 'Good'), (40, 47, 2.0, 'Fair'), (32, 39, 1.5, 'Below Average'), (22, 31, 1.0, 'Poor'), (0, 21, 0.5, 'Very Poor')],
        (50, 59): [(52, float('inf'), 3.0, 'Excellent'), (43, 51, 2.5, 'Good'), (35, 42, 2.0, 'Fair'), (28, 34, 1.5, 'Below Average'), (20, 27, 1.0, 'Poor'), (0, 19, 0.5, 'Very Poor')],
        (60, 69): [(46, float('inf'), 3.0, 'Excellent'), (38, 45, 2.5, 'Good'), (30, 37, 2.0, 'Fair'), (23, 29, 1.5, 'Below Average'), (16, 22, 1.0, 'Poor'), (0, 15, 0.5, 'Very Poor')],
        (70, 79): [(38, float('inf'), 3.0, 'Excellent'), (30, 37, 2.5, 'Good'), (23, 29, 2.0, 'Fair'), (17, 22, 1.5, 'Below Average'), (12, 16, 1.0, 'Poor'), (0, 11, 0.5, 'Very Poor')],
        (80, 120): [(32, float('inf'), 3.0, 'Excellent'), (24, 31, 2.5, 'Good'), (18, 23, 2.0, 'Fair'), (13, 17, 1.5, 'Below Average'), (8, 12, 1.0, 'Poor'), (0, 7, 0.5, 'Very Poor')],
    },
    'female': {
        (18, 29): [(73, float('inf'), 3.0, 'Excellent'), (63, 72, 2.5, 'Good'), (53, 62, 2.0, 'Fair'), (43, 52, 1.5, 'Below Average'), (33, 42, 1.0, 'Poor'), (0, 32, 0.5, 'Very Poor')],
        (30, 39): [(68, float('inf'), 3.0, 'Excellent'), (58, 67, 2.5, 'Good'), (48, 57, 2.0, 'Fair'), (38, 47, 1.5, 'Below Average'), (28, 37, 1.0, 'Poor'), (0, 27, 0.5, 'Very Poor')],
        (40, 49): [(61, float('inf'), 3.0, 'Excellent'), (51, 60, 2.5, 'Good'), (43, 50, 2.0, 'Fair'), (35, 42, 1.5, 'Below Average'), (25, 34, 1.0, 'Poor'), (0, 24, 0.5, 'Very Poor')],
        (50, 59): [(55, float('inf'), 3.0, 'Excellent'), (46, 54, 2.5, 'Good'), (38, 45, 2.0, 'Fair'), (30, 37, 1.5, 'Below Average'), (22, 29, 1.0, 'Poor'), (0, 21, 0.5, 'Very Poor')],
        (60, 69): [(49, float('inf'), 3.0, 'Excellent'), (40, 48, 2.5, 'Good'), (32, 39, 2.0, 'Fair'), (25, 31, 1.5, 'Below Average'), (18, 24, 1.0, 'Poor'), (0, 17, 0.5, 'Very Poor')],
        (70, 79): [(40, float('inf'), 3.0, 'Excellent'), (32, 39, 2.5, 'Good'), (25, 31, 2.0, 'Fair'), (19, 24, 1.5, 'Below Average'), (13, 18, 1.0, 'Poor'), (0, 12, 0.5, 'Very Poor')],
        (80, 120): [(34, float('inf'), 3.0, 'Excellent'), (26, 33, 2.5, 'Good'), (20, 25, 2.0, 'Fair'), (14, 19, 1.5, 'Below Average'), (9, 13, 1.0, 'Poor'), (0, 8, 0.5, 'Very Poor')],
    },
}


def score_dsst(score: int, age: int, sex: str) -> Dict[str, Any]:
    """Score DSST (3 pts max)."""
    sex_key = sex.lower()
    if sex_key not in DSST_TABLES:
        sex_key = 'male'
    
    age_table = None
    for (min_age, max_age), table in DSST_TABLES[sex_key].items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = DSST_TABLES[sex_key][(18, 29)]
    
    for min_score, max_score, points, category in age_table:
        if min_score <= score <= max_score:
            # Cap at maximum 3.0 points
            capped_points = min(points, 3.0)
            result = {
                'points': capped_points,
                'category': category,
                'raw_score': score,
            }
            if category in ('Poor', 'Very Poor'):
                result['alert'] = 'Low processing speed - Consider cognitive evaluation'
            return result
    
    return {'points': 0.5, 'category': 'Very Poor', 'raw_score': score}


# =============================================================================
# TEST 8: CLOCK DRAWING TEST (2 points max)
# =============================================================================

def score_clock_drawing(raw_score: int) -> Dict[str, Any]:
    """
    Score clock drawing test (2 pts max).
    
    Raw score 0-7 based on components:
    - Circle intact
    - All numbers present (1-12)
    - Numbers in correct sequence
    - Numbers in correct spatial position
    - Two hands present
    - Hands show correct time (11:10)
    - Hands in correct proportion (hour shorter)
    
    Args:
        raw_score: Sum of correct components (0-7)
    """
    if raw_score == 7:
        points = 2.0
        category = 'Perfect'
    elif raw_score >= 6:
        points = 1.5
        category = 'Minor Errors'
    elif raw_score >= 4:
        points = 1.0
        category = 'Moderate Errors'
    elif raw_score >= 2:
        points = 0.5
        category = 'Significant Errors'
    else:
        points = 0.0
        category = 'Severe Errors'
    
    # Cap at maximum 2.0 points
    capped_points = min(points, 2.0)
    
    result = {'points': capped_points, 'category': category, 'raw_score': raw_score}
    
    if raw_score >= 2 and raw_score < 4:
        result['alert'] = 'Visuospatial/executive concern'
    elif raw_score < 2:
        result['alert'] = 'Severe visuospatial impairment - urgent evaluation needed'
    
    return result


# =============================================================================
# TEST 9: VERBAL FLUENCY - ANIMALS (2 points max)
# =============================================================================

VERBAL_FLUENCY_TABLES = {
    (18, 49): [(23, float('inf'), 2.0, 'Excellent'), (19, 22, 1.5, 'Good'), (15, 18, 1.0, 'Fair'), (12, 14, 0.5, 'Below Average'), (0, 11, 0.0, 'Poor')],
    (50, 64): [(21, float('inf'), 2.0, 'Excellent'), (17, 20, 1.5, 'Good'), (14, 16, 1.0, 'Fair'), (11, 13, 0.5, 'Below Average'), (0, 10, 0.0, 'Poor')],
    (65, 79): [(19, float('inf'), 2.0, 'Excellent'), (15, 18, 1.5, 'Good'), (12, 14, 1.0, 'Fair'), (10, 11, 0.5, 'Below Average'), (0, 9, 0.0, 'Poor')],
    (80, 120): [(17, float('inf'), 2.0, 'Excellent'), (13, 16, 1.5, 'Good'), (10, 12, 1.0, 'Fair'), (8, 9, 0.5, 'Below Average'), (0, 7, 0.0, 'Poor')],
}


def score_verbal_fluency(animals_count: int, age: int) -> Dict[str, Any]:
    """Score Verbal Fluency Animals (2 pts max)."""
    age_table = None
    for (min_age, max_age), table in VERBAL_FLUENCY_TABLES.items():
        if min_age <= age <= max_age:
            age_table = table
            break
    
    if age_table is None:
        age_table = VERBAL_FLUENCY_TABLES[(18, 49)]
    
    for min_count, max_count, points, category in age_table:
        if min_count <= animals_count <= max_count:
            # Cap at maximum 2.0 points
            capped_points = min(points, 2.0)
            result = {
                'points': capped_points,
                'category': category,
                'animals_count': animals_count,
            }
            if animals_count < 12:
                result['alert'] = 'Low verbal fluency - Language/executive concern'
            return result
    
    return {'points': 0.0, 'category': 'Poor', 'animals_count': animals_count}


# =============================================================================
# TEST 10 & 11: PHQ-2 AND GAD-2 MENTAL HEALTH SCREENS (1 pt each)
# =============================================================================

def score_phq2(total: int) -> Dict[str, Any]:
    """
    Score PHQ-2 depression screen (1 pt max).
    
    Total range: 0-6
    """
    if total <= 1:
        points = 1.0
        category = 'Minimal/None'
    elif total == 2:
        points = 0.7
        category = 'Mild'
    elif total <= 4:
        points = 0.3
        category = 'Moderate'
    else:
        points = 0.0
        category = 'Severe'
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    result = {'points': capped_points, 'category': category, 'total': total}
    
    if total >= 3:
        result['followup_flag'] = True
        if total >= 5:
            result['urgent_flag'] = True
            result['alert'] = 'URGENT: Immediate mental health referral needed'
        else:
            result['alert'] = 'Recommend full PHQ-9 evaluation'
    
    return result


def score_gad2(total: int) -> Dict[str, Any]:
    """
    Score GAD-2 anxiety screen (1 pt max).
    
    Total range: 0-6
    """
    if total <= 1:
        points = 1.0
        category = 'Minimal/None'
    elif total == 2:
        points = 0.7
        category = 'Mild'
    elif total <= 4:
        points = 0.3
        category = 'Moderate'
    else:
        points = 0.0
        category = 'Severe'
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    result = {'points': capped_points, 'category': category, 'total': total}
    
    if total >= 3:
        result['followup_flag'] = True
        if total >= 5:
            result['urgent_flag'] = True
            result['alert'] = 'URGENT: Immediate mental health referral needed'
        else:
            result['alert'] = 'Recommend full GAD-7 evaluation'
    
    return result


# =============================================================================
# COMPOSITE SCORING
# =============================================================================

def get_pillar2_category(total_score: float) -> str:
    """Get overall Pillar 2 category based on total score (out of 18)."""
    percentage = (total_score / 18.0) * 100
    
    if percentage >= 90:
        return 'Excellent'
    elif percentage >= 75:
        return 'Good'
    elif percentage >= 55:
        return 'Fair'
    elif percentage >= 40:
        return 'Below Average'
    else:
        return 'Poor'


def calculate_pillar2_alerts(results: Dict, age: int) -> list[Dict[str, Any]]:
    """Generate comprehensive clinical alerts from all Pillar 2 tests."""
    alerts = []
    
    # Memory retention
    if results.get('memory_retention_flag'):
        alerts.append({
            'type': 'MEMORY_RETENTION',
            'severity': 'HIGH',
            'message': f"Low memory retention ({results.get('memory_retention_pct', 0):.0f}%) - hippocampal concern",
        })
    
    # Multiple cognitive domains affected
    poor_domains = sum(1 for cat in [
        results.get('memory_immediate_category'),
        results.get('dsst_category'),
        results.get('trails_b_category'),
        results.get('digit_span_category'),
        results.get('verbal_fluency_category'),
    ] if cat in ('Poor', 'Very Poor'))
    
    if poor_domains >= 2:
        alerts.append({
            'type': 'MULTIPLE_COGNITIVE_DEFICITS',
            'severity': 'HIGH',
            'message': f'{poor_domains} cognitive domains impaired - neuropsychological evaluation recommended',
        })
    
    # Mental health urgent
    if results.get('phq2_urgent_flag') or results.get('gad2_urgent_flag'):
        alerts.append({
            'type': 'MENTAL_HEALTH_URGENT',
            'severity': 'URGENT',
            'message': 'Immediate mental health evaluation and safety assessment needed',
        })
    
    return alerts
