"""
Pillar 3 Scoring - Metabolic & Digestive Health
================================================

Scoring functions for all 5 test components.
Total: 20 points maximum
"""

from typing import Dict, Any


# =============================================================================
# TEST 1: GLUCOSE METABOLISM & ENERGY (5 points)
# =============================================================================

def score_glucose_exact(glucose: float, hba1c: float) -> Dict[str, Any]:
    """
    Score glucose control from exact values.
    Uses worse (more conservative) score from glucose vs HbA1c.
    
    Args:
        glucose: Fasting glucose in mg/dL
        hba1c: HbA1c percentage
        
    Returns:
        Dict with points, category, and clinical notes
    """
    # Score fasting glucose
    if glucose < 100:
        glucose_score = 3.0
        glucose_cat = "Optimal"
    elif glucose < 110:
        glucose_score = 2.5
        glucose_cat = "Borderline"
    elif glucose < 126:
        glucose_score = 1.5
        glucose_cat = "Pre-diabetic"
    elif glucose < 151:
        glucose_score = 1.0
        glucose_cat = "Diabetic - Controlled"
    else:
        glucose_score = 0.0
        glucose_cat = "Diabetic - Poor Control"
    
    # Score HbA1c
    if hba1c < 5.7:
        hba1c_score = 3.0
        hba1c_cat = "Optimal"
    elif hba1c < 6.1:
        hba1c_score = 2.5
        hba1c_cat = "Borderline"
    elif hba1c < 6.5:
        hba1c_score = 1.5
        hba1c_cat = "Pre-diabetic"
    elif hba1c < 7.6:
        hba1c_score = 1.0
        hba1c_cat = "Diabetic - Controlled"
    else:
        hba1c_score = 0.0
        hba1c_cat = "Diabetic - Poor Control"
    
    # Use worse (lower) score - more conservative
    final_score = min(glucose_score, hba1c_score)
    
    # Determine category from worse metric
    if glucose_score <= hba1c_score:
        category = glucose_cat
    else:
        category = hba1c_cat
    
    # Cap at maximum 3.0 points
    capped_score = min(final_score, 3.0)
    
    return {
        'points': capped_score,
        'category': category,
        'glucose_score': glucose_score,
        'hba1c_score': hba1c_score,
    }


def score_glucose_category(category: str) -> Dict[str, Any]:
    """Score glucose control from category selection."""
    scoring = {
        'optimal': (3.0, 'Optimal'),
        'borderline': (2.5, 'Borderline'),
        'prediabetic': (1.5, 'Pre-diabetic'),
        'diabetic_controlled': (1.0, 'Diabetic - Controlled'),
        'diabetic_poor': (0.0, 'Diabetic - Poor Control'),
    }
    
    points, cat = scoring.get(category, (0.0, 'Unknown'))
    
    # Cap at maximum 3.0 points
    capped_points = min(points, 3.0)
    
    return {
        'points': capped_points,
        'category': cat,
    }


def score_post_meal_feeling(feeling: str) -> Dict[str, Any]:
    """Score post-meal energy feeling (1 point max)."""
    scoring = {
        'energized': (1.0, 'Optimal glucose regulation'),
        'comfortable': (0.75, 'Good'),
        'tired': (0.5, 'Possible reactive hypoglycemia'),
        'coma': (0.0, 'Poor glucose regulation'),
    }
    
    points, note = scoring.get(feeling, (0.0, 'Unknown'))
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


def score_fasting_tolerance(tolerance: str) -> Dict[str, Any]:
    """Score ability to tolerate fasting (1 point max)."""
    scoring = {
        'fine': (1.0, 'Good metabolic flexibility'),
        'hungry': (0.75, 'Acceptable'),
        'difficult': (0.25, 'Hypoglycemia concern'),
        'cannot': (0.0, 'Severe glucose dysregulation'),
    }
    
    points, note = scoring.get(tolerance, (0.0, 'Unknown'))
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


# =============================================================================
# TEST 2: DIGESTIVE FUNCTION (6 points)
# =============================================================================

