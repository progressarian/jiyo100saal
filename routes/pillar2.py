"""
Pillar 2 Routes - Cognitive Function
=====================================

Routes for all 11 cognitive test components.
Maximum 20 points total.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from decimal import Decimal
from typing import Optional

from models import db
from models.assessment import Assessment
from models.patient import Patient
from models.pillar2 import Pillar2Results
from scoring.pillar2 import (
    score_memory_recall,
    calculate_retention_rate,
    score_digit_span,
    score_digit_span_forward,
    score_digit_span_backward,
    score_trails_a,
    score_trails_b,
    calculate_trails_ba_ratio,
    score_dsst,
    score_clock_drawing,
    score_verbal_fluency,
    score_phq2,
    score_gad2,
    MEMORY_WORD_LIST,
)

bp = Blueprint('pillar2', __name__, url_prefix='/assessment')


# =============================================================================
# PILLAR 2 DASHBOARD / OVERVIEW
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2')
def overview(assessment_id: int):
    """Pillar 2 overview showing all tests and scores."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = assessment.pillar2_results
        
        # Calculate test completion status
        tests_complete = {
            'memory': pillar2 and pillar2.memory_immediate_count is not None and pillar2.memory_delayed_count is not None,
            'digit_span': pillar2 and pillar2.digit_span_forward is not None and pillar2.digit_span_backward is not None,
            'trails': pillar2 and pillar2.trails_a_time is not None and pillar2.trails_b_time is not None,
            'dsst': pillar2 and pillar2.dsst_score is not None,
            'clock': pillar2 and pillar2.clock_score_raw is not None,
            'verbal_fluency': pillar2 and pillar2.verbal_fluency_animals is not None,
            'mental_health': pillar2 and pillar2.phq2_total is not None and pillar2.gad2_total is not None,
        }
        
        completed_count = sum(1 for v in tests_complete.values() if v)
        
        return render_template(
            'pillar2/overview.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
            tests_complete=tests_complete,
            completed_count=completed_count,
        )
    finally:
        session.close()


