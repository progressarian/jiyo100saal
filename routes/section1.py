"""
Section 1 Routes - Body Composition
===================================

Form handling for Section 1 of the FAS assessment.
Supports DEXA, BIA, and Manual (skinfolds/circumferences) input methods.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from models.base import db
from models.assessment import Assessment
from models.section1 import Section1Results
from calculators.body_composition import (
    calculate_lmi,
    calculate_whr,
    calculate_body_density_jackson_pollock,
    calculate_body_fat_siri,
    calculate_body_fat_navy,
    calculate_skinfold_sum,
    calculate_lean_mass_from_fat,
)
from scoring.section1 import (
    score_body_fat_pct,
    score_lmi,
    score_visceral_fat,
    score_fat_distribution_ag_ratio,
    score_fat_distribution_whr,
    assess_sarcopenia_risk,
    get_bone_density_category,
)

section1_bp = Blueprint('section1', __name__, url_prefix='/assessment')


# =============================================================================
# HELPERS
# =============================================================================

def parse_decimal(value: str, default: Optional[Decimal] = None) -> Optional[Decimal]:
    """Safely parse decimal from form input."""
    if not value or value.strip() == '':
        return default
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return default


def parse_int(value: str, default: Optional[int] = None) -> Optional[int]:
    """Safely parse integer from form input."""
    if not value or value.strip() == '':
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def validate_section1_data(data: dict, input_method: str) -> list[str]:
    """Validate Section 1 form data server-side."""
    errors = []
    
    if not input_method:
        errors.append('Please select an input method (DEXA, BIA, or Manual)')
        return errors
    
    # Body fat validation
    body_fat = data.get('body_fat_pct')
    if body_fat is not None:
        bf = float(body_fat)
        if not (5 <= bf <= 60):
            errors.append('Body fat % must be between 5-60%')
    
    # Lean mass validation
    lean_mass = data.get('lean_mass_kg')
    if lean_mass is not None:
        lm = float(lean_mass)
        if not (20 <= lm <= 100):
            errors.append('Lean mass must be between 20-100 kg')
    
    # Visceral fat validation
    vfa = data.get('visceral_fat_area')
    if vfa is not None:
        v = int(vfa)
        if not (0 <= v <= 500):
            errors.append('Visceral fat area must be between 0-500 cm²')
    
    # Skinfold validation
    if input_method == 'manual':
        for site in ['chest', 'abdomen', 'thigh', 'triceps', 'subscapular', 'suprailiac', 'midaxillary']:
            val = data.get(f'skinfold_{site}_mm')
            if val is not None:
                sf = float(val)
                if not (1 <= sf <= 50):
                    errors.append(f'{site.capitalize()} skinfold must be between 1-50 mm')
    
    # Neck circumference validation
    neck = data.get('neck_circumference_cm')
    if neck is not None:
        n = float(neck)
        if not (25 <= n <= 60):
            errors.append('Neck circumference must be between 25-60 cm')
    
    return errors


# =============================================================================
# ROUTES
# =============================================================================

@section1_bp.route('/<int:assessment_id>/section1', methods=['GET'])
def section1_form(assessment_id: int):
    """Display Section 1 form."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        # Check if Section 0 is complete (required before Section 1)
        if not assessment.section0_results:
            flash('Please complete Section 0 first', 'warning')
            return redirect(url_for('section0.section0_form', assessment_id=assessment_id))
        
        section0 = assessment.section0_results
        existing = assessment.section1_results
        
        return render_template(
            'section1/form.html',
            assessment=assessment,
            patient=assessment.patient,
            section0=section0,
            section1=existing,
        )
    finally:
        session.close()