def score_bowel_frequency(frequency: str) -> Dict[str, Any]:
    """Score bowel movement frequency (2 points max)."""
    scoring = {
        '1-2daily': (2.0, 'Optimal'),
        'oncedaily': (2.0, 'Optimal'),
        '3-4daily': (1.5, 'Frequent - may indicate loose stools'),
        '2-3days': (1.0, 'Mild constipation'),
        '5plus': (0.5, 'Very frequent - diarrhea/IBS concern'),
        'weekly': (0.0, 'Severe constipation'),
    }
    
    points, note = scoring.get(frequency, (0.0, 'Unknown'))
    
    # Cap at maximum 2.0 points
    capped_points = min(points, 2.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


def score_stool_consistency(consistency: str) -> Dict[str, Any]:
    """Score stool consistency using Bristol Stool Scale (1 point max)."""
    scoring = {
        'normal': (1.0, 'Healthy (Type 3-4)'),
        'slightly': (0.5, 'Minor concern (Type 2 or 5)'),
        'abnormal': (0.0, 'Constipation or diarrhea (Type 1, 6, 7)'),
    }
    
    points, note = scoring.get(consistency, (0.0, 'Unknown'))
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


def score_reflux_frequency(frequency: str) -> Dict[str, Any]:
    """Score heartburn/acid reflux frequency (2 points max)."""
    scoring = {
        'never': (2.0, 'No GERD'),
        'occasional': (1.5, 'Mild'),
        'frequent': (0.75, 'GERD likely'),
        'daily': (0.0, 'Chronic GERD'),
    }
    
    points, note = scoring.get(frequency, (0.0, 'Unknown'))
    
    # Cap at maximum 2.0 points
    capped_points = min(points, 2.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


def score_meal_comfort(comfort: str) -> Dict[str, Any]:
    """Score post-meal comfort (1 point max)."""
    scoring = {
        'comfortable': (1.0, 'Good digestion'),
        'mild': (0.75, 'Minor issue'),
        'bloated': (0.25, 'Digestive concern'),
        'significant': (0.0, 'Digestive disorder'),
    }
    
    points, note = scoring.get(comfort, (0.0, 'Unknown'))
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


# =============================================================================
# TEST 3: GUT SYMPTOMS (4 points)
# =============================================================================

def score_bloating_frequency(frequency: str) -> Dict[str, Any]:
    """Score bloating/gas frequency (2 points max)."""
    scoring = {
        'rarely': (2.0, 'No issue'),
        'occasional': (1.5, 'Minor'),
        'frequent': (0.5, 'IBS/SIBO concern'),
        'daily': (0.0, 'Chronic issue'),
    }
    
    points, note = scoring.get(frequency, (0.0, 'Unknown'))
    
    # Cap at maximum 2.0 points
    capped_points = min(points, 2.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


def score_abdominal_pain(frequency: str) -> Dict[str, Any]:
    """Score abdominal pain/cramping frequency (1 point max)."""
    scoring = {
        'no': (1.0, 'No concern'),
        'rarely': (0.75, 'Minimal'),
        'occasional': (0.5, 'Monitor'),
        'frequent': (0.0, 'IBS/IBD concern'),
    }
    
    points, note = scoring.get(frequency, (0.0, 'Unknown'))
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


def score_food_intolerances(intolerances: str) -> Dict[str, Any]:
    """Score number of food intolerances (1 point max)."""
    scoring = {
        'none': (1.0, 'No intolerances'),
        'few': (0.75, 'Common (lactose, etc.)'),
        'several': (0.5, 'Multiple sensitivities'),
        'many': (0.0, 'Severe restrictions'),
    }
    
    points, note = scoring.get(intolerances, (0.0, 'Unknown'))
    
    # Cap at maximum 1.0 point
    capped_points = min(points, 1.0)
    
    return {
        'points': capped_points,
        'clinical_note': note,
    }


# =============================================================================
# TEST 4: LIVER FUNCTION (3 points)
# =============================================================================

def score_liver_exact(alt: float, ast: float, sex: str) -> Dict[str, Any]:
    """
    Score liver function from exact ALT and AST values.
    Uses worse (more conservative) score.
    Sex-adjusted thresholds.
    
    Args:
        alt: ALT value in U/L
        ast: AST value in U/L
        sex: 'male' or 'female'
        
    Returns:
        Dict with points, category, and scores for each enzyme
    """
    if sex.lower() == 'male':
        # Male thresholds
        if alt < 30:
            alt_score = 3.0
            alt_cat = "Optimal"
        elif alt <= 40:
            alt_score = 2.5
            alt_cat = "Normal"
        elif alt <= 60:
            alt_score = 1.5
            alt_cat = "Mildly Elevated"
        elif alt <= 90:
            alt_score = 0.5
            alt_cat = "Moderately Elevated"
        else:
            alt_score = 0.0
            alt_cat = "Severely Elevated"
        
        # AST scoring (same thresholds for males)
        if ast < 30:
            ast_score = 3.0
        elif ast <= 40:
            ast_score = 2.5
        elif ast <= 60:
            ast_score = 1.5
        elif ast <= 90:
            ast_score = 0.5
        else:
            ast_score = 0.0
    else:
        # Female thresholds (lower)
        if alt < 25:
            alt_score = 3.0
            alt_cat = "Optimal"
        elif alt <= 35:
            alt_score = 2.5
            alt_cat = "Normal"
        elif alt <= 50:
            alt_score = 1.5
            alt_cat = "Mildly Elevated"
        elif alt <= 75:
            alt_score = 0.5
            alt_cat = "Moderately Elevated"
        else:
            alt_score = 0.0
            alt_cat = "Severely Elevated"
        
        # AST scoring (same thresholds for females)
        if ast < 25:
            ast_score = 3.0
        elif ast <= 35:
            ast_score = 2.5
        elif ast <= 50:
            ast_score = 1.5
        elif ast <= 75:
            ast_score = 0.5
        else:
            ast_score = 0.0
    
    # Use worse (lower) score - more conservative
    final_score = min(alt_score, ast_score)
    
    # Determine category from ALT (primary liver enzyme)
    category = alt_cat
    
    # Cap at maximum 3.0 points
    capped_score = min(final_score, 3.0)
    
    return {
        'points': capped_score,
        'category': category,
        'alt_score': alt_score,
        'ast_score': ast_score,
    }


def score_liver_category(category: str) -> Dict[str, Any]:
    """Score liver function from category selection."""
    scoring = {
        'optimal': (3.0, 'Optimal'),
        'normal': (2.5, 'Normal'),
        'mild': (1.5, 'Mildly Elevated'),
        'moderate': (0.5, 'Moderately Elevated'),
        'severe': (0.0, 'Severely Elevated'),
    }
    
    points, cat = scoring.get(category, (0.0, 'Unknown'))
    
    # Cap at maximum 3.0 points
    capped_points = min(points, 3.0)
    
    return {
        'points': capped_points,
        'category': cat,
    }


# =============================================================================
# TEST 5: METABOLIC INFLAMMATION (2 points)
# =============================================================================

def score_crp_exact(crp: float) -> Dict[str, Any]:
    """
    Score hs-CRP from exact value.
    Cardiovascular disease risk stratification.
    
    Args:
        crp: hs-CRP value in mg/L
        
    Returns:
        Dict with points, risk level, and clinical note
    """
    if crp < 1.0:
        score = 2.0
        risk = "Low Risk"
        note = "Minimal inflammation"
    elif crp < 2.0:
        score = 1.5
        risk = "Moderate Risk"
        note = "Moderate cardiovascular risk"
    elif crp < 3.0:
        score = 1.0
        risk = "Moderate-High Risk"
        note = "Elevated cardiovascular risk"
    elif crp <= 10.0:
        score = 0.5
        risk = "High Risk"
        note = "Significant inflammation"
    else:
        score = 0.0
        risk = "Very High/Acute Inflammation"
        note = "Acute inflammation or infection"
    
    # Cap at maximum 2.0 points
    capped_score = min(score, 2.0)
    
    return {
        'points': capped_score,
        'risk_level': risk,
        'clinical_note': note,
    }


def score_crp_category(category: str) -> Dict[str, Any]:
    """Score hs-CRP from category selection."""
    scoring = {
        'low': (2.0, 'Low Risk'),
        'average': (1.25, 'Average Risk'),
        'high': (0.5, 'High Risk'),
        'very_high': (0.0, 'Very High/Acute'),
    }
    
    points, risk = scoring.get(category, (0.0, 'Unknown'))
    
    # Cap at maximum 2.0 points
    capped_points = min(points, 2.0)
    
    return {
        'points': capped_points,
        'risk_level': risk,
    }
