"""
Report Generation Routes
========================

Routes for generating PDF assessment reports.
"""

from flask import Blueprint, send_file, flash, redirect, url_for
from models import db
from models.assessment import Assessment
from reports.pdf_generator import generate_assessment_report

bp = Blueprint('reports', __name__, url_prefix='/assessment')


@bp.route('/<int:assessment_id>/report')
def generate_report(assessment_id: int):
    """Generate and download PDF assessment report."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        # Generate PDF
        pdf_buffer = generate_assessment_report(assessment)
        
        # Create filename
        patient_name = assessment.patient.full_name.replace(' ', '_')
        date_str = assessment.assessment_date.strftime('%Y%m%d')
        filename = f"Jiyo100Saal_Report_{patient_name}_{date_str}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('assessments.view_assessment', assessment_id=assessment_id))
    finally:
        session.close()
