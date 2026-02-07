"""
Pillar 5 Routes - Disease Prevention & Clinical Biomarkers
===========================================================

10 routes for all 9 test components.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from decimal import Decimal

from models import db
from models.assessment import Assessment
from models.pillar5 import Pillar5Results
from scoring.pillar5 import (
    score_ldl, score_hdl, score_triglycerides, score_ratio,
    score_apob, score_lp_a, score_cac, score_tmt, score_echo_ct,
    score_kidney_exact, score_kidney_category, score_cancer_screening,
    score_organ_imaging, score_bone, score_vision, score_hearing,
    score_chronic_disease
)

bp = Blueprint('pillar5', __name__, url_prefix='/assessment')


@bp.route('/<int:assessment_id>/pillar5', methods=['GET'])
def overview(assessment_id):
    """Pillar 5 overview - all 9 tests."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = session.query(Pillar5Results).filter_by(
            assessment_id=assessment_id
        ).first()
        
        if not pillar5:
            pillar5 = Pillar5Results(assessment_id=assessment_id)
            session.add(pillar5)
            session.commit()
        
        return render_template('pillar5/overview.html', 
                             assessment=assessment,
                             patient=assessment.patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/lipids', methods=['GET', 'POST'])
def lipids(assessment_id):
    """Standard lipid panel - dual input mode."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        patient = assessment.patient
        
        if request.method == 'POST':
            input_mode = request.form.get('input_mode', 'exact')
            pillar5.lipids_input_mode = input_mode
            
            if input_mode == 'exact':
                # Exact values
                ldl = request.form.get('ldl_cholesterol')
                hdl = request.form.get('hdl_cholesterol')
                tg = request.form.get('triglycerides')
                
                if ldl and hdl and tg:
                    pillar5.ldl_cholesterol = Decimal(ldl)
                    pillar5.hdl_cholesterol = Decimal(hdl)
                    pillar5.triglycerides = Decimal(tg)
                    
                    # Auto-calculate total cholesterol and ratio
                    pillar5.calculate_total_cholesterol()
                    pillar5.calculate_total_hdl_ratio()
                    
                    # Score each component
                    ldl_pts, ldl_cat = score_ldl(float(ldl))
                    pillar5.ldl_points = ldl_pts
                    
                    hdl_pts, hdl_cat = score_hdl(float(hdl), patient.sex)
                    pillar5.hdl_points = hdl_pts
                    
                    tg_pts, tg_cat = score_triglycerides(float(tg))
                    pillar5.triglycerides_points = tg_pts
                    
                    ratio_pts, ratio_cat = score_ratio(float(pillar5.total_hdl_ratio))
                    pillar5.ratio_points = ratio_pts
                    
                    # Total lipids score
                    pillar5.lipids_total_points = ldl_pts + hdl_pts + tg_pts + ratio_pts
                    
                    # Category
                    lipids_total = float(pillar5.lipids_total_points)
                    if lipids_total >= 3.6:
                        pillar5.lipids_category = 'Excellent'
                    elif lipids_total >= 2.8:
                        pillar5.lipids_category = 'Good'
                    elif lipids_total >= 2.0:
                        pillar5.lipids_category = 'Acceptable'
                    else:
                        pillar5.lipids_category = 'Poor'
            
            else:  # category
                category = request.form.get('lipids_category')
                pillar5.lipids_category_input = category
                
                # Score based on category
                if category == 'optimal':
                    pillar5.lipids_total_points = Decimal('4.0')
                    pillar5.lipids_category = 'Excellent'
                elif category == 'good':
                    pillar5.lipids_total_points = Decimal('3.2')
                    pillar5.lipids_category = 'Good'
                elif category == 'acceptable':
                    pillar5.lipids_total_points = Decimal('2.4')
                    pillar5.lipids_category = 'Acceptable'
                elif category == 'borderline':
                    pillar5.lipids_total_points = Decimal('1.6')
                    pillar5.lipids_category = 'Borderline'
                else:  # high risk
                    pillar5.lipids_total_points = Decimal('0.8')
                    pillar5.lipids_category = 'High Risk'
            
            session.commit()
            flash('Lipid panel results saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/lipids.html',
                             assessment=assessment,
                             patient=patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/advanced-lipids', methods=['GET', 'POST'])
def advanced_lipids(assessment_id):
    """Advanced lipids - ApoB and Lp(a)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        
        if request.method == 'POST':
            apob = request.form.get('apob')
            lp_a = request.form.get('lp_a')
            
            if apob:
                pillar5.apob = Decimal(apob)
                apob_pts, apob_cat = score_apob(float(apob))
                pillar5.apob_points = apob_pts
            
            if lp_a:
                pillar5.lp_a = Decimal(lp_a)
                lp_a_pts, lp_a_cat = score_lp_a(float(lp_a))
                pillar5.lp_a_points = lp_a_pts
            
            # Total advanced lipids
            pillar5.advanced_lipids_points = (pillar5.apob_points or Decimal('0')) + (pillar5.lp_a_points or Decimal('0'))
            
            session.commit()
            flash('Advanced lipids saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/advanced_lipids.html',
                             assessment=assessment,
                             patient=assessment.patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/cardiac-imaging', methods=['GET', 'POST'])
def cardiac_imaging(assessment_id):
    """Cardiac imaging - CAC, TMT, Echo/CT."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        patient = assessment.patient
        
        if request.method == 'POST':
            # CAC Score
            cac_input = request.form.get('cac_score_input')
            if cac_input == 'notPerformed':
                pillar5.cac_score = None
                pillar5.cac_category = 'Not Performed'
                pillar5.cac_points = Decimal('0.6')  # Neutral
            else:
                cac = request.form.get('cac_score')
                if cac:
                    pillar5.cac_score = Decimal(cac)
                    cac_pts, cac_cat = score_cac(float(cac))
                    pillar5.cac_points = cac_pts
                    pillar5.cac_category = cac_cat
            
            # TMT
            tmt_performed = request.form.get('tmt_performed') == 'on'
            pillar5.tmt_performed = tmt_performed
            
            if tmt_performed:
                tmt_result = request.form.get('tmt_result')
                pillar5.tmt_result = tmt_result
                tmt_pts, tmt_cat = score_tmt(tmt_result)
                pillar5.tmt_points = tmt_pts
            else:
                pillar5.tmt_result = 'notPerformed'
                pillar5.tmt_points = Decimal('0.6')  # Neutral
            
            # Echo/CT
            echo_performed = request.form.get('echo_ct_performed') == 'on'
            pillar5.echo_ct_performed = echo_performed
            
            if echo_performed:
                echo_result = request.form.get('echo_ct_result')
                pillar5.echo_ct_result = echo_result
                echo_pts, echo_cat = score_echo_ct(echo_result)
                pillar5.echo_ct_points = echo_pts
            else:
                pillar5.echo_ct_result = 'notPerformed'
                pillar5.echo_ct_points = Decimal('0.6')  # Neutral
            
            # Total cardiac imaging
            pillar5.cardiac_imaging_points = (pillar5.cac_points or Decimal('0')) + \
                                            (pillar5.tmt_points or Decimal('0')) + \
                                            (pillar5.echo_ct_points or Decimal('0'))
            
            session.commit()
            flash('Cardiac imaging results saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/cardiac_imaging.html',
                             assessment=assessment,
                             patient=patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/kidney', methods=['GET', 'POST'])
def kidney(assessment_id):
    """Kidney function - dual input mode with eGFR calculation."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        patient = assessment.patient
        
        if request.method == 'POST':
            input_mode = request.form.get('input_mode', 'exact')
            pillar5.kidney_input_mode = input_mode
            
            if input_mode == 'exact':
                creatinine = request.form.get('creatinine')
                if creatinine:
                    pillar5.creatinine = Decimal(creatinine)
                    
                    # Calculate eGFR
                    pillar5.calculate_egfr(patient.current_age, patient.sex)
                    
                    # Score from eGFR
                    kidney_pts, kidney_cat = score_kidney_exact(float(pillar5.egfr))
                    pillar5.kidney_points = kidney_pts
                    pillar5.kidney_category = kidney_cat
            
            else:  # category
                category = request.form.get('kidney_category')
                pillar5.kidney_category_input = category
                kidney_pts, kidney_cat = score_kidney_category(category)
                pillar5.kidney_points = kidney_pts
                pillar5.kidney_category = kidney_cat
            
            session.commit()
            flash('Kidney function saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/kidney.html',
                             assessment=assessment,
                             patient=patient,
                             patient_age=patient.current_age,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/cancer-screening', methods=['GET', 'POST'])
def cancer_screening(assessment_id):
    """Cancer screening - dynamic checklist."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        patient = assessment.patient
        
        if request.method == 'POST':
            # Get checkboxes
            pillar5.screening_colonoscopy = request.form.get('colonoscopy') == 'on'
            pillar5.screening_mammogram = request.form.get('mammogram') == 'on'
            pillar5.screening_pap_hpv = request.form.get('pap_hpv') == 'on'
            pillar5.screening_ldct = request.form.get('ldct') == 'on'
            pillar5.screening_psa = request.form.get('psa') == 'on'
            pillar5.screening_skin = request.form.get('skin') == 'on'
            
            # Get recommended count and completed count from form
            pillar5.screening_recommended_count = int(request.form.get('recommended_count') or 0)
            pillar5.screening_completed_count = int(request.form.get('completed_count') or 0)
            
            # Calculate compliance
            pillar5.calculate_screening_compliance()
            
            # Score based on compliance
            if pillar5.screening_compliance_pct:
                screening_pts, screening_cat = score_cancer_screening(float(pillar5.screening_compliance_pct))
                pillar5.screening_points = screening_pts
            
            session.commit()
            flash('Cancer screening results saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/cancer_screening.html',
                             assessment=assessment,
                             patient=patient,
                             patient_age=patient.current_age,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/organ-imaging', methods=['GET', 'POST'])
def organ_imaging(assessment_id):
    """Organ imaging - abdomen and chest."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        
        if request.method == 'POST':
            # Abdomen
            abdomen = request.form.get('abdomen_imaging')
            pillar5.abdomen_imaging = abdomen
            abdomen_pts, abdomen_cat = score_organ_imaging(abdomen)
            pillar5.abdomen_points = abdomen_pts
            
            # Chest
            chest = request.form.get('chest_imaging')
            pillar5.chest_imaging = chest
            chest_pts, chest_cat = score_organ_imaging(chest)
            pillar5.chest_points = chest_pts
            
            # Total organ imaging
            pillar5.organ_imaging_points = abdomen_pts + chest_pts
            
            session.commit()
            flash('Organ imaging results saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/organ_imaging.html',
                             assessment=assessment,
                             patient=assessment.patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/bone', methods=['GET', 'POST'])
def bone(assessment_id):
    """Bone health - DEXA scan."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        patient = assessment.patient
        
        if request.method == 'POST':
            dexa_performed = request.form.get('dexa_performed') == 'on'
            pillar5.dexa_performed = dexa_performed
            
            if dexa_performed:
                t_score = request.form.get('dexa_t_score')
                if t_score:
                    pillar5.dexa_t_score = Decimal(t_score)
                    bone_pts, bone_cat = score_bone(float(t_score))
                    pillar5.bone_points = bone_pts
                    pillar5.bone_category = bone_cat
            else:
                # Not performed - neutral score if not indicated
                if patient.current_age < 50:
                    pillar5.bone_points = Decimal('0.7')  # Neutral
                    pillar5.bone_category = 'Not Indicated'
                else:
                    pillar5.bone_points = Decimal('0.3')  # Slightly penalize
                    pillar5.bone_category = 'Not Performed'
            
            session.commit()
            flash('Bone health results saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/bone.html',
                             assessment=assessment,
                             patient=patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/sensory', methods=['GET', 'POST'])
def sensory(assessment_id):
    """Sensory health - vision and hearing."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        
        if request.method == 'POST':
            # Vision
            vision = request.form.get('vision_status')
            pillar5.vision_status = vision
            vision_pts, vision_cat = score_vision(vision)
            pillar5.vision_points = vision_pts
            
            # Hearing
            hearing = request.form.get('hearing_status')
            pillar5.hearing_status = hearing
            hearing_pts, hearing_cat = score_hearing(hearing)
            pillar5.hearing_points = hearing_pts
            
            # Total sensory
            pillar5.sensory_points = vision_pts + hearing_pts
            
            session.commit()
            flash('Sensory health results saved!', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/sensory.html',
                             assessment=assessment,
                             patient=assessment.patient,
                             pillar5=pillar5)
    finally:
        session.close()


@bp.route('/<int:assessment_id>/pillar5/chronic', methods=['GET', 'POST'])
def chronic(assessment_id):
    """Chronic disease management."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessments.list_assessments'))
        
        pillar5 = assessment.pillar5_results
        
        if request.method == 'POST':
            has_disease = request.form.get('has_chronic_disease') == 'on'
            pillar5.has_chronic_disease = has_disease
            
            if has_disease:
                disease_list = request.form.get('chronic_disease_list', '')
                pillar5.chronic_disease_list = disease_list
                
                management = request.form.get('disease_management')
                pillar5.disease_management = management
                
                chronic_pts, chronic_cat = score_chronic_disease(has_disease, management)
                pillar5.chronic_disease_points = chronic_pts
            else:
                pillar5.disease_management = 'none'
                pillar5.chronic_disease_points = Decimal('1.0')  # Full points
            
            # Calculate total and functional age modifier
            pillar5.calculate_pillar5_total()
            pillar5.calculate_functional_age_modifier()
            pillar5.detect_clinical_alerts()
            
            session.commit()
            flash('Pillar 5 complete! All tests saved.', 'success')
            return redirect(url_for('pillar5.overview', assessment_id=assessment_id))
        
        return render_template('pillar5/chronic.html',
                             assessment=assessment,
                             patient=assessment.patient,
                             pillar5=pillar5)
    finally:
        session.close()
