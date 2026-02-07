"""
Pillar 1 Routes - Movement & Strength
======================================

Routes for all 8 physical performance tests.
Field names aligned with models/pillar1.py
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from decimal import Decimal
from typing import Optional

from models import db
from models.assessment import Assessment
from models.patient import Patient
from models.pillar1 import Pillar1Results
from calculators.pillar1 import (
    calculate_gait_speed,
    get_faster_gait_trial,
    calculate_grip_best,
    get_best_flexibility_trial,
    calculate_6mwt_distance,
    calculate_6mwt_percent_predicted,
    estimate_vo2max_non_exercise,
    estimate_vo2max_from_6mwt,
    vo2max_to_mets,
)
from scoring.pillar1 import (
    score_chair_stand,
    score_grip_strength,
    score_gait_speed,
    score_balance,
    score_tug,
    score_vo2max,
    score_flexibility,
    score_6mwt,
)

bp = Blueprint('pillar1', __name__, url_prefix='/assessment')


# =============================================================================
# PILLAR 1 DASHBOARD / OVERVIEW
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1')
def overview(assessment_id: int):
    """Pillar 1 overview showing all tests and scores."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = assessment.pillar1_results
        
        # Calculate test completion status
        tests_complete = {
            'chair_stand': pillar1 and pillar1.chair_stand_reps is not None,
            'grip_strength': pillar1 and pillar1.grip_dominant_best is not None,
            'gait_speed': pillar1 and pillar1.gait_speed_ms is not None,
            'balance': pillar1 and pillar1.single_leg_better_best is not None,
            'tug': pillar1 and pillar1.tug_faster_sec is not None,
            'vo2max': pillar1 and pillar1.vo2_max is not None,
            'flexibility': pillar1 and pillar1.flexibility_best_cm is not None,
            '6mwt': pillar1 and pillar1.walk_6min_total_m is not None,
        }
        
        completed_count = sum(1 for v in tests_complete.values() if v)
        
        return render_template(
            'pillar1/overview.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
            tests_complete=tests_complete,
            completed_count=completed_count,
        )
    finally:
        session.close()


# =============================================================================
# TEST 1: 30-SECOND CHAIR STAND
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/chair-stand', methods=['GET', 'POST'])
def chair_stand(assessment_id: int):
    """30-Second Chair Stand Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        
        if request.method == 'POST':
            try:
                reps = int(request.form.get('reps', 0))
                
                # Calculate score
                result = score_chair_stand(reps, assessment.age_at_assessment, patient.sex)
                
                # Update model
                pillar1.chair_stand_reps = reps
                pillar1.chair_stand_score = Decimal(str(result['score']))
                pillar1.chair_stand_category = result['category']
                
                session.commit()
                flash(f"Chair stand test saved: {reps} reps, {result['score']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/chair_stand.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
        )
    finally:
        session.close()


# =============================================================================
# TEST 2: GRIP STRENGTH
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/grip-strength', methods=['GET', 'POST'])
def grip_strength(assessment_id: int):
    """Grip Strength Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        
        if request.method == 'POST':
            try:
                dominant_hand = request.form.get('dominant_hand', 'right')
                
                # Get left hand trials
                pillar1.grip_dominant_hand = dominant_hand
                pillar1.grip_left_1 = _parse_decimal(request.form.get('grip_left_1'))
                pillar1.grip_left_2 = _parse_decimal(request.form.get('grip_left_2'))
                pillar1.grip_left_3 = _parse_decimal(request.form.get('grip_left_3'))
                
                # Get right hand trials
                pillar1.grip_right_1 = _parse_decimal(request.form.get('grip_right_1'))
                pillar1.grip_right_2 = _parse_decimal(request.form.get('grip_right_2'))
                pillar1.grip_right_3 = _parse_decimal(request.form.get('grip_right_3'))
                
                # Use model's built-in calculation
                pillar1.calculate_grip_best()
                
                if pillar1.grip_dominant_best is None:
                    flash('Please enter at least one grip measurement for dominant hand', 'error')
                    return redirect(url_for('pillar1.grip_strength', assessment_id=assessment_id))
                
                # Score based on dominant hand
                result = score_grip_strength(float(pillar1.grip_dominant_best), assessment.age_at_assessment, patient.sex)
                
                pillar1.grip_score = Decimal(str(result['score']))
                pillar1.grip_category = result['category']
                
                # Set sarcopenia flag on the pillar1 model
                if result.get('sarcopenia_flag'):
                    pillar1.sarcopenia_flag = True
                
                session.commit()
                
                msg = f"Grip strength saved: {pillar1.grip_dominant_best} kg, {result['score']} points ({result['category']})"
                if result.get('sarcopenia_flag'):
                    msg += " ⚠️ SARCOPENIA WARNING"
                flash(msg, 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/grip_strength.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
        )
    finally:
        session.close()


