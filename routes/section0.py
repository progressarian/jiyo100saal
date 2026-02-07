"""
Section 0 Routes - Baseline Health & Context
============================================

Form handling for Section 0 of the FAS assessment.
Includes demographics, vitals, medications, family history, and risk factors.
"""

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from models.base import db
from models.assessment import Assessment
from models.section0 import Section0Results, FamilyHistory

section0_bp = Blueprint('section0', __name__, url_prefix='/assessment')


# =============================================================================
# VALIDATION HELPERS
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


def parse_bool(value: str) -> Optional[bool]:
    """Parse boolean from form input."""
    if value is None:
        return None
    if value in ('true', 'yes', '1', 'on'):
        return True
    if value in ('false', 'no', '0', 'off'):
        return False
    return None


def parse_date(value: str) -> Optional[date]:
    """Safely parse date from form input."""
    if not value or value.strip() == '':
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def validate_section0_data(data: dict, sex: str) -> list[str]:
    """
    Validate Section 0 form data server-side.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # Required fields
    if not data.get('height_cm'):
        errors.append('Height is required')
    elif not (120 <= float(data['height_cm']) <= 220):
        errors.append('Height must be between 120-220 cm')
    
    if not data.get('weight_kg'):
        errors.append('Weight is required')
    elif not (30 <= float(data['weight_kg']) <= 250):
        errors.append('Weight must be between 30-250 kg')
    
    # Blood pressure validation
    if data.get('bp_systolic_1'):
        if not (60 <= int(data['bp_systolic_1']) <= 250):
            errors.append('Systolic BP must be between 60-250 mmHg')
    
    if data.get('bp_diastolic_1'):
        if not (40 <= int(data['bp_diastolic_1']) <= 150):
            errors.append('Diastolic BP must be between 40-150 mmHg')
    
    # Waist circumference
    if data.get('waist_circumference_cm'):
        waist = float(data['waist_circumference_cm'])
        if not (40 <= waist <= 200):
            errors.append('Waist circumference must be between 40-200 cm')
    
    # Heart rate
    if data.get('resting_heart_rate'):
        hr = int(data['resting_heart_rate'])
        if not (30 <= hr <= 200):
            errors.append('Resting heart rate must be between 30-200 bpm')
    
    return errors


# =============================================================================
# ROUTES
# =============================================================================

@section0_bp.route('/<int:assessment_id>/section0', methods=['GET'])
def section0_form(assessment_id: int):
    """Display Section 0 form (new or edit existing)."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        # Check if Section 0 already exists
        existing = assessment.section0_results
        
        return render_template(
            'section0/form.html',
            assessment=assessment,
            patient=assessment.patient,
            section0=existing,
            family_history=existing.family_history if existing else None,
        )
    finally:
        session.close()


