"""
Pillar 1 Calculators - Movement & Strength
===========================================

Calculation functions for all 8 physical performance tests.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any
import math


# =============================================================================
# TEST 1: 30-SECOND CHAIR STAND
# =============================================================================

def calculate_chair_stand_metrics(reps: int) -> Dict[str, Any]:
    """
    Calculate metrics from chair stand test.
    
    Args:
        reps: Number of complete stands in 30 seconds
        
    Returns:
        Dict with reps and derived metrics
    """
    return {
        'reps': reps,
        'reps_per_minute': reps * 2,  # Extrapolated
    }


# =============================================================================
# TEST 2: GRIP STRENGTH
# =============================================================================

def calculate_grip_best(trials: list[Optional[float]]) -> Optional[float]:
    """
    Get best grip strength from trials.
    
    Args:
        trials: List of grip strength measurements (kg)
        
    Returns:
        Best (maximum) value from valid trials
    """
    valid_trials = [t for t in trials if t is not None and t > 0]
    if not valid_trials:
        return None
    return max(valid_trials)


def calculate_grip_asymmetry(left_best: float, right_best: float) -> Dict[str, Any]:
    """
    Calculate asymmetry between hands.
    
    Args:
        left_best: Best left hand grip (kg)
        right_best: Best right hand grip (kg)
        
    Returns:
        Dict with asymmetry metrics
    """
    if left_best <= 0 or right_best <= 0:
        return {'asymmetry_percent': None, 'asymmetry_flag': False}
    
    diff = abs(left_best - right_best)
    max_val = max(left_best, right_best)
    asymmetry_percent = (diff / max_val) * 100
    
    return {
        'asymmetry_percent': round(asymmetry_percent, 1),
        'asymmetry_flag': asymmetry_percent > 10,  # >10% difference is concerning
        'stronger_hand': 'left' if left_best > right_best else 'right',
    }


# =============================================================================
# TEST 3: 4-METER GAIT SPEED
# =============================================================================

def calculate_gait_speed(time_seconds: float, distance_meters: float = 4.0) -> float:
    """
    Calculate gait speed from timed walk.
    
    Args:
        time_seconds: Time to complete walk
        distance_meters: Distance walked (default 4m)
        
    Returns:
        Speed in m/s
    """
    if time_seconds <= 0:
        raise ValueError("Time must be positive")
    
    return round(distance_meters / time_seconds, 2)


def get_faster_gait_trial(trial1_time: float, trial2_time: float) -> Dict[str, Any]:
    """
    Get the faster (lower time) trial and calculate speed.
    
    Args:
        trial1_time: Time for trial 1 (seconds)
        trial2_time: Time for trial 2 (seconds)
        
    Returns:
        Dict with faster time and calculated speed
    """
    faster_time = min(trial1_time, trial2_time)
    speed = calculate_gait_speed(faster_time)
    
    return {
        'faster_time': faster_time,
        'speed_ms': speed,
        'trial_used': 1 if trial1_time <= trial2_time else 2,
    }


# =============================================================================
# TEST 4: BALANCE ASSESSMENT
# =============================================================================

def score_romberg_test(eyes_open_pass: bool, eyes_closed_pass: bool) -> Dict[str, Any]:
    """
    Score Romberg test (standing with feet together).
    
    Args:
        eyes_open_pass: Whether patient passed eyes-open test (30 sec)
        eyes_closed_pass: Whether patient passed eyes-closed test (30 sec)
        
    Returns:
        Dict with score and interpretation
    """
    if eyes_open_pass and eyes_closed_pass:
        return {
            'romberg_score': 1.0,
            'romberg_result': 'normal',
            'interpretation': 'Normal proprioception, vestibular, and cerebellar function',
        }
    elif eyes_open_pass and not eyes_closed_pass:
        return {
            'romberg_score': 0.5,
            'romberg_result': 'positive',
            'interpretation': 'Positive Romberg sign - proprioceptive or sensory deficit',
        }
    else:
        return {
            'romberg_score': 0.0,
            'romberg_result': 'severely_abnormal',
            'interpretation': 'Severe balance impairment - cerebellar or vestibular dysfunction',
        }


def get_worse_single_leg_time(
    non_dominant_best: float,
    dominant_best: float
) -> Dict[str, Any]:
    """
    Get the worse (lower) single-leg stance time for conservative scoring.
    
    Args:
        non_dominant_best: Best time for non-dominant leg (seconds)
        dominant_best: Best time for dominant leg (seconds)
        
    Returns:
        Dict with worse time and leg used
    """
    worse_time = min(non_dominant_best, dominant_best)
    
    return {
        'worse_time': worse_time,
        'leg_used': 'non_dominant' if non_dominant_best <= dominant_best else 'dominant',
        'asymmetry_percent': abs(non_dominant_best - dominant_best) / max(non_dominant_best, dominant_best) * 100 if max(non_dominant_best, dominant_best) > 0 else 0,
    }


# =============================================================================
# TEST 5: TIMED UP AND GO (TUG)
# =============================================================================

def calculate_tug_metrics(
    time_seconds: float,
    unsteady_gait: bool = False,
    unsteady_turn: bool = False,
    used_arms: bool = False,
    plopped_down: bool = False
) -> Dict[str, Any]:
    """
    Calculate TUG metrics with qualitative modifiers.
    
    Args:
        time_seconds: TUG completion time
        unsteady_gait: Whether gait was unsteady
        unsteady_turn: Whether turn was unsteady/paused
        used_arms: Whether patient used arms to push up
        plopped_down: Whether patient sat down poorly
        
    Returns:
        Dict with time and modifier information
    """
    modifiers = []
    modifier_total = 0.0
    
    if unsteady_gait:
        modifiers.append('Unsteady gait (-0.2)')
        modifier_total -= 0.2
    if unsteady_turn:
        modifiers.append('Unsteady turn (-0.2)')
        modifier_total -= 0.2
    if used_arms:
        modifiers.append('Used arms to stand (-0.1)')
        modifier_total -= 0.1
    if plopped_down:
        modifiers.append('Poor sitting control (-0.2)')
        modifier_total -= 0.2
    
    return {
        'time_seconds': time_seconds,
        'modifiers': modifiers,
        'modifier_total': modifier_total,
        'has_qualitative_issues': len(modifiers) > 0,
    }


def get_faster_tug_trial(trial1_time: float, trial2_time: float) -> float:
    """Get faster (lower) TUG time from two trials."""
    return min(trial1_time, trial2_time)


# =============================================================================
# TEST 6: VO2 MAX
# =============================================================================

def estimate_vo2max_bruce_protocol(time_minutes: float, sex: str) -> float:
    """
    Estimate VO2 max from Bruce Protocol treadmill time.
    
    Args:
        time_minutes: Total time on Bruce Protocol (minutes)
        sex: 'male' or 'female'
        
    Returns:
        Estimated VO2 max in mL/kg/min
    """
    # Foster equation for Bruce Protocol
    if sex.lower() == 'male':
        vo2max = 14.76 - (1.379 * time_minutes) + (0.451 * time_minutes**2) - (0.012 * time_minutes**3)
    else:
        vo2max = 4.38 * time_minutes - 3.9
    
    return round(max(vo2max, 0), 1)


def estimate_vo2max_non_exercise(
    age: int,
    sex: str,
    bmi: float,
    resting_hr: int,
    physical_activity_index: int
) -> float:
    """
    Estimate VO2 max using non-exercise prediction equation (Jurca).
    
    Args:
        age: Age in years
        sex: 'male' or 'female'
        bmi: Body mass index (kg/m²)
        resting_hr: Resting heart rate (bpm)
        physical_activity_index: PA-I score (0-7 scale)
        
    Returns:
        Estimated VO2 max in mL/kg/min
        
    Physical Activity Index Scale:
        0: No regular physical activity
        1: Light activity <1x/week
        2: Light activity 1-2x/week, <30 min
        3: Moderate activity 2-3x/week, 30-60 min
        4: Moderate activity 3-4x/week, 30-60 min
        5: Vigorous activity 3-4x/week, 30-60 min
        6: Vigorous activity 5-7x/week, 30-60 min
        7: Very vigorous training >7 hrs/week
    """
    # Jurca equation coefficients (corrected)
    if sex.lower() == 'male':
        vo2max = (
            67.350
            - (0.381 * age)
            - (0.754 * bmi)
            - (0.155 * resting_hr)
            + (1.921 * physical_activity_index)
        )
    else:
        vo2max = (
            56.363
            - (0.381 * age)
            - (0.754 * bmi)
            - (0.155 * resting_hr)
            + (1.921 * physical_activity_index)
        )
    
    return round(max(vo2max, 10), 1)  # Floor at 10 mL/kg/min


def estimate_vo2max_from_6mwt(
    distance_meters: float,
    age: int,
    weight_kg: float,
    height_cm: float,
    sex: str
) -> float:
    """
    Estimate VO2 max from 6-Minute Walk Test distance.
    
    Args:
        distance_meters: Distance walked in 6 minutes
        age: Age in years
        weight_kg: Weight in kg
        height_cm: Height in cm
        sex: 'male' or 'female'
        
    Returns:
        Estimated VO2 max in mL/kg/min
    """
    # Simplified estimation formula
    vo2max = (
        (0.02 * distance_meters)
        - (0.191 * age)
        - (0.07 * weight_kg)
        + (0.09 * height_cm)
        + 2.45
    )
    
    # Add sex adjustment
    if sex.lower() == 'female':
        vo2max -= 2.0
    
    return round(max(vo2max, 10), 1)


def vo2max_to_mets(vo2max: float) -> float:
    """Convert VO2 max to METs."""
    return round(vo2max / 3.5, 1)


# =============================================================================
# TEST 7: SIT-AND-REACH FLEXIBILITY
# =============================================================================

def get_best_flexibility_trial(trials: list[float]) -> float:
    """Get best (highest) sit-and-reach distance from trials."""
    valid = [t for t in trials if t is not None]
    if not valid:
        return 0.0
    return max(valid)


# =============================================================================
# TEST 8: 6-MINUTE WALK TEST
# =============================================================================

def calculate_6mwt_distance(
    laps_completed: int,
    course_length_meters: float,
    partial_lap_meters: float = 0.0
) -> float:
    """
    Calculate total 6MWT distance.
    
    Args:
        laps_completed: Number of complete laps
        course_length_meters: Length of one lap
        partial_lap_meters: Additional distance in partial lap
        
    Returns:
        Total distance in meters
    """
    return (laps_completed * course_length_meters) + partial_lap_meters


def calculate_6mwt_percent_predicted(
    distance_meters: float,
    age: int,
    height_cm: float,
    weight_kg: float,
    sex: str
) -> float:
    """
    Calculate % of predicted 6MWT distance using Enright equations.
    
    Args:
        distance_meters: Actual distance walked
        age: Age in years
        height_cm: Height in cm
        weight_kg: Weight in kg
        sex: 'male' or 'female'
        
    Returns:
        Percent of predicted distance
    """
    # Enright & Sherill equations for predicted distance
    if sex.lower() == 'male':
        predicted = (7.57 * height_cm) - (5.02 * age) - (1.76 * weight_kg) - 309
    else:
        predicted = (2.11 * height_cm) - (2.29 * weight_kg) - (5.78 * age) + 667
    
    if predicted <= 0:
        return 100.0
    
    return round((distance_meters / predicted) * 100, 1)


# =============================================================================
# PILLAR 1 TOTALS
# =============================================================================

def calculate_pillar1_total(
    chair_stand_score: float,
    grip_score: float,
    gait_score: float,
    balance_score: float,
    tug_score: float,
    vo2max_score: float,
    flexibility_score: float,
    walk_6min_score: float,
    balance_bonus: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate Pillar 1 total score.
    
    Args:
        Individual test scores
        balance_bonus: Optional 0.5 bonus for exceptional balance
        
    Returns:
        Dict with total score and breakdown
    """
    # Maximum possible: 20 points (22 with balance bonus)
    total = (
        chair_stand_score +
        grip_score +
        gait_score +
        balance_score +
        tug_score +
        vo2max_score +
        flexibility_score +
        walk_6min_score +
        balance_bonus
    )
    
    max_possible = 20.0 + balance_bonus
    percentage = (total / max_possible) * 100
    
    # Determine category
    if percentage >= 85:
        category = 'Excellent'
    elif percentage >= 70:
        category = 'Very Good'
    elif percentage >= 55:
        category = 'Good'
    elif percentage >= 40:
        category = 'Fair'
    elif percentage >= 25:
        category = 'Below Average'
    else:
        category = 'Poor'
    
    return {
        'total_score': round(total, 2),
        'max_possible': max_possible,
        'percentage': round(percentage, 1),
        'category': category,
        'breakdown': {
            'chair_stand': chair_stand_score,
            'grip_strength': grip_score,
            'gait_speed': gait_score,
            'balance': balance_score + balance_bonus,
            'tug': tug_score,
            'vo2max': vo2max_score,
            'flexibility': flexibility_score,
            '6mwt': walk_6min_score,
        }
    }


def calculate_functional_age_impact(pillar1_total: float, age: int) -> Dict[str, Any]:
    """
    Calculate functional age impact from Pillar 1 score.
    
    Args:
        pillar1_total: Total Pillar 1 score (out of 20)
        age: Chronological age
        
    Returns:
        Dict with functional age impact
    """
    percentage = (pillar1_total / 20.0) * 100
    
    # Functional age modifier based on score
    if percentage >= 85:
        modifier = -4  # Excellent: -4 years
    elif percentage >= 75:
        modifier = -2  # Very Good: -2 years
    elif percentage >= 60:
        modifier = 0   # Good: no change
    elif percentage >= 45:
        modifier = +2  # Fair: +2 years
    elif percentage >= 30:
        modifier = +4  # Below Average: +4 years
    else:
        modifier = +6  # Poor: +6 years
    
    functional_age = age + modifier
    
    return {
        'chronological_age': age,
        'functional_age_modifier': modifier,
        'functional_age': functional_age,
        'interpretation': f"{'+' if modifier > 0 else ''}{modifier} years" if modifier != 0 else "No change",
    }