@section1_bp.route('/<int:assessment_id>/section1', methods=['POST'])
def save_section1(assessment_id: int):
    """Save Section 1 form data."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        if not assessment.section0_results:
            flash('Section 0 must be completed first', 'error')
            return redirect(url_for('section0.section0_form', assessment_id=assessment_id))
        
        section0 = assessment.section0_results
        patient = assessment.patient
        age = assessment.age_at_assessment
        sex = patient.sex
        height_cm = float(section0.height_cm)
        weight_kg = float(section0.weight_kg)
        waist_cm = float(section0.waist_circumference_cm) if section0.waist_circumference_cm else None
        hip_cm = float(section0.hip_circumference_cm) if section0.hip_circumference_cm else None
        
        # Get input method
        input_method = request.form.get('input_method')
        
        # Collect form data based on input method
        form_data = {}
        
        if input_method == 'dexa':
            form_data = {
                'body_fat_pct': parse_decimal(request.form.get('dexa_body_fat_pct')),
                'fat_mass_kg': parse_decimal(request.form.get('dexa_fat_mass_kg')),
                'lean_mass_kg': parse_decimal(request.form.get('dexa_lean_mass_kg')),
                'asmi': parse_decimal(request.form.get('dexa_asmi')),
                'visceral_fat_area': parse_int(request.form.get('dexa_visceral_fat_area')),
                'ag_ratio': parse_decimal(request.form.get('dexa_android_gynoid_ratio')),
                'lumbar_tscore': parse_decimal(request.form.get('dexa_lumbar_tscore')),
                'hip_tscore': parse_decimal(request.form.get('dexa_hip_tscore')),
            }
        elif input_method == 'bia':
            form_data = {
                'body_fat_pct': parse_decimal(request.form.get('bia_body_fat_pct')),
                'lean_mass_kg': parse_decimal(request.form.get('bia_lean_mass_kg')),
                'water_pct': parse_decimal(request.form.get('bia_water_pct')),
                'visceral_fat_level': parse_int(request.form.get('bia_visceral_fat_level')),
            }
        elif input_method == 'manual':
            manual_type = request.form.get('manual_type', 'skinfolds')
            form_data = {
                'manual_type': manual_type,
                'neck_circumference_cm': parse_decimal(request.form.get('neck_circumference_cm')),
            }
            
            if manual_type == 'skinfolds':
                form_data.update({
                    'skinfold_chest_mm': parse_decimal(request.form.get('skinfold_chest_mm')),
                    'skinfold_abdomen_mm': parse_decimal(request.form.get('skinfold_abdomen_mm')),
                    'skinfold_thigh_mm': parse_decimal(request.form.get('skinfold_thigh_mm')),
                    'skinfold_triceps_mm': parse_decimal(request.form.get('skinfold_triceps_mm')),
                    'skinfold_subscapular_mm': parse_decimal(request.form.get('skinfold_subscapular_mm')),
                    'skinfold_suprailiac_mm': parse_decimal(request.form.get('skinfold_suprailiac_mm')),
                    'skinfold_midaxillary_mm': parse_decimal(request.form.get('skinfold_midaxillary_mm')),
                })
        
        # Validate
        errors = validate_section1_data(form_data, input_method)
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('section1.section1_form', assessment_id=assessment_id))
        
        # Get or create Section 1 results
        section1 = assessment.section1_results
        if not section1:
            section1 = Section1Results(assessment_id=assessment_id)
            session.add(section1)
        
        section1.input_method = input_method
        
        # =================================================================
        # PROCESS DEXA DATA
        # =================================================================
        if input_method == 'dexa':
            section1.dexa_body_fat_pct = form_data.get('body_fat_pct')
            section1.dexa_total_fat_mass_kg = form_data.get('fat_mass_kg')
            section1.dexa_lean_mass_kg = form_data.get('lean_mass_kg')
            section1.dexa_asmi = form_data.get('asmi')
            section1.dexa_visceral_fat_area = form_data.get('visceral_fat_area')
            section1.dexa_android_gynoid_ratio = form_data.get('ag_ratio')
            section1.dexa_lumbar_tscore = form_data.get('lumbar_tscore')
            section1.dexa_hip_tscore = form_data.get('hip_tscore')
            
            # Set final body fat from DEXA
            section1.body_fat_pct = section1.dexa_body_fat_pct
            
            # Calculate LMI if lean mass provided
            if section1.dexa_lean_mass_kg:
                lmi = calculate_lmi(float(section1.dexa_lean_mass_kg), height_cm)
                section1.lean_mass_index = Decimal(str(lmi))
        
        # =================================================================
        # PROCESS BIA DATA
        # =================================================================
        elif input_method == 'bia':
            section1.bia_body_fat_pct = form_data.get('body_fat_pct')
            section1.bia_lean_mass_kg = form_data.get('lean_mass_kg')
            section1.bia_water_pct = form_data.get('water_pct')
            section1.bia_visceral_fat_level = form_data.get('visceral_fat_level')
            
            # Set final body fat from BIA
            section1.body_fat_pct = section1.bia_body_fat_pct
            
            # Calculate LMI if lean mass provided
            if section1.bia_lean_mass_kg:
                lmi = calculate_lmi(float(section1.bia_lean_mass_kg), height_cm)
                section1.lean_mass_index = Decimal(str(lmi))
        
        # =================================================================
        # PROCESS MANUAL DATA
        # =================================================================
        elif input_method == 'manual':
            manual_type = form_data.get('manual_type')
            neck_cm = float(form_data['neck_circumference_cm']) if form_data.get('neck_circumference_cm') else None
            section1.neck_circumference_cm = form_data.get('neck_circumference_cm')
            
            if manual_type == 'skinfolds':
                # Store skinfold measurements
                section1.skinfold_chest_mm = form_data.get('skinfold_chest_mm')
                section1.skinfold_abdomen_mm = form_data.get('skinfold_abdomen_mm')
                section1.skinfold_thigh_mm = form_data.get('skinfold_thigh_mm')
                section1.skinfold_triceps_mm = form_data.get('skinfold_triceps_mm')
                section1.skinfold_subscapular_mm = form_data.get('skinfold_subscapular_mm')
                section1.skinfold_suprailiac_mm = form_data.get('skinfold_suprailiac_mm')
                section1.skinfold_midaxillary_mm = form_data.get('skinfold_midaxillary_mm')
                
                # Calculate body fat from skinfolds
                sum_sf = calculate_skinfold_sum(
                    float(section1.skinfold_chest_mm) if section1.skinfold_chest_mm else None,
                    float(section1.skinfold_abdomen_mm) if section1.skinfold_abdomen_mm else None,
                    float(section1.skinfold_thigh_mm) if section1.skinfold_thigh_mm else None,
                    float(section1.skinfold_triceps_mm) if section1.skinfold_triceps_mm else None,
                    float(section1.skinfold_subscapular_mm) if section1.skinfold_subscapular_mm else None,
                    float(section1.skinfold_suprailiac_mm) if section1.skinfold_suprailiac_mm else None,
                    float(section1.skinfold_midaxillary_mm) if section1.skinfold_midaxillary_mm else None,
                )
                
                if sum_sf is not None:
                    body_density = calculate_body_density_jackson_pollock(sum_sf, age, sex)
                    section1.body_density = Decimal(str(body_density))
                    body_fat_pct = calculate_body_fat_siri(body_density)
                    section1.body_fat_pct = Decimal(str(body_fat_pct))
                    
                    # Calculate lean mass from body fat
                    lean_mass = calculate_lean_mass_from_fat(weight_kg, body_fat_pct)
                    lmi = calculate_lmi(lean_mass, height_cm)
                    section1.lean_mass_index = Decimal(str(lmi))
            
            elif manual_type == 'circumferences' and neck_cm and waist_cm:
                # Calculate body fat using Navy method
                try:
                    body_fat_pct = calculate_body_fat_navy(
                        height_cm, waist_cm, neck_cm, sex, hip_cm
                    )
                    section1.body_fat_pct = Decimal(str(body_fat_pct))
                    
                    # Calculate lean mass from body fat
                    lean_mass = calculate_lean_mass_from_fat(weight_kg, body_fat_pct)
                    lmi = calculate_lmi(lean_mass, height_cm)
                    section1.lean_mass_index = Decimal(str(lmi))
                except ValueError as e:
                    flash(f'Navy method calculation error: {str(e)}', 'error')
        
        # =================================================================
        # CALCULATE WHR (if hip available)
        # =================================================================
        if waist_cm and hip_cm:
            whr = calculate_whr(waist_cm, hip_cm)
            section1.waist_hip_ratio = Decimal(str(whr))
        
        # =================================================================
        # CALCULATE SCORES
        # =================================================================
        
        # Body fat score
        if section1.body_fat_pct:
            bf_score, bf_category = score_body_fat_pct(float(section1.body_fat_pct), age, sex)
            section1.body_fat_score = Decimal(str(bf_score))
            section1.body_fat_category = bf_category
        
        # LMI score
        if section1.lean_mass_index:
            lmi_score, lmi_category = score_lmi(float(section1.lean_mass_index), sex)
            section1.lmi_score = Decimal(str(lmi_score))
            section1.lmi_category = lmi_category
        
        # Visceral fat score
        vfa = section1.dexa_visceral_fat_area
        bia_vf = section1.bia_visceral_fat_level
        if vfa or bia_vf:
            vf_score, _ = score_visceral_fat(vfa, bia_vf)
            section1.visceral_fat_score = Decimal(str(vf_score))
        
        # Fat distribution score
        if section1.dexa_android_gynoid_ratio:
            fd_score, _ = score_fat_distribution_ag_ratio(
                float(section1.dexa_android_gynoid_ratio), sex
            )
            section1.fat_distribution_score = Decimal(str(fd_score))
        elif section1.waist_hip_ratio:
            fd_score, _ = score_fat_distribution_whr(
                float(section1.waist_hip_ratio), sex
            )
            section1.fat_distribution_score = Decimal(str(fd_score))
        
        # =================================================================
        # ASSESS SARCOPENIA RISK
        # =================================================================
        asmi = float(section1.dexa_asmi) if section1.dexa_asmi else None
        lmi = float(section1.lean_mass_index) if section1.lean_mass_index else None
        
        is_at_risk, _ = assess_sarcopenia_risk(sex, lmi=lmi, asmi=asmi)
        section1.sarcopenia_risk = is_at_risk
        
        # =================================================================
        # METABOLIC SYNDROME CRITERIA (just waist for now)
        # =================================================================
        criteria_met = 0
        if waist_cm:
            if sex == 'male' and waist_cm >= 90:
                criteria_met += 1
            elif sex == 'female' and waist_cm >= 80:
                criteria_met += 1
        section1.metabolic_syndrome_criteria_met = criteria_met
        
        # Commit all changes
        session.commit()
        
        # Determine next action
        save_action = request.form.get('save_action', 'save')
        
        if save_action == 'save_continue':
            flash('Section 1 saved! Continue to Pillar 1 (Movement & Strength).', 'success')
            return redirect(url_for('pillar1.overview', assessment_id=assessment_id))
        else:
            flash('Section 1 saved successfully!', 'success')
            return redirect(url_for('section1.section1_form', assessment_id=assessment_id))
        
    except Exception as e:
        session.rollback()
        flash(f'Error saving data: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('section1.section1_form', assessment_id=assessment_id))
    finally:
        session.close()


@section1_bp.route('/<int:assessment_id>/section1/api', methods=['GET'])
def get_section1_data(assessment_id: int):
    """API endpoint to get Section 1 data as JSON."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        section1 = assessment.section1_results
        if not section1:
            return jsonify({'error': 'Section 1 not found'}), 404
        
        return jsonify(section1.to_dict())
    finally:
        session.close()


