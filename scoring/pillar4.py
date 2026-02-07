"""
Pillar 4 Scoring Functions - Vitality & Hormones
=================================================

9 scoring functions for Pillar 4 tests:
1. Thyroid Function (4 pts) - dual input mode
2. Sex Hormones (4 pts) - sex-specific, age-adjusted for males
3. Sexual Health (1 pt) - sex-specific
4. Vitamin D (2 pts) - dual input mode
5. Hemoglobin & Iron (2 pts) - sex-adjusted, dual input mode
6. Exercise Habits (2 pts)
7. Sleep Duration & Quality (3 pts)
8. Skin & Hair Health (1 pt)
9. Stress & Overwhelm (1 pt)

All scoring functions enforce maximum caps.
"""

from decimal import Decimal
from typing import Tuple, Optional


# ==============================================================================
# TEST 1: THYROID FUNCTION (4 POINTS)
# ==============================================================================

def score_thyroid_exact(tsh: float, free_t4: Optional[float] = None, 
                       free_t3: Optional[float] = None) -> Tuple[Decimal, str]:
    """
    Score thyroid function from exact lab values.
    TSH is primary marker. T4/T3 provide refinement.
    
    Args:
        tsh: TSH value (mIU/L)
        free_t4: Free T4 value (ng/dL) - optional
        free_t3: Free T3 value (pg/mL) - optional
    
    Returns:
        (score, category) - max 4.0 points
    """
    # TSH scoring (primary)
    if 0.5 <= tsh <= 2.0:
        tsh_score = 4.0
        category = "Optimal"
    elif 2.1 <= tsh <= 2.5:
        tsh_score = 3.5
        category = "Very Good"
    elif 2.6 <= tsh <= 4.5:
        tsh_score = 3.0
        category = "Acceptable"
    elif (0.4 <= tsh < 0.5) or (4.5 < tsh <= 10.0):
        tsh_score = 1.5
        category = "Subclinical Dysfunction"
    else:
        tsh_score = 0.0
        category = "Clinical Dysfunction"
    
    # Free T4 scoring (optimal: 1.0-1.5 ng/dL)
    t4_score = None
    if free_t4:
        if 1.0 <= free_t4 <= 1.5:
            t4_score = 4.0
        elif 0.8 <= free_t4 < 1.0 or 1.5 < free_t4 <= 1.8:
            t4_score = 3.0
        else:
            t4_score = 1.5
    
    # Free T3 scoring (optimal: 3.0-4.0 pg/mL)
    t3_score = None
    if free_t3:
        if 3.0 <= free_t3 <= 4.0:
            t3_score = 4.0
        elif 2.5 <= free_t3 < 3.0 or 4.0 < free_t3 <= 4.5:
            t3_score = 3.0
        else:
            t3_score = 1.5
    
    # Combined scoring
    if t4_score is not None and t3_score is not None:
        # All three tested - use weighted average toward worst
        final_score = min(tsh_score, (tsh_score + t4_score + t3_score) / 3)
        if final_score == 4.0:
            category = "Optimal - All markers"
    elif tsh_score:
        # TSH only - cap at 3.5
        final_score = min(tsh_score, 3.5)
        if final_score >= 3.5:
            category = "Good (TSH only)"
    else:
        final_score = tsh_score
    
    return Decimal(str(round(min(final_score, 4.0), 1))), category


def score_thyroid_category(tsh_category: str, t3_t4_status: str = 'notTested') -> Tuple[Decimal, str]:
    """
    Score thyroid function from category selection.
    
    Args:
        tsh_category: TSH category (optimal/veryGood/acceptable/subclinical/clinical)
        t3_t4_status: T3/T4 status (optimal/suboptimal/notTested)
    
    Returns:
        (score, category) - max 4.0 points
    """
    if tsh_category == 'optimal':
        if t3_t4_status == 'optimal':
            return Decimal('4.0'), 'Optimal'
        elif t3_t4_status == 'suboptimal':
            return Decimal('3.0'), 'Good (T3/T4 suboptimal)'
        else:  # notTested
            return Decimal('3.5'), 'Good (TSH only)'
    elif tsh_category == 'veryGood':
        if t3_t4_status == 'optimal':
            return Decimal('3.5'), 'Very Good'
        elif t3_t4_status == 'suboptimal':
            return Decimal('2.5'), 'Acceptable'
        else:  # notTested
            return Decimal('3.0'), 'Acceptable (TSH only)'
    elif tsh_category == 'acceptable':
        return Decimal('3.0'), 'Acceptable'
    elif tsh_category == 'subclinical':
        return Decimal('1.5'), 'Subclinical Dysfunction'
    elif tsh_category == 'clinical':
        return Decimal('0.0'), 'Clinical Dysfunction'
    else:
        return Decimal('0.0'), 'Unknown'