# =============================================================================
# TEST 1 & 2: MEMORY - IMMEDIATE & DELAYED WORD RECALL
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/memory', methods=['GET', 'POST'])
def memory(assessment_id: int):
    """Word Recall Memory Tests (Immediate & Delayed)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                test_phase = request.form.get('test_phase', 'immediate')
                
                if test_phase == 'immediate':
                    # Save immediate recall results
                    pillar2.memory_immediate_word1 = request.form.get('word1') == 'on'
                    pillar2.memory_immediate_word2 = request.form.get('word2') == 'on'
                    pillar2.memory_immediate_word3 = request.form.get('word3') == 'on'
                    pillar2.memory_immediate_word4 = request.form.get('word4') == 'on'
                    pillar2.memory_immediate_word5 = request.form.get('word5') == 'on'
                    pillar2.memory_immediate_word6 = request.form.get('word6') == 'on'
                    pillar2.memory_immediate_word7 = request.form.get('word7') == 'on'
                    pillar2.memory_immediate_word8 = request.form.get('word8') == 'on'
                    pillar2.memory_immediate_word9 = request.form.get('word9') == 'on'
                    pillar2.memory_immediate_word10 = request.form.get('word10') == 'on'
                    
                    count = pillar2.calculate_immediate_memory_count()
                    result = score_memory_recall(count, assessment.age_at_assessment)
                    
                    pillar2.memory_immediate_points = Decimal(str(result['points']))
                    pillar2.memory_immediate_category = result['category']
                    
                    session.commit()
                    flash(f"Immediate recall saved: {count}/10 words, {result['points']} points ({result['category']})", 'success')
                    
                elif test_phase == 'delayed':
                    # Save delayed recall results
                    pillar2.memory_delayed_word1 = request.form.get('word1') == 'on'
                    pillar2.memory_delayed_word2 = request.form.get('word2') == 'on'
                    pillar2.memory_delayed_word3 = request.form.get('word3') == 'on'
                    pillar2.memory_delayed_word4 = request.form.get('word4') == 'on'
                    pillar2.memory_delayed_word5 = request.form.get('word5') == 'on'
                    pillar2.memory_delayed_word6 = request.form.get('word6') == 'on'
                    pillar2.memory_delayed_word7 = request.form.get('word7') == 'on'
                    pillar2.memory_delayed_word8 = request.form.get('word8') == 'on'
                    pillar2.memory_delayed_word9 = request.form.get('word9') == 'on'
                    pillar2.memory_delayed_word10 = request.form.get('word10') == 'on'
                    
                    count = pillar2.calculate_delayed_memory_count()
                    result = score_memory_recall(count, assessment.age_at_assessment)
                    
                    pillar2.memory_delayed_points = Decimal(str(result['points']))
                    pillar2.memory_delayed_category = result['category']
                    
                    # Calculate retention rate
                    pillar2.calculate_retention_rate()
                    
                    session.commit()
                    
                    msg = f"Delayed recall saved: {count}/10 words, {result['points']} points ({result['category']})"
                    if pillar2.memory_retention_pct is not None:
                        msg += f" | Retention: {pillar2.memory_retention_pct}%"
                        if pillar2.memory_retention_flag:
                            msg += " ⚠️ LOW RETENTION"
                    flash(msg, 'success')
                    
                    return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/memory.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
            word_list=MEMORY_WORD_LIST,
        )
    finally:
        session.close()


# =============================================================================
# TEST 3 & 4: DIGIT SPAN (Forward & Backward)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/digit-span', methods=['GET', 'POST'])
def digit_span(assessment_id: int):
    """Digit Span Test (Forward & Backward)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                forward_raw = request.form.get('digit_span_forward', '').strip()
                backward_raw = request.form.get('digit_span_backward', '').strip()
                
                forward = int(forward_raw) if forward_raw else 0
                backward = int(backward_raw) if backward_raw else 0
                
                if forward < 0 or backward < 0:
                    flash('Digit span values cannot be negative', 'error')
                    return redirect(url_for('pillar2.digit_span', assessment_id=assessment_id))
                
                # Store raw data
                pillar2.digit_span_forward = forward
                pillar2.digit_span_backward = backward
                pillar2.calculate_digit_span_total()
                
                # Calculate separate scores
                fwd_result = score_digit_span_forward(forward)
                bwd_result = score_digit_span_backward(backward)
                
                pillar2.digit_span_forward_points = Decimal(str(fwd_result['points']))
                pillar2.digit_span_forward_category = fwd_result['category']
                pillar2.digit_span_backward_points = Decimal(str(bwd_result['points']))
                pillar2.digit_span_backward_category = bwd_result['category']
                
                # Combined score
                combined = score_digit_span(forward, backward, assessment.age_at_assessment)
                pillar2.digit_span_points = Decimal(str(combined['points']))
                pillar2.digit_span_category = combined['category']
                
                if combined['total'] < 10:
                    pillar2.memory_deficit_flag = True
                
                session.commit()
                flash(f"Digit Span saved: Forward={forward} ({fwd_result['points']}pt), Backward={backward} ({bwd_result['points']}pt), Total={combined['total']} ({combined['category']})", 'success')
                
                return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/digit_span.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
        )
    finally:
        session.close()


