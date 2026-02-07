"""
Pillar 4 Routes - Vitality & Hormones
======================================

Routes for Pillar 4 assessment:
- Overview dashboard
- 9 test routes (thyroid, hormones, sexual health, vitamin D, iron, exercise, sleep, appearance, stress)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session
from decimal import Decimal
from typing import Optional

from models import db
from models.assessment import Assessment
from models.patient import Patient
from models.pillar4 import Pillar4Results
from scoring.pillar4 import (
    score_thyroid_exact,
    score_thyroid_category,
    score_male_testosterone_exact,
    score_male_testosterone_category,
    score_female_hormones,
    score_sexual_health,
    score_vitamin_d_exact,
    score_vitamin_d_category,
    score_hemoglobin_exact,
    score_hemoglobin_category,
    score_exercise,
    score_sleep,
    score_appearance,
    score_stress,
)

bp = Blueprint('pillar4', __name__, url_prefix='/assessment')


# =============================================================================
# PILLAR 4 DASHBOARD / OVERVIEW
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4')
def overview(assessment_id: int):
    """Pillar 4 overview showing all tests and scores."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        
        # Get or create Pillar 4 results
        pillar4 = assessment.pillar4_results
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
            session.commit()
        
        # Calculate completion status
        tests_completed = sum([
            1 if pillar4.thyroid_points is not None else 0,
            1 if pillar4.hormone_points is not None else 0,
            1 if pillar4.sexual_health_points is not None else 0,
            1 if pillar4.vitd_points is not None else 0,
            1 if pillar4.iron_points is not None else 0,
            1 if pillar4.exercise_points is not None else 0,
            1 if pillar4.sleep_points is not None else 0,
            1 if pillar4.appearance_points is not None else 0,
            1 if pillar4.stress_points is not None else 0,
        ])
        
        return render_template(
            'pillar4/overview.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4,
            tests_completed=tests_completed,
            total_tests=9
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 1: THYROID FUNCTION
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/thyroid', methods=['GET', 'POST'])
def thyroid(assessment_id: int):
    """Thyroid function assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            input_mode = request.form.get('input_mode')
            pillar4.thyroid_input_mode = input_mode
            
            if input_mode == 'exact':
                tsh = float(request.form.get('tsh'))
                free_t4 = request.form.get('free_t4')
                free_t3 = request.form.get('free_t3')
                
                pillar4.tsh = Decimal(str(tsh))
                pillar4.free_t4 = Decimal(str(free_t4)) if free_t4 else None
                pillar4.free_t3 = Decimal(str(free_t3)) if free_t3 else None
                
                points, category = score_thyroid_exact(
                    tsh,
                    float(free_t4) if free_t4 else None,
                    float(free_t3) if free_t3 else None
                )
                
                pillar4.thyroid_points = points
                pillar4.thyroid_category = category
            
            else:  # category mode
                tsh_category = request.form.get('tsh_category')
                t3_t4_status = request.form.get('t3_t4_status')
                
                pillar4.thyroid_category_input = tsh_category
                pillar4.t3_t4_status = t3_t4_status
                
                points, category = score_thyroid_category(tsh_category, t3_t4_status)
                
                pillar4.thyroid_points = points
                pillar4.thyroid_category = category
            
            session.commit()
            flash('Thyroid assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/thyroid.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 2: SEX HORMONES (SEX-SPECIFIC)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/hormones', methods=['GET', 'POST'])
def hormones(assessment_id: int):
    """Sex hormone assessment (sex-specific)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            if patient.sex == 'male':
                # Male hormone scoring
                input_mode = request.form.get('input_mode')
                pillar4.hormone_input_mode = input_mode
                
                if input_mode == 'exact':
                    total_t = float(request.form.get('total_testosterone'))
                    free_t = request.form.get('free_testosterone')
                    estradiol = request.form.get('estradiol')
                    
                    pillar4.total_testosterone = Decimal(str(total_t))
                    pillar4.free_testosterone = Decimal(str(free_t)) if free_t else None
                    pillar4.estradiol_male = Decimal(str(estradiol)) if estradiol else None
                    
                    points, assessment_str = score_male_testosterone_exact(
                        total_t,
                        assessment.age_at_assessment,
                        float(free_t) if free_t else None,
                        float(estradiol) if estradiol else None
                    )
                    
                    pillar4.hormone_points = points
                    pillar4.hormone_assessment = assessment_str
                    pillar4.testosterone_category = assessment_str
                
                else:  # category mode
                    category = request.form.get('testosterone_category')
                    pillar4.testosterone_category = category
                    
                    points, assessment_str = score_male_testosterone_category(category)
                    
                    pillar4.hormone_points = points
                    pillar4.hormone_assessment = assessment_str
            
            else:  # female
                # Female hormone scoring
                input_mode = request.form.get('female_hormone_input_mode', 'symptoms')
                menopause_status = request.form.get('menopause_status')
                cycle_regularity = request.form.get('cycle_regularity')
                female_symptoms = request.form.get('female_symptoms')
                hormone_category = request.form.get('female_hormone_category', 'notTested')
                
                pillar4.female_hormone_input_mode = input_mode
                pillar4.menopause_status = menopause_status
                pillar4.cycle_regularity = cycle_regularity if menopause_status == 'pre' else None
                pillar4.female_symptoms = female_symptoms
                pillar4.female_hormone_category = hormone_category
                
                if input_mode == 'exact':
                    # Exact lab values mode
                    estradiol_f = request.form.get('estradiol_female')
                    progesterone = request.form.get('progesterone')
                    fsh = request.form.get('fsh')
                    lh = request.form.get('lh')
                    testosterone_f = request.form.get('testosterone_female')
                    amh = request.form.get('amh')
                    
                    # Save exact values
                    pillar4.estradiol_female = Decimal(str(estradiol_f)) if estradiol_f else None
                    pillar4.progesterone = Decimal(str(progesterone)) if progesterone else None
                    pillar4.fsh = Decimal(str(fsh)) if fsh else None
                    pillar4.lh = Decimal(str(lh)) if lh else None
                    pillar4.testosterone_female = Decimal(str(testosterone_f)) if testosterone_f else None
                    pillar4.amh = Decimal(str(amh)) if amh else None
                    
                    # Score with exact values
                    from scoring.pillar4 import score_female_hormones_exact
                    points, assessment_str = score_female_hormones_exact(
                        menopause_status,
                        assessment.age_at_assessment,
                        float(estradiol_f) if estradiol_f else None,
                        float(progesterone) if progesterone else None,
                        float(fsh) if fsh else None,
                        float(lh) if lh else None,
                        float(testosterone_f) if testosterone_f else None,
                        float(amh) if amh else None,
                        female_symptoms
                    )
                    
                    pillar4.hormone_points = points
                    pillar4.hormone_assessment = assessment_str
                
                else:  # symptoms mode
                    # Original symptom-based scoring
                    points, assessment_str = score_female_hormones(
                        menopause_status,
                        cycle_regularity if menopause_status == 'pre' else None,
                        female_symptoms,
                        hormone_category
                    )
                    
                    pillar4.hormone_points = points
                    pillar4.hormone_assessment = assessment_str
            
            session.commit()
            flash('Hormone assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/hormones.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 3: SEXUAL HEALTH (SEX-SPECIFIC)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/sexual-health', methods=['GET', 'POST'])
def sexual_health(assessment_id: int):
    """Sexual health assessment (sex-specific, optional)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            response = request.form.get('sexual_health')
            pillar4.sexual_health = response
            
            points, note = score_sexual_health(response)
            pillar4.sexual_health_points = points
            
            session.commit()
            flash('Sexual health assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/sexual_health.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 4: VITAMIN D
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/vitamin-d', methods=['GET', 'POST'])
def vitamin_d(assessment_id: int):
    """Vitamin D assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            input_mode = request.form.get('input_mode')
            pillar4.vitd_input_mode = input_mode
            
            if input_mode == 'exact':
                vitd = float(request.form.get('vitamin_d'))
                pillar4.vitamin_d = Decimal(str(vitd))
                
                points, category = score_vitamin_d_exact(vitd)
                
                pillar4.vitd_points = points
                pillar4.vitd_category = category
            
            else:  # category mode
                category = request.form.get('vitd_category')
                pillar4.vitd_category_input = category
                
                points, category_str = score_vitamin_d_category(category)
                
                pillar4.vitd_points = points
                pillar4.vitd_category = category_str
            
            session.commit()
            flash('Vitamin D assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/vitamin_d.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 5: HEMOGLOBIN & IRON (SEX-ADJUSTED)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/iron', methods=['GET', 'POST'])
def iron(assessment_id: int):
    """Hemoglobin & iron assessment (sex-adjusted)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            input_mode = request.form.get('input_mode')
            pillar4.iron_input_mode = input_mode
            
            if input_mode == 'exact':
                hb = float(request.form.get('hemoglobin'))
                ferritin = request.form.get('ferritin')
                
                pillar4.hemoglobin = Decimal(str(hb))
                pillar4.ferritin = Decimal(str(ferritin)) if ferritin else None
                
                points, category = score_hemoglobin_exact(
                    hb,
                    patient.sex,
                    float(ferritin) if ferritin else None
                )
                
                pillar4.iron_points = points
                pillar4.iron_category = category
            
            else:  # category mode
                category = request.form.get('iron_category')
                pillar4.iron_category_input = category
                
                points, category_str = score_hemoglobin_category(category)
                
                pillar4.iron_points = points
                pillar4.iron_category = category_str
            
            session.commit()
            flash('Iron/hemoglobin assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/iron.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 6: EXERCISE HABITS
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/exercise', methods=['GET', 'POST'])
def exercise(assessment_id: int):
    """Exercise habits assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            frequency = request.form.get('exercise_frequency')
            cardio = request.form.get('exercise_cardio') == 'on'
            strength = request.form.get('exercise_strength') == 'on'
            flexibility = request.form.get('exercise_flexibility') == 'on'
            
            pillar4.exercise_frequency = frequency
            pillar4.exercise_cardio = cardio
            pillar4.exercise_strength = strength
            pillar4.exercise_flexibility = flexibility
            
            types_count = sum([cardio, strength, flexibility])
            points, category = score_exercise(frequency, types_count)
            
            pillar4.exercise_points = points
            
            session.commit()
            flash('Exercise assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/exercise.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 7: SLEEP DURATION & QUALITY
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/sleep', methods=['GET', 'POST'])
def sleep(assessment_id: int):
    """Sleep assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            duration = request.form.get('sleep_duration')
            quality = request.form.get('sleep_quality')
            onset = request.form.get('sleep_onset')
            
            pillar4.sleep_duration = duration
            pillar4.sleep_quality = quality
            pillar4.sleep_onset = onset
            
            points, category = score_sleep(duration, quality, onset)
            
            pillar4.sleep_points = points
            
            session.commit()
            flash('Sleep assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/sleep.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 8: SKIN & HAIR HEALTH
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/appearance', methods=['GET', 'POST'])
def appearance(assessment_id: int):
    """Skin and hair health assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            skin_elasticity = request.form.get('skin_elasticity')
            hair_health = request.form.get('hair_health')
            
            pillar4.skin_elasticity = skin_elasticity
            pillar4.hair_health = hair_health
            
            points, note = score_appearance(skin_elasticity, hair_health)
            
            pillar4.appearance_points = points
            
            session.commit()
            flash('Skin & hair assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/appearance.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# TEST 9: STRESS & OVERWHELM
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/stress', methods=['GET', 'POST'])
def stress(assessment_id: int):
    """Stress level assessment."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar4 = assessment.pillar4_results
        
        if not pillar4:
            pillar4 = Pillar4Results(assessment_id=assessment_id)
            assessment.pillar4_results = pillar4
            session.add(pillar4)
        
        if request.method == 'POST':
            level = int(request.form.get('stress_level'))
            
            pillar4.stress_level = level
            
            points, category = score_stress(level)
            
            pillar4.stress_points = points
            pillar4.stress_category = category
            
            session.commit()
            flash('Stress assessment saved!', 'success')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        return render_template(
            'pillar4/stress.html',
            assessment=assessment,
            patient=patient,
            pillar4=pillar4
        )
    
    finally:
        session.close()


# =============================================================================
# CALCULATE PILLAR 4 TOTAL
# =============================================================================

@bp.route('/<int:assessment_id>/pillar4/calculate-total', methods=['POST'])
def calculate_total(assessment_id: int):
    """Calculate total Pillar 4 score."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment or not assessment.pillar4_results:
            flash('Pillar 4 not found', 'error')
            return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
        
        pillar4 = assessment.pillar4_results
        
        # Calculate totals
        pillar4.calculate_pillar4_total()
        pillar4.calculate_functional_age_modifier()
        pillar4.detect_clinical_alerts()
        
        session.commit()
        
        flash(f'Pillar 4 total calculated: {pillar4.pillar4_total}/20 ({pillar4.pillar4_category})', 'success')
        return redirect(url_for('pillar4.overview', assessment_id=assessment_id))
    
    finally:
        session.close()