# =============================================================================
# CALCULATION API ENDPOINTS (for AJAX)
# =============================================================================

@section1_bp.route('/calculate-body-fat-skinfolds', methods=['POST'])
def calculate_body_fat_skinfolds_api():
    """Calculate body fat from skinfolds (AJAX)."""
    data = request.get_json()
    
    try:
        chest = float(data.get('chest', 0))
        abdomen = float(data.get('abdomen', 0))
        thigh = float(data.get('thigh', 0))
        triceps = float(data.get('triceps', 0))
        subscapular = float(data.get('subscapular', 0))
        suprailiac = float(data.get('suprailiac', 0))
        midaxillary = float(data.get('midaxillary', 0))
        age = int(data.get('age', 30))
        sex = data.get('sex', 'male')
        weight_kg = float(data.get('weight_kg', 70))
        height_cm = float(data.get('height_cm', 170))
        
        sum_sf = chest + abdomen + thigh + triceps + subscapular + suprailiac + midaxillary
        
        if sum_sf <= 0:
            return jsonify({'error': 'Please enter all skinfold measurements'}), 400
        
        body_density = calculate_body_density_jackson_pollock(sum_sf, age, sex)
        body_fat_pct = calculate_body_fat_siri(body_density)
        lean_mass = calculate_lean_mass_from_fat(weight_kg, body_fat_pct)
        lmi = calculate_lmi(lean_mass, height_cm)
        
        bf_score, bf_category = score_body_fat_pct(body_fat_pct, age, sex)
        lmi_score, lmi_category = score_lmi(lmi, sex)
        is_sarcopenia, _ = assess_sarcopenia_risk(sex, lmi=lmi)
        
        return jsonify({
            'sum_skinfolds': round(sum_sf, 1),
            'body_density': body_density,
            'body_fat_pct': body_fat_pct,
            'lean_mass_kg': lean_mass,
            'lmi': lmi,
            'bf_score': bf_score,
            'bf_category': bf_category,
            'lmi_score': lmi_score,
            'lmi_category': lmi_category,
            'sarcopenia_risk': is_sarcopenia,
        })
    except (ValueError, TypeError, ZeroDivisionError) as e:
        return jsonify({'error': str(e)}), 400