# =============================================================================
# TEST 3: GAIT SPEED
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/gait-speed', methods=['GET', 'POST'])
def gait_speed(assessment_id: int):
    """4-Meter Gait Speed Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        
        if request.method == 'POST':
            try:
                trial1_time = float(request.form.get('trial1_time', 0))
                trial2_time = float(request.form.get('trial2_time', 0))
                walking_aid = request.form.get('walking_aid', '')
                
                if trial1_time <= 0 or trial2_time <= 0:
                    flash('Please enter valid times for both trials', 'error')
                    return redirect(url_for('pillar1.gait_speed', assessment_id=assessment_id))
                
                # Store trials
                pillar1.gait_trial_1_sec = Decimal(str(trial1_time))
                pillar1.gait_trial_2_sec = Decimal(str(trial2_time))
                pillar1.gait_walking_aid = walking_aid if walking_aid else None
                
                # Use model's built-in calculation
                pillar1.calculate_gait_speed()
                
                # Score
                result = score_gait_speed(float(pillar1.gait_speed_ms), assessment.age_at_assessment)
                
                pillar1.gait_score = Decimal(str(result['score']))
                pillar1.gait_category = result['category']
                
                session.commit()
                flash(f"Gait speed saved: {pillar1.gait_speed_ms} m/s, {result['score']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/gait_speed.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
        )
    finally:
        session.close()


# =============================================================================
# TEST 4: BALANCE ASSESSMENT
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/balance', methods=['GET', 'POST'])
def balance(assessment_id: int):
    """Balance Assessment (Romberg + Single-Leg Stance)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        
        if request.method == 'POST':
            try:
                # Romberg test
                pillar1.romberg_eyes_open = request.form.get('romberg_eyes_open') == 'pass'
                pillar1.romberg_eyes_closed = request.form.get('romberg_eyes_closed') == 'pass'
                
                # Single-leg stance - LEFT leg
                pillar1.single_leg_left_1 = _parse_decimal(request.form.get('left_trial1'))
                pillar1.single_leg_left_2 = _parse_decimal(request.form.get('left_trial2'))
                
                # Single-leg stance - RIGHT leg
                pillar1.single_leg_right_1 = _parse_decimal(request.form.get('right_trial1'))
                pillar1.single_leg_right_2 = _parse_decimal(request.form.get('right_trial2'))
                
                # Use model's built-in calculation (uses BETTER leg per spec)
                pillar1.calculate_single_leg_best()
                
                # Score
                single_leg_time = float(pillar1.single_leg_better_best) if pillar1.single_leg_better_best else 0
                result = score_balance(
                    pillar1.romberg_eyes_open,
                    pillar1.romberg_eyes_closed,
                    single_leg_time,
                    assessment.age_at_assessment
                )
                
                pillar1.single_leg_score = Decimal(str(result['single_leg_score']))
                pillar1.single_leg_category = result['single_leg_category']
                pillar1.balance_total_score = Decimal(str(result['total_score']))
                pillar1.balance_category = result['single_leg_category']
                
                session.commit()
                flash(f"Balance assessment saved: {result['total_score']} points total", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/balance.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
        )
    finally:
        session.close()


