"""
Pillar 3 Routes - Metabolic & Digestive Health
===============================================

Routes for all 5 test components.
Maximum 20 points total.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from decimal import Decimal
from typing import Optional

from models import db
from models.assessment import Assessment
from models.patient import Patient
from models.pillar3 import Pillar3Results
from scoring.pillar3 import (
    score_glucose_exact,
    score_glucose_category,
    score_post_meal_feeling,
    score_fasting_tolerance,
    score_bowel_frequency,
    score_stool_consistency,
    score_reflux_frequency,
    score_meal_comfort,
    score_bloating_frequency,
    score_abdominal_pain,
    score_food_intolerances,
    score_liver_exact,
    score_liver_category,
    score_crp_exact,
    score_crp_category,
)

bp = Blueprint('pillar3', __name__, url_prefix='/assessment')


# =============================================================================
# PILLAR 3 DASHBOARD / OVERVIEW
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3')
def overview(assessment_id: int):
    """Pillar 3 overview showing all tests and scores."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar3 = assessment.pillar3_results
        
        # Calculate test completion status
        tests_complete = {
            'glucose': pillar3 and pillar3.glucose_total_points is not None,
            'digestive': pillar3 and pillar3.digestive_total_points is not None,
            'gut_symptoms': pillar3 and pillar3.gut_symptoms_total_points is not None,
            'liver': pillar3 and pillar3.liver_points is not None,
            'inflammation': pillar3 and pillar3.crp_points is not None,
        }
        
        completed_count = sum(1 for v in tests_complete.values() if v)
        
        return render_template(
            'pillar3/overview.html',
            assessment=assessment,
            patient=patient,
            pillar3=pillar3,
            tests_complete=tests_complete,
            completed_count=completed_count,
        )
    finally:
        session.close()