# ==============================================================================
# TEST 2: SEX HORMONES (4 POINTS) - SEX-SPECIFIC
# ==============================================================================

def score_male_testosterone_exact(total_t: float, age: int, 
                                  free_t: Optional[float] = None,
                                  estradiol: Optional[float] = None) -> Tuple[Decimal, str]:
    """
    Score male testosterone levels (age-adjusted).
    
    Args:
        total_t: Total testosterone (ng/dL)
        age: Patient age in years
        free_t: Free testosterone (pg/mL) - optional
        estradiol: Estradiol (pg/mL) - optional
    
    Returns:
        (score, assessment) - max 4.0 points
    """
    # Age-adjusted thresholds
    if age < 50:
        # Ages 30-49
        if total_t > 750:
            total_t_score = 4.0
            assessment = "Optimal"
        elif total_t >= 650:
            total_t_score = 3.6
            assessment = "Very Good"
        elif total_t >= 500:
            total_t_score = 3.2
            assessment = "Good"
        elif total_t >= 350:
            total_t_score = 2.4
            assessment = "Acceptable"
        elif total_t >= 264:
            total_t_score = 1.2
            assessment = "Low-Normal"
        else:
            total_t_score = 0.0
            assessment = "Hypogonadal"
    elif age < 70:
        # Ages 50-69
        if total_t > 650:
            total_t_score = 4.0
            assessment = "Optimal for age"
        elif total_t >= 550:
            total_t_score = 3.6
            assessment = "Very Good"
        elif total_t >= 450:
            total_t_score = 3.2
            assessment = "Good"
        elif total_t >= 300:
            total_t_score = 2.4
            assessment = "Acceptable"
        elif total_t >= 264:
            total_t_score = 1.2
            assessment = "Low-Normal"
        else:
            total_t_score = 0.0
            assessment = "Hypogonadal"
    else:
        # Ages 70+
        if total_t > 550:
            total_t_score = 4.0
            assessment = "Optimal for age"
        elif total_t >= 450:
            total_t_score = 3.6
            assessment = "Very Good"
        elif total_t >= 350:
            total_t_score = 3.2
            assessment = "Good"
        elif total_t >= 264:
            total_t_score = 2.4
            assessment = "Acceptable"
        elif total_t >= 200:
            total_t_score = 1.2
            assessment = "Low-Normal"
        else:
            total_t_score = 0.0
            assessment = "Low"
    
    final_score = total_t_score
    
    # Free testosterone adjustment
    if free_t is not None:
        if 12 <= free_t <= 25:
            free_t_score = 4.0
        elif 9 <= free_t < 12 or 25 < free_t <= 30:
            free_t_score = 3.0
        else:
            free_t_score = 1.5
        
        # Average with total T, weighted toward worse
        final_score = min(total_t_score, (total_t_score + free_t_score) / 2)
        assessment += " (free T adjusted)"
    
    # Estradiol penalty
    if estradiol is not None and estradiol > 40:
        final_score = max(final_score - 0.5, 0)
        assessment += " (elevated estradiol)"
    
    return Decimal(str(round(min(final_score, 4.0), 1))), assessment


def score_male_testosterone_category(category: str) -> Tuple[Decimal, str]:
    """
    Score male testosterone from category selection.
    
    Args:
        category: Testosterone category
    
    Returns:
        (score, assessment) - max 4.0 points
    """
    if category == 'optimal':
        return Decimal('4.0'), 'Optimal for age'
    elif category == 'veryGood':
        return Decimal('3.6'), 'Very Good'
    elif category == 'good':
        return Decimal('3.2'), 'Good'
    elif category == 'acceptable':
        return Decimal('2.4'), 'Acceptable'
    elif category == 'lowNormal':
        return Decimal('1.2'), 'Low-Normal'
    elif category == 'low':
        return Decimal('0.0'), 'Hypogonadal - requires evaluation'
    else:
        return Decimal('0.0'), 'Unknown'


