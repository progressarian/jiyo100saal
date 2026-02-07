"""
Assessment Routes
=================

Assessment overview and navigation.
"""

from flask import Blueprint, render_template, redirect, url_for, flash

from models.base import db
from models.assessment import Assessment

assessments_bp = Blueprint('assessments', __name__, url_prefix='/assessments')


def generate_top_recommendations(assessment):
    """Generate top 3 personalized recommendations based on pillar scores."""
    recs = []
    
    # Check each pillar's percentage score and add recommendations for weak areas
    if assessment.pillar1_results and assessment.pillar1_results.pillar1_pct:
        if float(assessment.pillar1_results.pillar1_pct) < 70:
            recs.append(("Movement & Strength", 
                        float(assessment.pillar1_results.pillar1_pct),
                        "Increase physical activity and strength training"))
    
    if assessment.pillar2_results and assessment.pillar2_results.pillar2_pct:
        if float(assessment.pillar2_results.pillar2_pct) < 70:
            recs.append(("Cognitive Function",
                        float(assessment.pillar2_results.pillar2_pct),
                        "Engage in brain training and mental exercises"))
    
    if assessment.pillar3_results and assessment.pillar3_results.pillar3_pct:
        if float(assessment.pillar3_results.pillar3_pct) < 70:
            recs.append(("Metabolic Health",
                        float(assessment.pillar3_results.pillar3_pct),
                        "Improve diet and metabolic markers"))
    
    if assessment.pillar4_results and assessment.pillar4_results.pillar4_pct:
        if float(assessment.pillar4_results.pillar4_pct) < 70:
            recs.append(("Vitality & Hormones",
                        float(assessment.pillar4_results.pillar4_pct),
                        "Optimize sleep, exercise, and hormone health"))
    
    if assessment.pillar5_results and assessment.pillar5_results.pillar5_pct:
        if float(assessment.pillar5_results.pillar5_pct) < 70:
            recs.append(("Disease Prevention",
                        float(assessment.pillar5_results.pillar5_pct),
                        "Complete overdue health screenings"))
    
    # Sort by score (lowest first)
    recs.sort(key=lambda x: x[1])
    
    # Extract just the recommendation text
    recommendations = [rec[2] for rec in recs]
    
    # If less than 3 issues, add general wellness tips
    if len(recommendations) < 3:
        if len(recommendations) == 0:
            recommendations.append("Maintain current healthy habits and consistency")
        recommendations.append("Schedule annual comprehensive physical exam")
        recommendations.append("Stay engaged with preventive health screenings")
    
    return recommendations[:3]


@assessments_bp.route('/<int:assessment_id>')
def view_assessment(assessment_id: int):
    """View assessment overview with links to all sections."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        # Calculate functional age only if at least one pillar is complete
        chronological_age = None
        functional_age = None
        age_difference = None
        top_recommendations = []
        
        if assessment.patient and (assessment.pillar1_results or assessment.pillar2_results or 
                                   assessment.pillar3_results or assessment.pillar4_results or 
                                   assessment.pillar5_results):
            chronological_age = assessment.patient.current_age
            total_modifier = 0.0
            pillars_completed = False
            
            # Sum up all pillar functional age modifiers
            if assessment.pillar1_results and assessment.pillar1_results.functional_age_impact is not None:
                total_modifier += float(assessment.pillar1_results.functional_age_impact)
                pillars_completed = True
            
            if assessment.pillar2_results and assessment.pillar2_results.functional_age_modifier is not None:
                total_modifier += float(assessment.pillar2_results.functional_age_modifier)
                pillars_completed = True
            
            if assessment.pillar3_results and assessment.pillar3_results.functional_age_modifier is not None:
                total_modifier += float(assessment.pillar3_results.functional_age_modifier)
                pillars_completed = True
            
            if assessment.pillar4_results and assessment.pillar4_results.functional_age_modifier is not None:
                total_modifier += float(assessment.pillar4_results.functional_age_modifier)
                pillars_completed = True
            
            if assessment.pillar5_results and assessment.pillar5_results.functional_age_modifier is not None:
                total_modifier += float(assessment.pillar5_results.functional_age_modifier)
                pillars_completed = True
            
            # Only set values if at least one pillar has been completed
            if pillars_completed:
                functional_age = round(chronological_age + total_modifier, 1)
                age_difference = round(total_modifier, 1)
                # Generate recommendations
                top_recommendations = generate_top_recommendations(assessment)
        
        return render_template('assessments/view.html',
                             assessment=assessment,
                             chronological_age=chronological_age,
                             functional_age=functional_age,
                             age_difference=age_difference,
                             top_recommendations=top_recommendations)
    finally:
        session.close()


@assessments_bp.route('/<int:assessment_id>/complete', methods=['POST'])
def complete_assessment(assessment_id: int):
    """Mark assessment as complete."""
    session = db.session()
    try:
        assessment = session.get(Assessment, assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('patients.list_patients'))
        
        assessment.status = 'completed'
        assessment.calculate_functional_age()
        session.commit()
        
        flash('Assessment completed!', 'success')
        return redirect(url_for('assessments.view_assessment', assessment_id=assessment_id))
    finally:
        session.close()