# =============================================================================
# TEST 5 & 6: TRAIL MAKING TESTS A & B
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/trails', methods=['GET', 'POST'])
def trails(assessment_id: int):
    """Trail Making Tests A & B."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                trails_a_time = float(request.form.get('trails_a_time', 0))
                trails_b_time = float(request.form.get('trails_b_time', 0))
                trails_a_errors = int(request.form.get('trails_a_errors', 0) or 0)
                trails_b_errors = int(request.form.get('trails_b_errors', 0) or 0)
                
                if trails_a_time <= 0 or trails_b_time <= 0:
                    flash('Please enter valid times for both tests', 'error')
                    return redirect(url_for('pillar2.trails', assessment_id=assessment_id))
                
                pillar2.trails_a_time = Decimal(str(trails_a_time))
                pillar2.trails_b_time = Decimal(str(trails_b_time))
                pillar2.trails_a_errors = trails_a_errors
                pillar2.trails_b_errors = trails_b_errors
                
                result_a = score_trails_a(trails_a_time, assessment.age_at_assessment)
                result_b = score_trails_b(trails_b_time, assessment.age_at_assessment)
                ba_ratio = calculate_trails_ba_ratio(trails_a_time, trails_b_time)
                
                pillar2.trails_a_points = Decimal(str(result_a['points']))
                pillar2.trails_a_category = result_a['category']
                pillar2.trails_b_points = Decimal(str(result_b['points']))
                pillar2.trails_b_category = result_b['category']
                
                pillar2.calculate_trails_ratio()
                pillar2.calculate_trails_total()
                
                if ba_ratio.get('level') in ('moderate', 'severe'):
                    pillar2.executive_dysfunction_flag = True
                
                session.commit()
                
                msg = f"Trails saved: A={trails_a_time}s ({result_a['points']}pts), B={trails_b_time}s ({result_b['points']}pts)"
                if ba_ratio.get('ratio'):
                    msg += f", B/A={ba_ratio['ratio']}"
                flash(msg, 'success')
                
                return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/trails.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
        )
    finally:
        session.close()


# =============================================================================
# TEST 7: DSST - DIGITAL SYMBOL SUBSTITUTION
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/dsst', methods=['GET', 'POST'])
def dsst(assessment_id: int):
    """Digital Symbol Substitution Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                dsst_raw = request.form.get('dsst_score', '').strip()
                score = int(dsst_raw) if dsst_raw else 0
                
                if score < 0:
                    flash('Score cannot be negative', 'error')
                    return redirect(url_for('pillar2.dsst', assessment_id=assessment_id))
                
                result = score_dsst(score, assessment.age_at_assessment, patient.sex)
                
                pillar2.dsst_score = score
                pillar2.dsst_points = Decimal(str(result['points']))
                pillar2.dsst_category = result['category']
                
                session.commit()
                flash(f"DSST saved: {score} correct, {result['points']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/dsst.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
        )
    finally:
        session.close()


# =============================================================================
# TEST 8: CLOCK DRAWING TEST
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/clock-drawing', methods=['GET', 'POST'])
def clock_drawing(assessment_id: int):
    """Clock Drawing Test."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                # Get component scores
                pillar2.clock_circle_intact = request.form.get('circle_intact') == 'on'
                pillar2.clock_numbers_present = request.form.get('numbers_present') == 'on'
                pillar2.clock_numbers_sequence = request.form.get('numbers_sequence') == 'on'
                pillar2.clock_numbers_position = request.form.get('numbers_position') == 'on'
                pillar2.clock_hands_present = request.form.get('hands_present') == 'on'
                pillar2.clock_hands_correct_time = request.form.get('hands_correct_time') == 'on'
                pillar2.clock_hands_proportion = request.form.get('hands_proportion') == 'on'
                pillar2.clock_notes = request.form.get('notes', '')
                
                raw_score = pillar2.calculate_clock_raw_score()
                result = score_clock_drawing(raw_score)
                
                pillar2.clock_points = Decimal(str(result['points']))
                pillar2.clock_category = result['category']
                
                if raw_score <= 3:
                    pillar2.cognitive_concern_flag = True
                
                session.commit()
                flash(f"Clock Drawing saved: {raw_score}/7 components, {result['points']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/clock_drawing.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
        )
    finally:
        session.close()


# =============================================================================
# TEST 9: VERBAL FLUENCY (ANIMALS)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/verbal-fluency', methods=['GET', 'POST'])
def verbal_fluency(assessment_id: int):
    """Verbal Fluency Test - Animals."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                animals_raw = request.form.get('verbal_fluency_animals', '').strip()
                animals = int(animals_raw) if animals_raw else 0
                repetitions = int(request.form.get('repetitions', 0) or 0)
                intrusions = int(request.form.get('intrusions', 0) or 0)
                
                if animals < 0:
                    flash('Animal count cannot be negative', 'error')
                    return redirect(url_for('pillar2.verbal_fluency', assessment_id=assessment_id))
                
                pillar2.verbal_fluency_animals = animals
                pillar2.verbal_fluency_repetitions = repetitions
                pillar2.verbal_fluency_intrusions = intrusions
                
                result = score_verbal_fluency(animals, assessment.age_at_assessment)
                
                pillar2.verbal_fluency_points = Decimal(str(result['points']))
                pillar2.verbal_fluency_category = result['category']
                
                if animals < 12:
                    pillar2.language_concern_flag = True
                
                session.commit()
                flash(f"Verbal Fluency saved: {animals} animals, {result['points']} points ({result['category']})", 'success')
                
                return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/verbal_fluency.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
        )
    finally:
        session.close()