def score_female_hormones(menopause_status: str, cycle_regularity: Optional[str] = None,
                          symptoms: Optional[str] = None, 
                          hormone_category: str = 'notTested') -> Tuple[Decimal, str]:
    """
    Score female hormone status (multi-factor assessment).
    
    Args:
        menopause_status: pre/peri/post
        cycle_regularity: yes/mostly/no (pre-menopausal only)
        symptoms: minimal/mild/moderate/severe
        hormone_category: optimal/acceptable/imbalanced/deficient/notTested
    
    Returns:
        (score, assessment) - max 4.0 points
    """
    base_score = 0.0
    
    # Hormone test results (2 points max)
    if hormone_category == 'optimal':
        base_score += 2.0
    elif hormone_category == 'acceptable':
        base_score += 1.5
    elif hormone_category == 'imbalanced':
        base_score += 1.0
    elif hormone_category == 'deficient':
        base_score += 0.5
    elif hormone_category == 'notTested':
        base_score += 1.5  # Neutral if not tested
    
    # Cycle regularity (1.5 points max - pre-menopausal only)
    if menopause_status == 'pre':
        if cycle_regularity == 'yes':
            base_score += 1.5
        elif cycle_regularity == 'mostly':
            base_score += 1.0
        elif cycle_regularity == 'no':
            base_score += 0.5
    elif menopause_status in ['peri', 'post']:
        base_score += 1.0  # Neutral for non-cycling women
    
    # Symptom adjustment (0.5 points max)
    if symptoms == 'minimal':
        base_score += 0.5
    elif symptoms == 'mild':
        base_score += 0.25
    elif symptoms == 'moderate':
        base_score -= 0.25
    elif symptoms == 'severe':
        base_score -= 0.5
    
    # Cap at 0-4 range
    final_score = min(max(base_score, 0), 4.0)
    
    # Category
    if final_score >= 3.5:
        category = "Optimal"
    elif final_score >= 2.5:
        category = "Good"
    elif final_score >= 1.5:
        category = "Acceptable"
    else:
        category = "Imbalanced"
    
    return Decimal(str(round(final_score, 1))), category


def score_female_hormones_exact(menopause_status: str, age: int,
                                estradiol: Optional[float] = None,
                                progesterone: Optional[float] = None,
                                fsh: Optional[float] = None,
                                lh: Optional[float] = None,
                                testosterone: Optional[float] = None,
                                amh: Optional[float] = None,
                                symptoms: str = 'mild') -> Tuple[Decimal, str]:
    """
    Score female hormones from exact lab values.
    
    Args:
        menopause_status: pre/peri/post
        age: Patient age
        estradiol: Estradiol (pg/mL)
        progesterone: Progesterone (ng/mL)
        fsh: FSH (mIU/mL)
        lh: LH (mIU/mL)
        testosterone: Testosterone (ng/dL)
        amh: AMH (ng/mL)
        symptoms: minimal/mild/moderate/severe
    
    Returns:
        (score, assessment) - max 4.0 points
    """
    base_score = 0.0
    flags = []
    
    # FSH-based menopause status verification (2 points max)
    if fsh:
        if menopause_status == 'pre':
            if fsh < 10:
                base_score += 2.0  # Optimal pre-menopausal
            elif fsh < 15:
                base_score += 1.5  # Borderline
                flags.append("FSH rising")
            else:
                base_score += 0.5  # Elevated for pre-menopausal
                flags.append("FSH elevated")
        elif menopause_status == 'peri':
            if 10 <= fsh <= 30:
                base_score += 2.0  # Expected peri-menopausal
            elif fsh < 10:
                base_score += 1.5  # Still cycling well
            else:
                base_score += 1.5  # Transitioning to post
        elif menopause_status == 'post':
            if fsh > 30:
                base_score += 2.0  # Expected post-menopausal
            else:
                base_score += 1.0  # Not fully menopausal yet
    else:
        base_score += 1.5  # Neutral if FSH not tested
    
    # Estradiol assessment (0.5 points)
    if estradiol:
        if menopause_status == 'pre':
            if 50 <= estradiol <= 350:
                base_score += 0.5  # Normal cycling range
            elif estradiol < 50:
                flags.append("low estradiol")
        elif menopause_status == 'peri':
            if 20 <= estradiol <= 150:
                base_score += 0.5  # Transitional range
            elif estradiol > 150:
                base_score += 0.25  # Still cycling
        elif menopause_status == 'post':
            if estradiol < 50:
                base_score += 0.5  # Expected post-menopausal
            else:
                flags.append("high estradiol for post-menopausal")
    
    # Testosterone assessment (0.5 points)
    if testosterone:
        if 15 <= testosterone <= 70:
            base_score += 0.5  # Normal female range
        elif testosterone > 70:
            flags.append("elevated testosterone")
        elif testosterone < 15:
            flags.append("low testosterone")
    
    # AMH assessment (0.5 points) - ovarian reserve
    if amh:
        if age < 35:
            if amh > 1.5:
                base_score += 0.5  # Good reserve
            elif amh > 1.0:
                base_score += 0.25  # Acceptable
        elif age < 45:
            if amh > 1.0:
                base_score += 0.5  # Good for age
            elif amh > 0.5:
                base_score += 0.25  # Declining
        else:  # 45+
            if amh > 0.5:
                base_score += 0.5  # Still present
            else:
                base_score += 0.25  # Low/absent (expected)
    
    # Symptom adjustment (0.5 points max)
    if symptoms == 'minimal':
        base_score += 0.5
    elif symptoms == 'mild':
        base_score += 0.25
    elif symptoms == 'moderate':
        base_score -= 0.25
    elif symptoms == 'severe':
        base_score -= 0.5
    
    # Cap at 0-4 range
    final_score = min(max(base_score, 0), 4.0)
    
    # Category
    if final_score >= 3.5:
        category = "Optimal"
    elif final_score >= 2.5:
        category = "Good"
    elif final_score >= 1.5:
        category = "Acceptable"
    else:
        category = "Imbalanced"
    
    if flags:
        category += f" ({', '.join(flags)})"
    
    return Decimal(str(round(final_score, 1))), category