@section0_bp.route('/<int:assessment_id>/section0', methods=['POST'])
def save_section0(assessment_id: int):
    """Save Section 0 form data."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        patient = assessment.patient
        
        # Collect form data
        form_data = {
            'height_cm': parse_decimal(request.form.get('height_cm')),
            'weight_kg': parse_decimal(request.form.get('weight_kg')),
            'waist_circumference_cm': parse_decimal(request.form.get('waist_circumference_cm')),
            'hip_circumference_cm': parse_decimal(request.form.get('hip_circumference_cm')),
            'bp_systolic_1': parse_int(request.form.get('bp_systolic_1')),
            'bp_diastolic_1': parse_int(request.form.get('bp_diastolic_1')),
            'bp_systolic_2': parse_int(request.form.get('bp_systolic_2')),
            'bp_diastolic_2': parse_int(request.form.get('bp_diastolic_2')),
            'bp_arm_used': request.form.get('bp_arm_used') or None,
            'bp_cuff_size': request.form.get('bp_cuff_size') or None,
            'resting_heart_rate': parse_int(request.form.get('resting_heart_rate')),
            'hr_method': request.form.get('hr_method') or None,
            'hr_rhythm': request.form.get('hr_rhythm') or None,
        }
        
        # Validate
        errors = validate_section0_data(form_data, patient.sex)
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('section0.section0_form', assessment_id=assessment_id))
        
        # Get or create Section 0 results
        section0 = assessment.section0_results
        if not section0:
            section0 = Section0Results(assessment_id=assessment_id)
            session.add(section0)
        
        # =================================================================
        # ANTHROPOMETRICS
        # =================================================================
        section0.height_cm = form_data['height_cm']
        section0.weight_kg = form_data['weight_kg']
        section0.waist_circumference_cm = form_data['waist_circumference_cm']
        section0.hip_circumference_cm = form_data['hip_circumference_cm']
        
        # Auto-calculate BMI
        section0.calculate_bmi_and_store()
        
        # =================================================================
        # VITAL SIGNS
        # =================================================================
        section0.bp_systolic_1 = form_data['bp_systolic_1']
        section0.bp_diastolic_1 = form_data['bp_diastolic_1']
        section0.bp_systolic_2 = form_data['bp_systolic_2']
        section0.bp_diastolic_2 = form_data['bp_diastolic_2']
        section0.bp_arm_used = form_data['bp_arm_used']
        section0.bp_cuff_size = form_data['bp_cuff_size']
        
        # Auto-calculate BP average and classification
        section0.calculate_bp_average()
        
        section0.resting_heart_rate = form_data['resting_heart_rate']
        section0.hr_method = form_data['hr_method']
        section0.hr_rhythm = form_data['hr_rhythm']
        
        # =================================================================
        # MEDICATIONS
        # =================================================================
        section0.medication_count = parse_int(request.form.get('medication_count'))
        
        # Medication categories (checkboxes)
        med_categories = request.form.getlist('medication_categories')
        section0.medication_categories = med_categories if med_categories else None
        
        # =================================================================
        # SMOKING
        # =================================================================
        section0.smoking_status = request.form.get('smoking_status') or None
        section0.pack_years = parse_decimal(request.form.get('pack_years'))
        section0.quit_date = parse_date(request.form.get('quit_date'))
        
        # =================================================================
        # ALCOHOL
        # =================================================================
        section0.alcohol_drinks_per_week = parse_int(request.form.get('alcohol_drinks_per_week'))
        section0.alcohol_pattern = request.form.get('alcohol_pattern') or None
        
        # =================================================================
        # FAMILY & SOCIAL
        # =================================================================
        section0.relationship_status = request.form.get('relationship_status') or None
        section0.has_children = parse_bool(request.form.get('has_children'))
        section0.children_details = request.form.get('children_details', '').strip() or None
        section0.living_situation = request.form.get('living_situation') or None
        section0.caregiving_role = request.form.get('caregiving_role') or None
        
        # =================================================================
        # PREGNANCY HISTORY (females only)
        # =================================================================
        if patient.sex == 'female':
            section0.pregnancy_count = parse_int(request.form.get('pregnancy_count'))
            section0.live_births = parse_int(request.form.get('live_births'))
            section0.age_first_pregnancy = parse_int(request.form.get('age_first_pregnancy'))
            section0.gestational_diabetes = parse_bool(request.form.get('gestational_diabetes'))
            section0.preeclampsia = parse_bool(request.form.get('preeclampsia'))
            section0.pcos = parse_bool(request.form.get('pcos'))
        
        # =================================================================
        # INJURIES
        # =================================================================
        section0.tbi_history = request.form.get('tbi_history') or None
        section0.fragility_fracture = parse_bool(request.form.get('fragility_fracture'))
        section0.fracture_location = request.form.get('fracture_location', '').strip() or None
        
        # =================================================================
        # MOTIVATIONS (optional)
        # =================================================================
        motivations = request.form.getlist('motivations')
        section0.motivations = motivations if motivations else None
        section0.personal_goal = request.form.get('personal_goal', '').strip() or None
        
        # =================================================================
        # FAMILY HISTORY
        # =================================================================
        family_history = section0.family_history
        if not family_history:
            family_history = FamilyHistory(section_0_id=section0.id)
            session.add(family_history)
            section0.family_history = family_history
        
        # Father
        family_history.father_status = request.form.get('father_status') or None
        family_history.father_current_age = parse_int(request.form.get('father_current_age'))
        family_history.father_age_at_death = parse_int(request.form.get('father_age_at_death'))
        family_history.father_cause_of_death = request.form.get('father_cause_of_death', '').strip() or None
        
        # Father conditions (JSON)
        father_conditions = {}
        if request.form.get('father_heart_disease'):
            father_conditions['heart_disease'] = True
            father_conditions['heart_disease_age'] = parse_int(request.form.get('father_heart_disease_age'))
        if request.form.get('father_stroke'):
            father_conditions['stroke'] = True
        if request.form.get('father_diabetes'):
            father_conditions['diabetes'] = True
        if request.form.get('father_cancer'):
            father_conditions['cancer'] = True
            father_conditions['cancer_type'] = request.form.get('father_cancer_type', '').strip()
        if request.form.get('father_dementia'):
            father_conditions['dementia'] = True
        family_history.father_conditions = father_conditions if father_conditions else None
        
        # Mother
        family_history.mother_status = request.form.get('mother_status') or None
        family_history.mother_current_age = parse_int(request.form.get('mother_current_age'))
        family_history.mother_age_at_death = parse_int(request.form.get('mother_age_at_death'))
        family_history.mother_cause_of_death = request.form.get('mother_cause_of_death', '').strip() or None
        
        # Mother conditions (JSON)
        mother_conditions = {}
        if request.form.get('mother_heart_disease'):
            mother_conditions['heart_disease'] = True
            mother_conditions['heart_disease_age'] = parse_int(request.form.get('mother_heart_disease_age'))
        if request.form.get('mother_stroke'):
            mother_conditions['stroke'] = True
        if request.form.get('mother_diabetes'):
            mother_conditions['diabetes'] = True
        if request.form.get('mother_breast_cancer'):
            mother_conditions['breast_cancer'] = True
            mother_conditions['breast_cancer_age'] = parse_int(request.form.get('mother_breast_cancer_age'))
        if request.form.get('mother_dementia'):
            mother_conditions['dementia'] = True
        family_history.mother_conditions = mother_conditions if mother_conditions else None
        
        # Grandparents longevity (optional)
        family_history.grandfather_paternal_age = parse_int(request.form.get('grandfather_paternal_age'))
        family_history.grandmother_paternal_age = parse_int(request.form.get('grandmother_paternal_age'))
        family_history.grandfather_maternal_age = parse_int(request.form.get('grandfather_maternal_age'))
        family_history.grandmother_maternal_age = parse_int(request.form.get('grandmother_maternal_age'))
        family_history.exceptional_longevity = request.form.get('exceptional_longevity') or None
        
        # Calculate family history modifiers
        family_history.calculate_parents_avg_lifespan()
        family_history.calculate_longevity_modifier()
        family_history.assess_cvd_family_risk()
        
        # =================================================================
        # CALCULATE RISK MODIFIERS
        # =================================================================
        section0.calculate_functional_age_modifier()
        
        # =================================================================
        # UPDATE ASSESSMENT STATUS
        # =================================================================
        if assessment.status == 'draft':
            assessment.status = 'in_progress'
        
        # Commit all changes
        session.commit()
        
        # Determine next action
        save_action = request.form.get('save_action', 'save')
        
        if save_action == 'save_continue':
            flash('Section 0 saved! Continue to Section 1 (Body Composition).', 'success')
            # TODO: redirect to section1 when built
            return redirect(url_for('assessments.view_assessment', assessment_id=assessment_id))
        else:
            flash('Section 0 saved successfully!', 'success')
            return redirect(url_for('section0.section0_form', assessment_id=assessment_id))
        
    except Exception as e:
        session.rollback()
        flash(f'Error saving data: {str(e)}', 'error')
        return redirect(url_for('section0.section0_form', assessment_id=assessment_id))
    finally:
        session.close()


@section0_bp.route('/<int:assessment_id>/section0/api', methods=['GET'])
def get_section0_data(assessment_id: int):
    """API endpoint to get Section 0 data as JSON."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            return jsonify({'error': 'Assessment not found'}), 404
        
        section0 = assessment.section0_results
        if not section0:
            return jsonify({'error': 'Section 0 not found'}), 404
        
        data = section0.to_dict()
        if section0.family_history:
            data['family_history'] = section0.family_history.to_dict()
        
        return jsonify(data)
    finally:
        session.close()


# =============================================================================
# PACK-YEARS CALCULATOR (AJAX endpoint)
# =============================================================================

@section0_bp.route('/calculate-pack-years', methods=['POST'])
def calculate_pack_years():
    """Calculate pack-years from cigarettes per day and years smoked."""
    data = request.get_json()
    
    cigarettes_per_day = data.get('cigarettes_per_day', 0)
    years_smoked = data.get('years_smoked', 0)
    
    try:
        cigs = float(cigarettes_per_day) if cigarettes_per_day else 0
        years = float(years_smoked) if years_smoked else 0
        
        # Pack-years = (cigarettes per day / 20) × years
        pack_years = (cigs / 20) * years
        
        return jsonify({
            'pack_years': round(pack_years, 1),
            'cigarettes_per_day': cigs,
            'years_smoked': years,
        })
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid input'}), 400