# =============================================================================
# TEST 5: TIMED UP AND GO
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/tug', methods=['GET', 'POST'])
def tug(assessment_id: int):
    """Timed Up and Go (TUG) Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        
        if request.method == 'POST':
            try:
                trial1_time = float(request.form.get('trial1_time', 0))
                trial2_time = float(request.form.get('trial2_time', 0))
                
                # Qualitative observations
                pillar1.tug_unsteady_gait = request.form.get('unsteady_gait') == 'yes'
                pillar1.tug_unsteady_turn = request.form.get('unsteady_turn') == 'yes'
                pillar1.tug_used_arms = request.form.get('used_arms') == 'yes'
                pillar1.tug_plopped_down = request.form.get('plopped_down') == 'yes'
                
                if trial1_time <= 0 or trial2_time <= 0:
                    flash('Please enter valid times for both trials', 'error')
                    return redirect(url_for('pillar1.tug', assessment_id=assessment_id))
                
                # Store trials
                pillar1.tug_trial_1_sec = Decimal(str(trial1_time))
                pillar1.tug_trial_2_sec = Decimal(str(trial2_time))
                
                # Use model's built-in calculation
                pillar1.calculate_tug_faster()
                
                # Score with qualitative modifiers
                result = score_tug(
                    float(pillar1.tug_faster_sec),
                    assessment.age_at_assessment,
                    pillar1.tug_unsteady_gait,
                    pillar1.tug_unsteady_turn,
                    pillar1.tug_used_arms,
                    pillar1.tug_plopped_down
                )
                
                pillar1.tug_base_score = Decimal(str(result['base_score']))
                pillar1.tug_score = Decimal(str(result['score']))
                pillar1.tug_category = result['category']
                
                session.commit()
                flash(f"TUG saved: {pillar1.tug_faster_sec} sec, {result['score']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/tug.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
        )
    finally:
        session.close()


# =============================================================================
# TEST 6: VO2 MAX
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/vo2max', methods=['GET', 'POST'])
def vo2max(assessment_id: int):
    """VO2 Max Assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        section0 = assessment.section0_results
        
        if request.method == 'POST':
            try:
                method = request.form.get('method', 'non_exercise')
                vo2_value = None
                
                pillar1.vo2_method = method
                
                if method == 'direct':
                    # Direct measurement entered
                    vo2_value = float(request.form.get('vo2max_direct', 0))
                    pillar1.vo2_direct_value = Decimal(str(vo2_value))
                    
                elif method == 'non_exercise':
                    # Non-exercise estimation
                    resting_hr = int(request.form.get('resting_hr', 70))
                    pa_index = int(request.form.get('pa_index', 3))
                    
                    pillar1.vo2_resting_hr = resting_hr
                    pillar1.vo2_pa_index = pa_index
                    
                    # Get BMI from Section 0 or calculate
                    bmi = float(section0.bmi) if section0 and section0.bmi else 25.0
                    
                    vo2_value = estimate_vo2max_non_exercise(
                        assessment.age_at_assessment,
                        patient.sex,
                        bmi,
                        resting_hr,
                        pa_index
                    )
                    
                elif method == '6mwt':
                    # Estimate from 6MWT if already completed
                    if pillar1.walk_6min_total_m:
                        height_cm = float(section0.height_cm) if section0 else 170
                        weight_kg = float(section0.weight_kg) if section0 else 70
                        
                        vo2_value = estimate_vo2max_from_6mwt(
                            float(pillar1.walk_6min_total_m),
                            assessment.age_at_assessment,
                            weight_kg,
                            height_cm,
                            patient.sex
                        )
                    else:
                        flash('Complete 6MWT first to use this estimation method', 'error')
                        return redirect(url_for('pillar1.vo2max', assessment_id=assessment_id))
                
                if vo2_value is None or vo2_value <= 0:
                    flash('Unable to calculate VO2 max', 'error')
                    return redirect(url_for('pillar1.vo2max', assessment_id=assessment_id))
                
                # Store final value
                pillar1.vo2_max = Decimal(str(vo2_value))
                
                # Calculate METs
                pillar1.calculate_vo2_mets()
                
                # Score
                result = score_vo2max(vo2_value, assessment.age_at_assessment, patient.sex)
                
                pillar1.vo2_score = Decimal(str(result['score']))
                pillar1.vo2_category = result['category']
                
                # Check for low VO2 flag
                if vo2_value < 20:
                    pillar1.low_vo2_flag = True
                
                session.commit()
                flash(f"VO2 max saved: {vo2_value} mL/kg/min ({pillar1.vo2_mets} METs), {result['score']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/vo2max.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
            section0=section0,
        )
    finally:
        session.close()