def score_female_hormones_exact(menopause_status: str, age: int,
                                estradiol: Optional[float] = None,
                                progesterone: Optional[float] = None,
                                fsh: Optional[float] = None,
                                lh: Optional[float] = None,
                                testosterone: Optional[float] = None,
                                amh: Optional[float] = None,
                                symptoms: Optional[str] = None) -> Tuple[Decimal, str]:
    """
    Score female hormones from exact lab values.
    Interpretation varies by menopause status and age.
    Combines exact values with symptoms for final score.
    
    Args:
        menopause_status: pre/peri/post
        age: Patient age
        estradiol: Estradiol (pg/mL)
        progesterone: Progesterone (ng/mL)
        fsh: FSH (mIU/mL)
        lh: LH (mIU/mL)
        testosterone: Testosterone (ng/dL) - female range
        amh: AMH (ng/mL) - ovarian reserve
        symptoms: minimal/mild/moderate/severe
    
    Returns:
        (score, assessment) - max 4.0 points
    """
    lab_score = 0.0
    flags = []
    
    # FSH scoring (1.5 points max) - primary menopause marker
    if fsh is not None:
        if menopause_status == 'pre':
            # Pre-menopausal: FSH should be <10
            if fsh < 10:
                lab_score += 1.5
            elif fsh < 15:
                lab_score += 1.0
                flags.append("Elevated FSH")
            else:
                lab_score += 0.5
                flags.append("High FSH - approaching peri-menopause")
        elif menopause_status == 'peri':
            # Peri-menopausal: FSH 10-30 is expected
            if 10 <= fsh <= 30:
                lab_score += 1.5
            elif fsh < 10:
                lab_score += 1.0
            else:
                lab_score += 1.0
                flags.append("Post-menopausal FSH")
        elif menopause_status == 'post':
            # Post-menopausal: FSH >30 is expected
            if fsh > 30:
                lab_score += 1.5
            elif fsh > 20:
                lab_score += 1.0
            else:
                lab_score += 0.5
                flags.append("Low FSH for post-menopause")
    else:
        # No FSH - give neutral partial credit
        lab_score += 1.0
    
    # Estradiol scoring (1.0 point max)
    if estradiol is not None:
        if menopause_status == 'pre':
            # Pre-menopausal: Cycle-dependent, broad range acceptable
            if 30 <= estradiol <= 350:
                lab_score += 1.0
            elif 15 <= estradiol < 30 or estradiol > 350:
                lab_score += 0.5
                flags.append("Estradiol outside typical cycle range")
            else:
                lab_score += 0.25
                flags.append("Very low estradiol")
        elif menopause_status == 'peri':
            # Peri-menopausal: Fluctuating, 20-200 typical
            if 20 <= estradiol <= 200:
                lab_score += 1.0
            else:
                lab_score += 0.75
        elif menopause_status == 'post':
            # Post-menopausal: <50 expected
            if estradiol < 50:
                lab_score += 1.0
            elif estradiol < 100:
                lab_score += 0.5
                flags.append("Elevated estradiol for post-menopause")
            else:
                lab_score += 0.25
                flags.append("High estradiol - investigate")
    else:
        lab_score += 0.5
    
    # Progesterone scoring (0.5 points max) - cycle-dependent
    if progesterone is not None and menopause_status in ['pre', 'peri']:
        if menopause_status == 'pre':
            # Pre-menopausal: Should be >5 in luteal phase, <1.5 in follicular
            if 5 <= progesterone <= 25:
                lab_score += 0.5
            elif 1.5 <= progesterone < 5:
                lab_score += 0.25
            elif progesterone < 1.5:
                lab_score += 0.5  # Follicular phase likely
            else:
                lab_score += 0.25
        elif menopause_status == 'peri':
            # Peri: Variable, <1 common
            if progesterone < 5:
                lab_score += 0.5
            else:
                lab_score += 0.25
    elif progesterone is not None and menopause_status == 'post':
        # Post-menopausal: Should be <1
        if progesterone < 1:
            lab_score += 0.5
        else:
            lab_score += 0.25
            flags.append("Elevated progesterone for post-menopause")
    else:
        lab_score += 0.25
    
    # Testosterone scoring (0.5 points max) - same across all ages
    if testosterone is not None:
        if 15 <= testosterone <= 70:
            lab_score += 0.5
        elif testosterone < 15:
            lab_score += 0.25
            flags.append("Low testosterone")
        else:
            lab_score += 0.25
            flags.append("Elevated testosterone - check for PCOS/adrenal")
    else:
        lab_score += 0.25
    
    # AMH scoring (0.5 points max) - ovarian reserve (pre/peri only)
    if amh is not None and menopause_status in ['pre', 'peri']:
        if amh > 1.0:
            lab_score += 0.5
        elif amh > 0.5:
            lab_score += 0.25
        else:
            lab_score += 0.1
            flags.append("Low AMH - diminished ovarian reserve")
    else:
        lab_score += 0.25
    
    # Cap lab score at 4.0
    lab_score = min(lab_score, 4.0)
    
    # Symptom adjustment (can adjust final score by -1 to +0.5)
    symptom_adjustment = 0.0
    if symptoms == 'minimal':
        symptom_adjustment = 0.5
    elif symptoms == 'mild':
        symptom_adjustment = 0.0
    elif symptoms == 'moderate':
        symptom_adjustment = -0.5
    elif symptoms == 'severe':
        symptom_adjustment = -1.0
    
    # Final score: weighted average of labs (80%) and symptoms (20%)
    final_score = lab_score + symptom_adjustment
    final_score = min(max(final_score, 0), 4.0)
    
    # Assessment category
    if final_score >= 3.5:
        assessment = "Optimal hormone balance"
    elif final_score >= 2.5:
        assessment = "Good balance"
    elif final_score >= 1.5:
        assessment = "Acceptable"
    else:
        assessment = "Hormonal imbalance"
    
    if flags:
        assessment += f" ({', '.join(flags)})"
    
    return Decimal(str(round(final_score, 1))), assessment


