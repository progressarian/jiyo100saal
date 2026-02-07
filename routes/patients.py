"""
Patient Routes
==============

Basic patient CRUD for testing Section 0 form.
"""

from datetime import date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.base import db
from models.patient import Patient
from models.assessment import Assessment

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')


@patients_bp.route('/')
def list_patients():
    """List all patients."""
    session = db.session()
    try:
        patients = session.query(Patient).order_by(Patient.created_at.desc()).all()
        return render_template('patients/list.html', patients=patients)
    finally:
        session.close()


@patients_bp.route('/new', methods=['GET', 'POST'])
def new_patient():
    """Create new patient."""
    if request.method == 'POST':
        session = db.session()
        try:
            # Parse form data
            dob_str = request.form.get('date_of_birth')
            dob = date.fromisoformat(dob_str) if dob_str else None
            
            patient = Patient(
                first_name=request.form.get('first_name', '').strip(),
                last_name=request.form.get('last_name', '').strip(),
                date_of_birth=dob,
                sex=request.form.get('sex'),
                phone=request.form.get('phone', '').strip() or None,
                email=request.form.get('email', '').strip() or None,
                external_id=request.form.get('external_id', '').strip() or None,
            )
            
            session.add(patient)
            session.commit()
            
            flash(f'Patient {patient.full_name} created successfully!', 'success')
            return redirect(url_for('patients.view_patient', patient_id=patient.id))
            
        except ValueError as e:
            session.rollback()
            flash(f'Validation error: {str(e)}', 'error')
            return render_template('patients/new.html')
        finally:
            session.close()
    
    return render_template('patients/new.html')


@patients_bp.route('/<int:patient_id>')
def view_patient(patient_id: int):
    """View patient details and assessments."""
    session = db.session()
    try:
        patient = session.get(Patient, patient_id)
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        return render_template('patients/view.html', patient=patient)
    finally:
        session.close()


@patients_bp.route('/<int:patient_id>/new-assessment', methods=['POST'])
def create_assessment(patient_id: int):
    """Create new assessment for patient."""
    session = db.session()
    try:
        patient = session.get(Patient, patient_id)
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        assessment = Assessment(
            patient_id=patient_id,
            assessment_date=date.today(),
            assessment_type=request.form.get('assessment_type', 'comprehensive'),
            status='draft',
            clinician_name=request.form.get('clinician_name', '').strip() or None,
        )
        
        session.add(assessment)
        session.commit()
        
        flash('Assessment created! Start with Section 0.', 'success')
        return redirect(url_for('section0.section0_form', assessment_id=assessment.id))
        
    finally:
        session.close()