# =============================================================================
# TEST 7: FLEXIBILITY (SIT-AND-REACH)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/flexibility', methods=['GET', 'POST'])
def flexibility(assessment_id: int):
    """Sit-and-Reach Flexibility Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        
        if request.method == 'POST':
            try:
                pillar1.flexibility_trial_1_cm = _parse_decimal(request.form.get('trial1'))
                pillar1.flexibility_trial_2_cm = _parse_decimal(request.form.get('trial2'))
                pillar1.flexibility_trial_3_cm = _parse_decimal(request.form.get('trial3'))
                
                # Use model's built-in calculation
                pillar1.calculate_flexibility_best()
                
                if pillar1.flexibility_best_cm is None:
                    flash('Please enter at least one measurement', 'error')
                    return redirect(url_for('pillar1.flexibility', assessment_id=assessment_id))
                
                # Score
                result = score_flexibility(float(pillar1.flexibility_best_cm), assessment.age_at_assessment, patient.sex)
                
                pillar1.flexibility_score = Decimal(str(result['score']))
                pillar1.flexibility_category = result['category']
                
                session.commit()
                flash(f"Flexibility saved: {pillar1.flexibility_best_cm} cm, {result['score']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/flexibility.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
        )
    finally:
        session.close()


# =============================================================================
# TEST 8: 6-MINUTE WALK TEST
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/6mwt', methods=['GET', 'POST'])
def walk_6min(assessment_id: int):
    """6-Minute Walk Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar1 = _get_or_create_pillar1(session, assessment)
        section0 = assessment.section0_results
        
        if request.method == 'POST':
            try:
                laps = int(request.form.get('laps', 0))
                course_length = int(request.form.get('course_length', 30))
                partial_distance = float(request.form.get('partial_distance', 0))
                
                pillar1.walk_6min_laps = laps
                pillar1.walk_6min_partial_m = Decimal(str(partial_distance))
                
                # Use model's built-in calculation
                pillar1.calculate_6min_walk_distance(course_length)
                
                # Calculate percent predicted
                height_cm = float(section0.height_cm) if section0 and section0.height_cm else 170
                weight_kg = float(section0.weight_kg) if section0 and section0.weight_kg else 70
                
                percent_predicted = calculate_6mwt_percent_predicted(
                    float(pillar1.walk_6min_total_m),
                    assessment.age_at_assessment,
                    height_cm,
                    weight_kg,
                    patient.sex
                )
                pillar1.walk_6min_pct_predicted = Decimal(str(percent_predicted))
                
                # Score
                result = score_6mwt(float(pillar1.walk_6min_total_m), assessment.age_at_assessment, patient.sex)
                
                pillar1.walk_6min_score = Decimal(str(result['score']))
                pillar1.walk_6min_category = result['category']
                
                session.commit()
                flash(f"6MWT saved: {pillar1.walk_6min_total_m} meters ({percent_predicted:.0f}% predicted), {result['score']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar1/walk_6min.html',
            assessment=assessment,
            patient=patient,
            pillar1=pillar1,
            section0=section0,
        )
    finally:
        session.close()


# =============================================================================
# CALCULATE TOTALS & GENERATE ALERTS
# =============================================================================

@bp.route('/<int:assessment_id>/pillar1/calculate-total', methods=['POST'])
def calculate_total(assessment_id: int):
    """Calculate Pillar 1 total score and generate alerts."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        patient = assessment.patient
        pillar1 = assessment.pillar1_results
        
        if not pillar1:
            return jsonify({'error': 'No Pillar 1 results found'}), 404
        
        # Use model's built-in calculations
        pillar1.calculate_pillar1_total()
        pillar1.calculate_functional_age_impact()
        alerts = pillar1.detect_clinical_alerts(assessment.age_at_assessment, patient.sex)
        
        session.commit()
        
        return jsonify({
            'total': {
                'total_score': float(pillar1.pillar1_total) if pillar1.pillar1_total else 0,
                'percentage': float(pillar1.pillar1_pct) if pillar1.pillar1_pct else 0,
                'category': pillar1.pillar1_category,
            },
            'age_impact': {
                'functional_age_modifier': pillar1.functional_age_impact,
                'interpretation': f"{'+' if pillar1.functional_age_impact and pillar1.functional_age_impact > 0 else ''}{pillar1.functional_age_impact} years" if pillar1.functional_age_impact else "No change",
            },
            'alerts': alerts,
        })
    finally:
        session.close()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_or_create_pillar1(session, assessment: Assessment) -> Pillar1Results:
    """Get existing Pillar 1 results or create new."""
    if assessment.pillar1_results:
        return assessment.pillar1_results
    
    pillar1 = Pillar1Results(assessment_id=assessment.id)
    session.add(pillar1)
    session.flush()
    return pillar1


def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    """Parse string to Decimal, returning None if empty."""
    if not value or value.strip() == '':
        return None
    try:
        return Decimal(value)
    except:
        return None