# ==============================================================================
# TEST 3: SEXUAL HEALTH (1 POINT) - SEX-SPECIFIC
# ==============================================================================

def score_sexual_health(response: str) -> Tuple[Decimal, str]:
    """
    Score sexual health and function (same scoring for male/female).
    
    Args:
        response: normal/mild/moderate/significant/skip
    
    Returns:
        (score, note) - max 1.0 point
    """
    if response == 'normal':
        return Decimal('1.0'), 'No concerns'
    elif response == 'mild':
        return Decimal('0.75'), 'Minor issue'
    elif response == 'moderate':
        return Decimal('0.5'), 'Reduced libido or function'
    elif response == 'significant':
        return Decimal('0.0'), 'Severe dysfunction - hormonal/vascular concern'
    elif response == 'skip':
        return Decimal('0.5'), 'Prefer not to answer (neutral score)'
    else:
        return Decimal('0.5'), 'No response'


# ==============================================================================
# TEST 4: VITAMIN D (2 POINTS)
# ==============================================================================

def score_vitamin_d_exact(vitd: float) -> Tuple[Decimal, str]:
    """
    Score vitamin D from exact lab value.
    
    Args:
        vitd: 25-Hydroxy Vitamin D (ng/mL)
    
    Returns:
        (score, category) - max 2.0 points
    """
    if vitd > 60:
        return Decimal('2.0'), 'Optimal'
    elif vitd >= 50:
        return Decimal('1.8'), 'Very Good'
    elif vitd >= 40:
        return Decimal('1.5'), 'Good'
    elif vitd >= 30:
        return Decimal('1.0'), 'Sufficient'
    elif vitd >= 20:
        return Decimal('0.5'), 'Insufficient'
    else:
        return Decimal('0.0'), 'Deficient'