# =============================================================================
# TEST 10 & 11: MENTAL HEALTH SCREENING (PHQ-2 & GAD-2)
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/mental-health', methods=['GET', 'POST'])
def mental_health(assessment_id: int):
    """Mental Health Screening (PHQ-2 & GAD-2)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        patient = assessment.patient
        pillar2 = _get_or_create_pillar2(session, assessment)
        
        if request.method == 'POST':
            try:
                # PHQ-2
                phq2_interest = int(request.form.get('phq2_interest', 0))
                phq2_depressed = int(request.form.get('phq2_depressed', 0))
                
                # GAD-2
                gad2_nervous = int(request.form.get('gad2_nervous', 0))
                gad2_worry = int(request.form.get('gad2_worry', 0))
                
                # Store values
                pillar2.phq2_interest = phq2_interest
                pillar2.phq2_depressed = phq2_depressed
                pillar2.gad2_nervous = gad2_nervous
                pillar2.gad2_worry = gad2_worry
                
                # Calculate totals
                pillar2.calculate_phq2_total()
                pillar2.calculate_gad2_total()
                
                # Score
                phq2_result = score_phq2(pillar2.phq2_total)
                gad2_result = score_gad2(pillar2.gad2_total)
                
                pillar2.phq2_points = Decimal(str(phq2_result['points']))
                pillar2.phq2_category = phq2_result['category']
                pillar2.gad2_points = Decimal(str(gad2_result['points']))
                pillar2.gad2_category = gad2_result['category']
                
                # Set flags
                if pillar2.phq2_followup_flag or pillar2.phq2_urgent_flag:
                    pillar2.depression_flag = True
                if pillar2.gad2_followup_flag or pillar2.gad2_urgent_flag:
                    pillar2.anxiety_flag = True
                
                session.commit()
                
                msg = f"Mental Health saved: PHQ-2={pillar2.phq2_total}/6 ({phq2_result['category']}), GAD-2={pillar2.gad2_total}/6 ({gad2_result['category']})"
                if pillar2.phq2_urgent_flag or pillar2.gad2_urgent_flag:
                    msg += " ⚠️ URGENT FOLLOW-UP NEEDED"
                elif pillar2.phq2_followup_flag or pillar2.gad2_followup_flag:
                    msg += " - Follow-up recommended"
                flash(msg, 'success')
                
                return redirect(url_for('pillar2.overview', assessment_id=assessment_id))
                
            except (ValueError, TypeError) as e:
                flash(f'Invalid input: {e}', 'error')
        
        return render_template(
            'pillar2/mental_health.html',
            assessment=assessment,
            patient=patient,
            pillar2=pillar2,
        )
    finally:
        session.close()


# =============================================================================
# CALCULATE TOTALS & GENERATE ALERTS
# =============================================================================

@bp.route('/<int:assessment_id>/pillar2/calculate-total', methods=['POST'])
def calculate_total(assessment_id: int):
    """Calculate Pillar 2 total score and generate alerts."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        patient = assessment.patient
        pillar2 = assessment.pillar2_results
        
        if not pillar2:
            return jsonify({'error': 'No Pillar 2 results found'}), 404
        
        pillar2.calculate_pillar2_total()
        pillar2.calculate_functional_age_modifier()
        alerts = pillar2.detect_clinical_alerts(assessment.age_at_assessment, patient.sex)
        
        session.commit()
        
        return jsonify({
            'total': {
                'total_score': float(pillar2.pillar2_total) if pillar2.pillar2_total else 0,
                'percentage': float(pillar2.pillar2_pct) if pillar2.pillar2_pct else 0,
                'category': pillar2.pillar2_category,
            },
            'age_impact': {
                'functional_age_modifier': float(pillar2.functional_age_modifier) if pillar2.functional_age_modifier else 0,
                'interpretation': f"{'+' if pillar2.functional_age_modifier and float(pillar2.functional_age_modifier) > 0 else ''}{pillar2.functional_age_modifier} years" if pillar2.functional_age_modifier else "No change",
            },
            'alerts': alerts,
        })
    finally:
        session.close()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_or_create_pillar2(session, assessment: Assessment) -> Pillar2Results:
    """Get existing Pillar 2 results or create new."""
    if assessment.pillar2_results:
        return assessment.pillar2_results
    
    pillar2 = Pillar2Results(assessment_id=assessment.id)
    session.add(pillar2)
    session.flush()
    return pillar2