# =============================================================================
# TEST 1: GLUCOSE METABOLISM & ENERGY (5 points)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3/glucose', methods=['GET', 'POST'])
def glucose(assessment_id: int):
    """Glucose metabolism and energy test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar3 = _get_or_create_pillar3(session, assessment)
        
        if request.method == 'POST':
            try:
                # Get input mode
                input_mode = request.form.get('input_mode', 'exact')
                pillar3.glucose_input_mode = input_mode
                
                # Part A: Blood Glucose Control (3 pts)
                if input_mode == 'exact':
                    glucose_value = float(request.form.get('fasting_glucose', 0))
                    hba1c_value = float(request.form.get('hba1c', 0))
                    
                    pillar3.fasting_glucose = Decimal(str(glucose_value))
                    pillar3.hba1c = Decimal(str(hba1c_value))
                    
                    result = score_glucose_exact(glucose_value, hba1c_value)
                    pillar3.glucose_blood_points = Decimal(str(result['points']))
                    pillar3.glucose_blood_category = result['category']
                else:
                    category = request.form.get('glucose_category')
                    pillar3.glucose_category = category
                    
                    result = score_glucose_category(category)
                    pillar3.glucose_blood_points = Decimal(str(result['points']))
                    pillar3.glucose_blood_category = result['category']
                
                # Part B: Functional Energy (2 pts)
                post_meal = request.form.get('post_meal_feeling')
                fasting_tol = request.form.get('fasting_tolerance')
                
                pillar3.post_meal_feeling = post_meal
                pillar3.fasting_tolerance = fasting_tol
                
                meal_result = score_post_meal_feeling(post_meal)
                fast_result = score_fasting_tolerance(fasting_tol)
                
                functional_points = meal_result['points'] + fast_result['points']
                pillar3.glucose_functional_points = Decimal(str(functional_points))
                
                # Calculate total glucose score
                pillar3.calculate_glucose_total()
                
                session.commit()
                flash(f"Glucose test saved: {pillar3.glucose_total_points}/5.0 points", 'success')
                
                return redirect(url_for('pillar3.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar3/glucose.html',
            assessment=assessment,
            patient=patient,
            pillar3=pillar3,
        )
    finally:
        session.close()


# =============================================================================
# TEST 2: DIGESTIVE FUNCTION (6 points)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3/digestive', methods=['GET', 'POST'])
def digestive(assessment_id: int):
    """Digestive function test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar3 = _get_or_create_pillar3(session, assessment)
        
        if request.method == 'POST':
            try:
                # Bowel frequency (2 pts)
                bowel_freq = request.form.get('bowel_frequency')
                pillar3.bowel_frequency = bowel_freq
                bowel_result = score_bowel_frequency(bowel_freq)
                pillar3.bowel_points = Decimal(str(bowel_result['points']))
                
                # Stool consistency (1 pt)
                stool = request.form.get('stool_consistency')
                pillar3.stool_consistency = stool
                stool_result = score_stool_consistency(stool)
                pillar3.stool_points = Decimal(str(stool_result['points']))
                
                # Reflux frequency (2 pts)
                reflux = request.form.get('reflux_frequency')
                pillar3.reflux_frequency = reflux
                reflux_result = score_reflux_frequency(reflux)
                pillar3.reflux_points = Decimal(str(reflux_result['points']))
                
                # Meal comfort (1 pt)
                comfort = request.form.get('meal_comfort')
                pillar3.meal_comfort = comfort
                comfort_result = score_meal_comfort(comfort)
                pillar3.meal_comfort_points = Decimal(str(comfort_result['points']))
                
                # Calculate total digestive score
                pillar3.calculate_digestive_total()
                
                session.commit()
                flash(f"Digestive function saved: {pillar3.digestive_total_points}/6.0 points", 'success')
                
                return redirect(url_for('pillar3.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar3/digestive.html',
            assessment=assessment,
            patient=patient,
            pillar3=pillar3,
        )
    finally:
        session.close()


# =============================================================================
# TEST 3: GUT SYMPTOMS (4 points)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3/gut-symptoms', methods=['GET', 'POST'])
def gut_symptoms(assessment_id: int):
    """Gut symptoms test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar3 = _get_or_create_pillar3(session, assessment)
        
        if request.method == 'POST':
            try:
                # Bloating/gas (2 pts)
                bloating = request.form.get('bloating_frequency')
                pillar3.bloating_frequency = bloating
                bloating_result = score_bloating_frequency(bloating)
                pillar3.bloating_points = Decimal(str(bloating_result['points']))
                
                # Abdominal pain (1 pt)
                pain = request.form.get('abdominal_pain')
                pillar3.abdominal_pain = pain
                pain_result = score_abdominal_pain(pain)
                pillar3.pain_points = Decimal(str(pain_result['points']))
                
                # Food intolerances (1 pt)
                intolerances = request.form.get('food_intolerances')
                pillar3.food_intolerances = intolerances
                intol_result = score_food_intolerances(intolerances)
                pillar3.intolerance_points = Decimal(str(intol_result['points']))
                
                # Calculate total gut symptoms score
                pillar3.calculate_gut_symptoms_total()
                
                session.commit()
                flash(f"Gut symptoms saved: {pillar3.gut_symptoms_total_points}/4.0 points", 'success')
                
                return redirect(url_for('pillar3.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar3/gut_symptoms.html',
            assessment=assessment,
            patient=patient,
            pillar3=pillar3,
        )
    finally:
        session.close()


# =============================================================================
# TEST 4: LIVER FUNCTION (3 points)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3/liver', methods=['GET', 'POST'])
def liver(assessment_id: int):
    """Liver function test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar3 = _get_or_create_pillar3(session, assessment)
        
        if request.method == 'POST':
            try:
                # Get input mode
                input_mode = request.form.get('input_mode', 'exact')
                pillar3.liver_input_mode = input_mode
                
                if input_mode == 'exact':
                    alt_value = float(request.form.get('alt_value', 0))
                    ast_value = float(request.form.get('ast_value', 0))
                    
                    pillar3.alt_value = Decimal(str(alt_value))
                    pillar3.ast_value = Decimal(str(ast_value))
                    
                    result = score_liver_exact(alt_value, ast_value, patient.sex)
                    pillar3.liver_points = Decimal(str(result['points']))
                    pillar3.liver_category = result['category']
                else:
                    category = request.form.get('liver_category')
                    pillar3.liver_category_input = category
                    
                    result = score_liver_category(category)
                    pillar3.liver_points = Decimal(str(result['points']))
                    pillar3.liver_category = result['category']
                
                session.commit()
                flash(f"Liver function saved: {pillar3.liver_points}/3.0 points ({pillar3.liver_category})", 'success')
                
                return redirect(url_for('pillar3.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar3/liver.html',
            assessment=assessment,
            patient=patient,
            pillar3=pillar3,
        )
    finally:
        session.close()


# =============================================================================
# TEST 5: METABOLIC INFLAMMATION (2 points)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3/inflammation', methods=['GET', 'POST'])
def inflammation(assessment_id: int):
    """Metabolic inflammation test (hs-CRP)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar3 = _get_or_create_pillar3(session, assessment)
        
        if request.method == 'POST':
            try:
                # Get input mode
                input_mode = request.form.get('input_mode', 'exact')
                pillar3.crp_input_mode = input_mode
                
                if input_mode == 'exact':
                    crp_value = float(request.form.get('hs_crp', 0))
                    pillar3.hs_crp = Decimal(str(crp_value))
                    
                    result = score_crp_exact(crp_value)
                    pillar3.crp_points = Decimal(str(result['points']))
                    pillar3.crp_risk_level = result['risk_level']
                else:
                    category = request.form.get('crp_category')
                    pillar3.crp_category_input = category
                    
                    result = score_crp_category(category)
                    pillar3.crp_points = Decimal(str(result['points']))
                    pillar3.crp_risk_level = result['risk_level']
                
                session.commit()
                flash(f"hs-CRP saved: {pillar3.crp_points}/2.0 points ({pillar3.crp_risk_level})", 'success')
                
                return redirect(url_for('pillar3.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar3/inflammation.html',
            assessment=assessment,
            patient=patient,
            pillar3=pillar3,
        )
    finally:
        session.close()


# =============================================================================
# CALCULATE TOTALS & GENERATE ALERTS
# =============================================================================

@bp.route('/<int:assessment_id>/pillar3/calculate-total', methods=['POST'])
def calculate_total(assessment_id: int):
    """Calculate Pillar 3 total score and generate alerts."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        pillar3 = assessment.pillar3_results
        
        if not pillar3:
            return jsonify({'error': 'No Pillar 3 results found'}), 404
        
        pillar3.calculate_pillar3_total()
        pillar3.calculate_functional_age_modifier()
        alerts = pillar3.detect_clinical_alerts()
        
        session.commit()
        
        return jsonify({
            'total': {
                'total_score': float(pillar3.pillar3_total) if pillar3.pillar3_total else 0,
                'percentage': float(pillar3.pillar3_pct) if pillar3.pillar3_pct else 0,
                'category': pillar3.pillar3_category,
            },
            'age_impact': {
                'functional_age_modifier': float(pillar3.functional_age_modifier) if pillar3.functional_age_modifier else 0,
                'interpretation': f"{'+' if pillar3.functional_age_modifier and float(pillar3.functional_age_modifier) > 0 else ''}{pillar3.functional_age_modifier} years" if pillar3.functional_age_modifier else "No change",
            },
            'alerts': alerts,
        })
    finally:
        session.close()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_or_create_pillar3(session, assessment: Assessment) -> Pillar3Results:
    """Get existing Pillar 3 results or create new."""
    if assessment.pillar3_results:
        return assessment.pillar3_results
    
    pillar3 = Pillar3Results(assessment_id=assessment.id)
    session.add(pillar3)
    session.flush()
    return pillar3