def score_vitamin_d_category(category: str) -> Tuple[Decimal, str]:
    """
    Score vitamin D from category selection.
    
    Args:
        category: optimal/sufficient/insufficient/deficient
    
    Returns:
        (score, category) - max 2.0 points
    """
    if category == 'optimal':
        return Decimal('2.0'), 'Optimal for health'
    elif category == 'sufficient':
        return Decimal('1.5'), 'Adequate'
    elif category == 'insufficient':
        return Decimal('0.8'), 'Supplement recommended'
    elif category == 'deficient':
        return Decimal('0.0'), 'Deficiency - requires treatment'
    else:
        return Decimal('0.0'), 'Unknown'


# ==============================================================================
# TEST 5: HEMOGLOBIN & IRON (2 POINTS) - SEX-ADJUSTED
# ==============================================================================

def score_hemoglobin_exact(hb: float, sex: str, ferritin: Optional[float] = None) -> Tuple[Decimal, str]:
    """
    Score hemoglobin/iron status from exact lab values (sex-adjusted).
    
    Args:
        hb: Hemoglobin (g/dL)
        sex: 'male' or 'female'
        ferritin: Ferritin (ng/mL) - optional
    
    Returns:
        (score, category) - max 2.0 points
    """
    if sex == 'male':
        if 14 <= hb <= 17.5:
            score = 2.0
            category = "Optimal"
        elif hb >= 13.5:
            score = 1.5
            category = "Acceptable"
        elif hb >= 12:
            score = 1.0
            category = "Borderline Low"
        elif hb >= 10:
            score = 0.5
            category = "Anemic"
        else:
            score = 0.0
            category = "Severe Anemia"
    else:  # female
        if 13 <= hb <= 16:
            score = 2.0
            category = "Optimal"
        elif hb >= 12:
            score = 1.5
            category = "Acceptable"
        elif hb >= 11:
            score = 1.0
            category = "Borderline Low"
        elif hb >= 9:
            score = 0.5
            category = "Anemic"
        else:
            score = 0.0
            category = "Severe Anemia"
    
    return Decimal(str(round(score, 1))), category


def score_hemoglobin_category(category: str) -> Tuple[Decimal, str]:
    """
    Score hemoglobin from category selection.
    
    Args:
        category: optimal/acceptable/borderline/anemic
    
    Returns:
        (score, note) - max 2.0 points
    """
    if category == 'optimal':
        return Decimal('2.0'), 'Normal iron status'
    elif category == 'acceptable':
        return Decimal('1.5'), 'Within normal range'
    elif category == 'borderline':
        return Decimal('1.0'), 'Monitor, consider supplementation'
    elif category == 'anemic':
        return Decimal('0.5'), 'Requires evaluation and treatment'
    else:
        return Decimal('0.0'), 'Unknown'


# ==============================================================================
# TEST 6: EXERCISE HABITS (2 POINTS)
# ==============================================================================