@section1_bp.route('/calculate-body-fat-navy', methods=['POST'])
def calculate_body_fat_navy_api():
    """Calculate body fat from Navy method (AJAX)."""
    data = request.get_json()
    
    try:
        height_cm = float(data.get('height_cm', 170))
        waist_cm = float(data.get('waist_cm', 90))
        neck_cm = float(data.get('neck_cm', 38))
        hip_cm = float(data.get('hip_cm')) if data.get('hip_cm') else None
        sex = data.get('sex', 'male')
        age = int(data.get('age', 30))
        weight_kg = float(data.get('weight_kg', 70))
        
        body_fat_pct = calculate_body_fat_navy(height_cm, waist_cm, neck_cm, sex, hip_cm)
        lean_mass = calculate_lean_mass_from_fat(weight_kg, body_fat_pct)
        lmi = calculate_lmi(lean_mass, height_cm)
        
        bf_score, bf_category = score_body_fat_pct(body_fat_pct, age, sex)
        lmi_score, lmi_category = score_lmi(lmi, sex)
        is_sarcopenia, _ = assess_sarcopenia_risk(sex, lmi=lmi)
        
        return jsonify({
            'body_fat_pct': body_fat_pct,
            'lean_mass_kg': lean_mass,
            'lmi': lmi,
            'bf_score': bf_score,
            'bf_category': bf_category,
            'lmi_score': lmi_score,
            'lmi_category': lmi_category,
            'sarcopenia_risk': is_sarcopenia,
        })
    except (ValueError, TypeError, ZeroDivisionError) as e:
        return jsonify({'error': str(e)}), 400


@section1_bp.route('/calculate-lmi', methods=['POST'])
def calculate_lmi_api():
    """Calculate LMI from lean mass (AJAX)."""
    data = request.get_json()
    
    try:
        lean_mass_kg = float(data.get('lean_mass_kg', 0))
        height_cm = float(data.get('height_cm', 170))
        sex = data.get('sex', 'male')
        
        if lean_mass_kg <= 0:
            return jsonify({'error': 'Lean mass must be positive'}), 400
        
        lmi = calculate_lmi(lean_mass_kg, height_cm)
        lmi_score, lmi_category = score_lmi(lmi, sex)
        is_sarcopenia, reason = assess_sarcopenia_risk(sex, lmi=lmi)
        
        return jsonify({
            'lmi': lmi,
            'lmi_score': lmi_score,
            'lmi_category': lmi_category,
            'sarcopenia_risk': is_sarcopenia,
            'sarcopenia_reason': reason,
        })
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400