def score_exercise(frequency: str, types_count: int) -> Tuple[Decimal, str]:
    """
    Score exercise habits (frequency + variety).
    
    Args:
        frequency: 6-7/4-5/2-3/0-1 days per week
        types_count: Number of exercise types (0-3)
    
    Returns:
        (score, category) - max 2.0 points
    """
    # Frequency scoring (1 point max)
    if frequency == '6-7':
        freq_score = 1.0
    elif frequency == '4-5':
        freq_score = 0.75
    elif frequency == '2-3':
        freq_score = 0.5
    elif frequency == '0-1':
        freq_score = 0.0
    else:
        freq_score = 0.0
    
    # Types scoring (1 point max)
    if types_count == 3:
        types_score = 1.0
    elif types_count == 2:
        types_score = 0.75
    elif types_count == 1:
        types_score = 0.5
    else:
        types_score = 0.0
    
    total_score = freq_score + types_score
    
    # Category
    if total_score >= 1.75:
        category = "Excellent"
    elif total_score >= 1.25:
        category = "Good"
    elif total_score >= 0.75:
        category = "Fair"
    else:
        category = "Poor"
    
    return Decimal(str(round(total_score, 1))), category


# ==============================================================================
# TEST 7: SLEEP DURATION & QUALITY (3 POINTS)
# ==============================================================================

def score_sleep(duration: str, quality: str, onset: str) -> Tuple[Decimal, str]:
    """
    Score sleep habits (duration + quality + onset).
    
    Args:
        duration: sleep duration category
        quality: how often feel rested (most/sometimes/rarely)
        onset: time to fall asleep (fast/medium/slow)
    
    Returns:
        (score, category) - max 3.0 points
    """
    # Duration scoring (1.5 points max)
    if duration == '7.5-8.5':
        duration_score = 1.5
    elif duration in ['7-7.4', '8.6-9']:
        duration_score = 1.0
    elif duration == '6-6.9':
        duration_score = 0.5
    elif duration in ['less6', 'more9']:
        duration_score = 0.0
    else:
        duration_score = 0.0
    
    # Quality scoring (1 point max)
    if quality == 'most':
        quality_score = 1.0
    elif quality == 'sometimes':
        quality_score = 0.5
    elif quality == 'rarely':
        quality_score = 0.0
    else:
        quality_score = 0.0
    
    # Onset scoring (0.5 points max)
    if onset == 'fast':
        onset_score = 0.5
    elif onset == 'medium':
        onset_score = 0.25
    elif onset == 'slow':
        onset_score = 0.0
    else:
        onset_score = 0.0
    
    total_score = duration_score + quality_score + onset_score
    
    # Category
    if total_score >= 2.5:
        category = "Excellent"
    elif total_score >= 1.5:
        category = "Good"
    elif total_score >= 1.0:
        category = "Fair"
    else:
        category = "Poor"
    
    return Decimal(str(round(total_score, 1))), category


# ==============================================================================
# TEST 8: SKIN & HAIR HEALTH (1 POINT)
# ==============================================================================

def score_appearance(skin_elasticity: str, hair_health: str) -> Tuple[Decimal, str]:
    """
    Score skin and hair health.
    
    Args:
        skin_elasticity: excellent/moderate/poor
        hair_health: thick/thinning/loss/significant/na
    
    Returns:
        (score, note) - max 1.0 point
    """
    # Skin scoring (0.5 points max)
    if skin_elasticity == 'excellent':
        skin_score = 0.5
    elif skin_elasticity == 'moderate':
        skin_score = 0.25
    elif skin_elasticity == 'poor':
        skin_score = 0.0
    else:
        skin_score = 0.0
    
    # Hair scoring (0.5 points max)
    if hair_health == 'thick':
        hair_score = 0.5
    elif hair_health == 'thinning':
        hair_score = 0.375
    elif hair_health == 'loss':
        hair_score = 0.25
    elif hair_health == 'significant':
        hair_score = 0.0
    elif hair_health == 'na':
        hair_score = 0.375  # Neutral score
    else:
        hair_score = 0.0
    
    total_score = skin_score + hair_score
    
    return Decimal(str(round(total_score, 2))), f"Skin: {skin_elasticity}, Hair: {hair_health}"


# ==============================================================================
# TEST 9: STRESS & OVERWHELM (1 POINT)
# ==============================================================================

def score_stress(level: int) -> Tuple[Decimal, str]:
    """
    Score stress level (1-10 scale).
    
    Args:
        level: Stress level (1-10)
    
    Returns:
        (score, category) - max 1.0 point
    """
    if level <= 2:
        return Decimal('1.0'), 'Low stress'
    elif level <= 4:
        return Decimal('0.75'), 'Low-moderate stress'
    elif level <= 6:
        return Decimal('0.5'), 'Moderate stress'
    elif level <= 8:
        return Decimal('0.25'), 'High stress'
    else:  # 9-10
        return Decimal('0.0'), 'Very high/severe stress'
