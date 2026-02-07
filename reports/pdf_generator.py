"""
PDF Report Generator
====================

Generates professional PDF assessment reports using ReportLab.
"""

from io import BytesIO
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart


# Brand colors
BRAND_PRIMARY = colors.HexColor('#667eea')
BRAND_SECONDARY = colors.HexColor('#764ba2')
BRAND_SUCCESS = colors.HexColor('#28a745')
BRAND_WARNING = colors.HexColor('#ffc107')
BRAND_DANGER = colors.HexColor('#dc3545')
BRAND_DARK = colors.HexColor('#343a40')
BRAND_LIGHT = colors.HexColor('#f8f9fa')


def get_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=BRAND_PRIMARY,
        spaceAfter=30,
        alignment=TA_CENTER,
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=BRAND_PRIMARY,
        spaceBefore=20,
        spaceAfter=10,
    ))
    
    # Subsection heading
    styles.add(ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=BRAND_DARK,
        spaceBefore=15,
        spaceAfter=8,
    ))
    
    # Custom body text
    styles.add(ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=BRAND_DARK,
        spaceAfter=6,
        leading=14,
    ))
    
    # Alert text
    styles.add(ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=BRAND_DANGER,
        spaceAfter=6,
        leading=14,
        fontName='Helvetica-Bold',
    ))
    
    # Success text
    styles.add(ParagraphStyle(
        'SuccessText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=BRAND_SUCCESS,
        spaceAfter=6,
        leading=14,
    ))
    
    # Center aligned
    styles.add(ParagraphStyle(
        'CenterText',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    
    # Large number display
    styles.add(ParagraphStyle(
        'LargeNumber',
        parent=styles['Normal'],
        fontSize=36,
        textColor=BRAND_PRIMARY,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    ))
    
    return styles


def safe_get(obj, attr, default='—'):
    """Safely get an attribute from an object."""
    if obj is None:
        return default
    val = getattr(obj, attr, None)
    if val is None:
        return default
    if isinstance(val, Decimal):
        return str(float(val))
    return str(val)


def safe_float(obj, attr, default=0):
    """Safely get a float value from an object."""
    if obj is None:
        return default
    val = getattr(obj, attr, None)
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def calculate_whr_risk(waist, hip, sex):
    """Calculate WHR risk category."""
    if waist is None or hip is None or hip == 0:
        return '—'
    try:
        whr = float(waist) / float(hip)
        if sex == 'male':
            if whr < 0.90:
                return 'Low Risk'
            elif whr < 1.0:
                return 'Moderate Risk'
            else:
                return 'High Risk'
        else:  # female
            if whr < 0.80:
                return 'Low Risk'
            elif whr < 0.85:
                return 'Moderate Risk'
            else:
                return 'High Risk'
    except:
        return '—'


def get_bmi_category(bmi):
    """Get BMI category from value."""
    if bmi is None:
        return '—'
    try:
        bmi_val = float(bmi)
        if bmi_val < 18.5:
            return 'Underweight'
        elif bmi_val < 25:
            return 'Normal'
        elif bmi_val < 30:
            return 'Overweight'
        else:
            return 'Obese'
    except:
        return '—'


# Pillar 2 color
BRAND_PILLAR2 = colors.HexColor('#7c3aed')

# Pillar 3 color
BRAND_PILLAR3 = colors.HexColor('#3498db')

# Pillar 4 color (purple-blue)
BRAND_PILLAR4 = colors.HexColor('#8e44ad')


def create_pillar1_chart(pillar1) -> Drawing:
    """Create a bar chart showing Pillar 1 test scores."""
    d = Drawing(400, 200)
    
    # Data
    tests = [
        ('Chair', safe_float(pillar1, 'chair_stand_score'), 3.0),
        ('Grip', safe_float(pillar1, 'grip_score'), 3.0),
        ('Gait', safe_float(pillar1, 'gait_score'), 2.0),
        ('Balance', safe_float(pillar1, 'balance_total_score'), 3.0),
        ('TUG', safe_float(pillar1, 'tug_score'), 2.0),
        ('VO2', safe_float(pillar1, 'vo2_score'), 4.0),
        ('Flex', safe_float(pillar1, 'flexibility_score'), 2.0),
        ('6MWT', safe_float(pillar1, 'walk_6min_score'), 3.0),
    ]
    
    # Normalize to percentage
    data = [[t[1] / t[2] * 100 if t[2] > 0 else 0 for t in tests]]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300
    bc.data = data
    bc.categoryAxis.categoryNames = [t[0] for t in tests]
    bc.categoryAxis.labels.angle = 45
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.labels.dy = -5
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 25
    bc.bars[0].fillColor = BRAND_PRIMARY
    
    d.add(bc)
    return d


def create_pillar2_chart(pillar2) -> Drawing:
    """Create a bar chart showing Pillar 2 test scores."""
    d = Drawing(400, 200)
    
    # Data - grouped by domain
    tests = [
        ('Memory\nImm', safe_float(pillar2, 'memory_immediate_points'), 2.0),
        ('Memory\nDel', safe_float(pillar2, 'memory_delayed_points'), 2.0),
        ('Digit\nSpan', safe_float(pillar2, 'digit_span_forward_points') + safe_float(pillar2, 'digit_span_backward_points'), 2.0),
        ('Trails', safe_float(pillar2, 'trails_a_points') + safe_float(pillar2, 'trails_b_points'), 6.0),
        ('DSST', safe_float(pillar2, 'dsst_points'), 3.0),
        ('Clock', safe_float(pillar2, 'clock_points'), 2.0),
        ('Verbal', safe_float(pillar2, 'verbal_fluency_points'), 2.0),
        ('Mental\nHealth', safe_float(pillar2, 'phq2_points') + safe_float(pillar2, 'gad2_points'), 2.0),
    ]
    
    # Normalize to percentage
    data = [[t[1] / t[2] * 100 if t[2] > 0 else 0 for t in tests]]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300
    bc.data = data
    bc.categoryAxis.categoryNames = [t[0] for t in tests]
    bc.categoryAxis.labels.angle = 45
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.labels.dy = -5
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 25
    bc.bars[0].fillColor = BRAND_PILLAR2
    
    d.add(bc)
    return d


def create_pillar3_chart(pillar3) -> Drawing:
    """Create a bar chart showing Pillar 3 test scores (5 main categories)."""
    d = Drawing(400, 200)
    
    # Data - 5 main test categories using correct field names
    tests = [
        ('Glucose', safe_float(pillar3, 'glucose_blood_points') + safe_float(pillar3, 'glucose_functional_points'), 5.0),
        ('Digestive', safe_float(pillar3, 'bowel_points') + safe_float(pillar3, 'stool_points') + 
                     safe_float(pillar3, 'reflux_points') + safe_float(pillar3, 'meal_comfort_points'), 6.0),
        ('Gut\nSymptoms', safe_float(pillar3, 'bloating_points') + safe_float(pillar3, 'pain_points') + 
                         safe_float(pillar3, 'intolerance_points'), 4.0),
        ('Liver', safe_float(pillar3, 'liver_points'), 3.0),
        ('Inflammation', safe_float(pillar3, 'crp_points'), 2.0),
    ]
    
    # Normalize to percentage
    data = [[t[1] / t[2] * 100 if t[2] > 0 else 0 for t in tests]]
    
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 120
    bc.width = 300
    bc.data = data
    bc.categoryAxis.categoryNames = [t[0] for t in tests]
    bc.categoryAxis.labels.angle = 45
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.labels.dy = -5
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 25
    bc.bars[0].fillColor = BRAND_PILLAR3
    
    d.add(bc)
    return d


def create_pillar4_chart(pillar4) -> Drawing:
    """Create a bar chart showing Pillar 4 test scores (9 tests)."""
    d = Drawing(400, 200)
    
    # Data - 9 test components
    tests = [
        ('Thyroid', safe_float(pillar4, 'thyroid_points'), 4.0),
        ('Hormones', safe_float(pillar4, 'hormone_points'), 4.0),
        ('Sexual', safe_float(pillar4, 'sexual_health_points'), 1.0),
        ('Vit D', safe_float(pillar4, 'vitd_points'), 2.0),
        ('Iron', safe_float(pillar4, 'iron_points'), 2.0),
        ('Exercise', safe_float(pillar4, 'exercise_points'), 2.0),
        ('Sleep', safe_float(pillar4, 'sleep_points'), 3.0),
        ('Appearance', safe_float(pillar4, 'appearance_points'), 1.0),
        ('Stress', safe_float(pillar4, 'stress_points'), 1.0),
    ]
    
    # Normalize to percentage
    data = [[t[1] / t[2] * 100 if t[2] > 0 else 0 for t in tests]]
    
    bc = VerticalBarChart()
    bc.x = 30
    bc.y = 50
    bc.height = 120
    bc.width = 340
    bc.data = data
    bc.categoryAxis.categoryNames = [t[0] for t in tests]
    bc.categoryAxis.labels.angle = 45
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.labels.dy = -5
    bc.categoryAxis.labels.fontSize = 8
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 100
    bc.valueAxis.valueStep = 25
    bc.bars[0].fillColor = BRAND_PILLAR4
    
    d.add(bc)
    return d


def generate_cover_page(story: List, styles: Dict, assessment, patient) -> None:
    """Generate the cover page."""
    story.append(Spacer(1, 2 * inch))
    
    # Title
    story.append(Paragraph("JIYO100SAAL", styles['CustomTitle']))
    story.append(Paragraph("Functional Aging Assessment", styles['CenterText']))
    story.append(Spacer(1, 0.5 * inch))
    
    # Decorative line
    story.append(HRFlowable(width="60%", thickness=3, color=BRAND_PRIMARY, 
                            spaceBefore=20, spaceAfter=20, hAlign='CENTER'))
    
    story.append(Spacer(1, 0.5 * inch))
    
    # Patient info table
    patient_data = [
        ['Patient Name:', patient.full_name if patient else '—'],
        ['Age at Assessment:', f"{assessment.age_at_assessment} years" if assessment else '—'],
        ['Sex:', patient.sex.capitalize() if patient and patient.sex else '—'],
        ['Assessment Date:', assessment.assessment_date.strftime('%B %d, %Y') if assessment and assessment.assessment_date else '—'],
        ['Assessment Type:', assessment.assessment_type.replace('_', ' ').title() if assessment and assessment.assessment_type else 'Comprehensive'],
    ]
    
    t = Table(patient_data, colWidths=[2.5 * inch, 3 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), BRAND_DARK),
        ('TEXTCOLOR', (1, 0), (1, -1), BRAND_PRIMARY),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    
    story.append(Spacer(1, 1 * inch))
    
    # Footer
    story.append(Paragraph("Confidential Medical Report", styles['CenterText']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['CenterText']))
    
    story.append(PageBreak())


def add_functional_age_box(story: List, assessment, patient, pillar1, pillar2, pillar3, pillar4, pillar5) -> None:
    """Add eye-catching functional age display to first page."""
    # Calculate functional age
    chronological_age = patient.current_age if patient else 0
    total_modifier = 0.0
    
    if pillar1 and getattr(pillar1, 'functional_age_impact', None):
        total_modifier += float(pillar1.functional_age_impact)
    if pillar2 and getattr(pillar2, 'functional_age_modifier', None):
        total_modifier += float(pillar2.functional_age_modifier)
    if pillar3 and getattr(pillar3, 'functional_age_modifier', None):
        total_modifier += float(pillar3.functional_age_modifier)
    if pillar4 and getattr(pillar4, 'functional_age_modifier', None):
        total_modifier += float(pillar4.functional_age_modifier)
    if pillar5 and getattr(pillar5, 'functional_age_modifier', None):
        total_modifier += float(pillar5.functional_age_modifier)
    
    functional_age = round(chronological_age + total_modifier, 1)
    age_difference = round(total_modifier, 1)
    
    # Determine status and color
    if age_difference <= -2:
        status = "EXCELLENT - Significantly Younger!"
        bg_color = colors.HexColor('#10b981')
    elif age_difference < 0:
        status = "GOOD - Younger Than Chronological"
        bg_color = colors.HexColor('#3b82f6')
    elif age_difference == 0:
        status = "AVERAGE - Right on Track"
        bg_color = colors.HexColor('#6b7280')
    elif age_difference <= 2:
        status = "NEEDS IMPROVEMENT"
        bg_color = colors.HexColor('#f59e0b')
    else:
        status = "URGENT - Requires Attention"
        bg_color = colors.HexColor('#ef4444')
    
    # Create table
    data = [
        ['YOUR FUNCTIONAL AGE ASSESSMENT'],
        [f'Chronological Age: {chronological_age} years'],
        [f'Functional Age: {functional_age} years'],
        [f'Difference: {abs(age_difference)} years {"YOUNGER ✓" if age_difference < 0 else "OLDER"}'],
        [f'Status: {status}'],
    ]
    
    table = Table(data, colWidths=[6.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), bg_color),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 18),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (0, -1), 14),
        ('FONTNAME', (0, 1), (0, 3), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.grey),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f9fafb')),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))


def add_pillar_impact_table(story: List, assessment, pillar1, pillar2, pillar3, pillar4, pillar5) -> None:
    """Show impact of each pillar on functional age."""
    data = [['PILLAR', 'SCORE', 'IMPACT', 'STATUS']]
    
    if pillar1 and getattr(pillar1, 'pillar1_total', None):
        impact = float(getattr(pillar1, 'functional_age_impact', 0))
        status = "✓" if impact <= 0 else "⚠"
        data.append(['Movement & Strength', 
                    f'{pillar1.pillar1_total}/20',
                    f'{impact:+.1f} years', 
                    status])
    
    if pillar2 and getattr(pillar2, 'pillar2_total', None):
        impact = float(getattr(pillar2, 'functional_age_modifier', 0))
        status = "✓" if impact <= 0 else "⚠"
        data.append(['Cognitive Function',
                    f'{pillar2.pillar2_total}/18',
                    f'{impact:+.1f} years',
                    status])
    
    if pillar3 and getattr(pillar3, 'pillar3_total', None):
        impact = float(getattr(pillar3, 'functional_age_modifier', 0))
        status = "✓" if impact <= 0 else "⚠"
        data.append(['Metabolic Health',
                    f'{pillar3.pillar3_total}/20',
                    f'{impact:+.1f} years',
                    status])
    
    if pillar4 and getattr(pillar4, 'pillar4_total', None):
        impact = float(getattr(pillar4, 'functional_age_modifier', 0))
        status = "✓" if impact <= 0 else "⚠"
        data.append(['Vitality & Hormones',
                    f'{pillar4.pillar4_total}/20',
                    f'{impact:+.1f} years',
                    status])
    
    if pillar5 and getattr(pillar5, 'pillar5_total', None):
        impact = float(getattr(pillar5, 'functional_age_modifier', 0))
        status = "✓" if impact <= 0 else "⚠"
        data.append(['Disease Prevention',
                    f'{pillar5.pillar5_total}/20',
                    f'{impact:+.1f} years',
                    status])
    
    table = Table(data, colWidths=[2.5 * inch, 1.2 * inch, 1.3 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))


def add_health_motivation_section(story: List, styles: Dict, assessment, section0) -> None:
    """Add patient's health goals and motivations to report."""
    if not section0:
        return
    
    # Get motivations from section0
    motivations = []
    if getattr(section0, 'motivation_children', None):
        motivations.append("Be there for children/grandchildren")
    if getattr(section0, 'motivation_independence', None):
        motivations.append("Maintain independence")
    if getattr(section0, 'motivation_travel', None):
        motivations.append("Active retirement/travel")
    if getattr(section0, 'motivation_avoid_parents', None):
        motivations.append("Avoid parents' health problems")
    if getattr(section0, 'motivation_performance', None):
        motivations.append("Athletic/fitness performance")
    if getattr(section0, 'motivation_cognitive', None):
        motivations.append("Cognitive sharpness")
    
    personal_goal = getattr(section0, 'personal_goal', None)
    
    if motivations or personal_goal:
        story.append(Spacer(1, 0.2 * inch))
        
        # Title
        story.append(Paragraph("YOUR HEALTH GOALS & MOTIVATION", styles['SubHeading']))
        
        # Motivations
        if motivations:
            for motivation in motivations:
                story.append(Paragraph(f"✓ {motivation}", styles['ReportBody']))
        
        # Personal goal
        if personal_goal:
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(f'<i>Personal Goal: "{personal_goal}"</i>', styles['ReportBody']))
        
        story.append(Spacer(1, 0.2 * inch))


def add_quick_summary_section(story: List, styles: Dict, assessment, pillar1, pillar2, pillar3, pillar4, pillar5) -> None:
    """Add intelligent health snapshot with personalized 3-month plan."""
    strengths = []
    three_month_focus = []
    tests_needed = []
    
    # Get patient for age/sex checks
    patient = assessment.patient if assessment else None
    
    # Analyze each pillar with specific 3-month actions
    if pillar1 and getattr(pillar1, 'pillar1_pct', None):
        pct = float(pillar1.pillar1_pct)
        if pct >= 80:
            strengths.append("💪 Excellent physical fitness")
        elif pct < 60:
            three_month_focus.append("💪 Start daily 30-min walks + 2x/week strength training")
    
    if pillar2 and getattr(pillar2, 'pillar2_pct', None):
        pct = float(pillar2.pillar2_pct)
        if pct >= 80:
            strengths.append("🧠 Sharp cognitive function")
        elif pct < 60:
            three_month_focus.append("🧠 Daily brain exercises + neurologist consultation")
    
    if pillar3 and getattr(pillar3, 'pillar3_pct', None):
        pct = float(pillar3.pillar3_pct)
        if pct >= 80:
            strengths.append("🔬 Optimal metabolic health")
        elif pct < 60:
            three_month_focus.append("🔬 Improve diet, retest glucose & lipids in 3 months")
    
    if pillar4 and getattr(pillar4, 'pillar4_pct', None):
        pct = float(pillar4.pillar4_pct)
        if pct >= 80:
            strengths.append("💜 Excellent vitality")
        elif pct < 60:
            three_month_focus.append("💜 Optimize sleep (7-8hrs), check vitamin D & thyroid")
    
    if pillar5 and getattr(pillar5, 'pillar5_pct', None):
        pct = float(pillar5.pillar5_pct)
        
        if pct >= 80:
            strengths.append("🏥 Excellent preventive care")
        elif pct < 60:
            # Identify specific tests needed
            if patient:
                if getattr(pillar5, 'screening_colonoscopy', None) == False and patient.current_age >= 45:
                    tests_needed.append("Colonoscopy (age 45+)")
                if getattr(pillar5, 'screening_psa', None) == False and patient.sex == 'male' and patient.current_age >= 40:
                    tests_needed.append("PSA test (prostate)")
                if getattr(pillar5, 'screening_mammogram', None) == False and patient.sex == 'female' and patient.current_age >= 40:
                    tests_needed.append("Mammogram")
                if getattr(pillar5, 'screening_pap_hpv', None) == False and patient.sex == 'female':
                    tests_needed.append("Pap smear")
            
            if tests_needed:
                three_month_focus.append(f"🏥 Schedule {len(tests_needed)} overdue screenings")
    
    # If no clear weaknesses, add maintenance focus
    if len(three_month_focus) == 0:
        three_month_focus.append("Maintain current healthy habits")
        three_month_focus.append("Continue regular exercise & preventive care")
    
    # Calculate improvement potential
    total_modifier = 0.0
    if pillar1 and getattr(pillar1, 'functional_age_impact', None) is not None:
        total_modifier += float(pillar1.functional_age_impact)
    if pillar2 and getattr(pillar2, 'functional_age_modifier', None) is not None:
        total_modifier += float(pillar2.functional_age_modifier)
    if pillar3 and getattr(pillar3, 'functional_age_modifier', None) is not None:
        total_modifier += float(pillar3.functional_age_modifier)
    if pillar4 and getattr(pillar4, 'functional_age_modifier', None) is not None:
        total_modifier += float(pillar4.functional_age_modifier)
    if pillar5 and getattr(pillar5, 'functional_age_modifier', None) is not None:
        total_modifier += float(pillar5.functional_age_modifier)
    
    # Estimate improvement potential
    if total_modifier > 2:
        improvement_potential = "Reduce functional age by 2-3 years in 3-6 months"
    elif total_modifier > 0:
        improvement_potential = "Reduce functional age by 1-2 years in 3-6 months"
    else:
        improvement_potential = "Maintain optimal functional age"
    
    # Only show if we have something to display
    if not strengths and not three_month_focus:
        return
    
    # Add section title
    story.append(Paragraph("YOUR HEALTH SNAPSHOT & 3-MONTH ACTION PLAN", styles['SubHeading']))
    
    # Create comprehensive summary table
    data = [['✓ YOUR STRENGTHS', '🎯 FOCUS AREAS FOR NEXT 3 MONTHS']]
    
    # Add strengths vs focus areas
    max_rows = max(len(strengths), len(three_month_focus))
    for i in range(max_rows):
        strength = strengths[i] if i < len(strengths) else ''
        focus = three_month_focus[i] if i < len(three_month_focus) else ''
        data.append([strength, focus])
    
    table = Table(data, colWidths=[2.5 * inch, 4 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#10b981')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('LEADING', (0, 1), (-1, -1), 14),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.15 * inch))
    
    # Add tests needed section if any
    if tests_needed:
        story.append(Paragraph(
            f"🔴 <b>URGENT SCREENINGS NEEDED:</b> {', '.join(tests_needed)}",
            styles['AlertText']
        ))
        story.append(Spacer(1, 0.1 * inch))
    
    # Add improvement potential
    story.append(Paragraph(
        f"🎯 <b>POTENTIAL:</b> {improvement_potential} with focused action!",
        styles['SuccessText']
    ))
    story.append(Spacer(1, 0.2 * inch))


def generate_executive_summary(story: List, styles: Dict, assessment, patient, section0, section1, pillar1, pillar2, pillar3, pillar4=None, pillar5=None) -> None:
    """Generate the executive summary page."""
    story.append(Paragraph("Executive Summary", styles['SectionHeading']))
    
    # Add health motivation (if available)
    add_health_motivation_section(story, styles, assessment, section0)
    
    # Add functional age box and pillar impact table
    add_functional_age_box(story, assessment, patient, pillar1, pillar2, pillar3, pillar4, pillar5)
    add_pillar_impact_table(story, assessment, pillar1, pillar2, pillar3, pillar4, pillar5)
    
    # Add quick strengths vs needs work summary
    add_quick_summary_section(story, styles, assessment, pillar1, pillar2, pillar3, pillar4, pillar5)
    
    # Calculate functional age
    chronological_age = assessment.age_at_assessment if assessment else 0
    section0_modifier = safe_float(section0, 'functional_age_modifier')
    pillar1_modifier = safe_float(pillar1, 'functional_age_impact')
    pillar2_modifier = safe_float(pillar2, 'functional_age_modifier')
    pillar3_modifier = safe_float(pillar3, 'functional_age_modifier')
    pillar4_modifier = safe_float(pillar4, 'functional_age_modifier') if pillar4 else 0
    pillar5_modifier = safe_float(pillar5, 'functional_age_modifier') if pillar5 else 0
    functional_age = chronological_age + section0_modifier + pillar1_modifier + pillar2_modifier + pillar3_modifier + pillar4_modifier + pillar5_modifier
    
    # Functional Age Display
    story.append(Paragraph("Functional Age Assessment", styles['SubHeading']))
    
    age_data = [
        ['Chronological Age:', f"{chronological_age} years"],
        ['Section 0 Modifier:', f"{'+' if section0_modifier > 0 else ''}{section0_modifier:.1f} years"],
        ['Pillar 1 Impact:', f"{'+' if pillar1_modifier > 0 else ''}{pillar1_modifier:.1f} years"],
        ['Pillar 2 Impact:', f"{'+' if pillar2_modifier > 0 else ''}{pillar2_modifier:.1f} years"],
        ['Pillar 3 Impact:', f"{'+' if pillar3_modifier > 0 else ''}{pillar3_modifier:.1f} years"],
        ['Pillar 4 Impact:', f"{'+' if pillar4_modifier > 0 else ''}{pillar4_modifier:.1f} years"] if pillar4 else ['Pillar 4 Impact:', 'Not assessed'],
        ['Pillar 5 Impact:', f"{'+' if pillar5_modifier > 0 else ''}{pillar5_modifier:.1f} years"] if pillar5 else ['Pillar 5 Impact:', 'Not assessed'],
        ['Estimated Functional Age:', f"{functional_age:.1f} years"],
    ]
    
    t = Table(age_data, colWidths=[2.5 * inch, 2 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, -1), (-1, -1), BRAND_PRIMARY),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e7f1ff')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Overall Assessment
    story.append(Paragraph("Overall Assessment", styles['SubHeading']))
    
    pillar1_total = safe_float(pillar1, 'pillar1_total')
    pillar1_category = safe_get(pillar1, 'pillar1_category', 'Not assessed')
    pillar2_total = safe_float(pillar2, 'pillar2_total')
    pillar2_category = safe_get(pillar2, 'pillar2_category', 'Not assessed')
    pillar3_total = safe_float(pillar3, 'pillar3_total')
    pillar3_category = safe_get(pillar3, 'pillar3_category', 'Not assessed')
    pillar4_total = safe_float(pillar4, 'pillar4_total') if pillar4 else 0
    pillar4_category = safe_get(pillar4, 'pillar4_category', 'Not assessed') if pillar4 else 'Not assessed'
    pillar5_total = safe_float(pillar5, 'pillar5_total') if pillar5 else 0
    pillar5_category = safe_get(pillar5, 'pillar5_category', 'Not assessed') if pillar5 else 'Not assessed'
    
    # Combined assessment based on all pillars
    pillar_count = 0
    total_pct = 0
    
    if pillar1_total > 0:
        total_pct += (pillar1_total / 20)
        pillar_count += 1
    if pillar2_total > 0:
        total_pct += (pillar2_total / 10)  # Pillar 2 is out of 10
        pillar_count += 1
    if pillar3_total > 0:
        total_pct += (pillar3_total / 20)
        pillar_count += 1
    if pillar4 and pillar4_total > 0:
        total_pct += (pillar4_total / 20)
        pillar_count += 1
    if pillar5 and pillar5_total > 0:
        total_pct += (pillar5_total / 20)
        pillar_count += 1
    
    combined_pct = (total_pct / pillar_count * 100) if pillar_count > 0 else 0
    
    if combined_pct >= 80:
        overall = "Excellent functional capacity for age"
    elif combined_pct >= 60:
        overall = "Good functional capacity with minor areas for improvement"
    elif combined_pct >= 40:
        overall = "Fair functional capacity - targeted interventions recommended"
    else:
        overall = "Below expected functional capacity - comprehensive intervention needed"
    
    story.append(Paragraph(f"Pillar 1 (Movement & Strength): <b>{pillar1_total:.1f}/20</b> ({pillar1_category})", styles['ReportBody']))
    story.append(Paragraph(f"Pillar 2 (Cognitive Function): <b>{pillar2_total:.1f}/10</b> ({pillar2_category})", styles['ReportBody']))
    story.append(Paragraph(f"Pillar 3 (Metabolic & Digestive): <b>{pillar3_total:.1f}/20</b> ({pillar3_category})", styles['ReportBody']))
    if pillar4:
        story.append(Paragraph(f"Pillar 4 (Vitality & Hormones): <b>{pillar4_total:.1f}/20</b> ({pillar4_category})", styles['ReportBody']))
    if pillar5:
        story.append(Paragraph(f"Pillar 5 (Disease Prevention): <b>{pillar5_total:.1f}/20</b> ({pillar5_category})", styles['ReportBody']))
    story.append(Paragraph(overall, styles['ReportBody']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Key Findings
    story.append(Paragraph("Key Findings", styles['SubHeading']))
    
    findings = []
    
    # Section 0 findings
    if section0:
        bp_sys = getattr(section0, 'bp_systolic_avg', None)
        bp_dia = getattr(section0, 'bp_diastolic_avg', None)
        bp_class = getattr(section0, 'bp_classification', None)
        if bp_sys and bp_sys >= 140:
            findings.append(f"• <b>Hypertension:</b> BP {bp_sys}/{bp_dia} mmHg ({bp_class or 'Elevated'})")
        
        smoking = getattr(section0, 'smoking_status', None)
        pack_years = getattr(section0, 'pack_years', None)
        if smoking and smoking != 'never':
            pack_str = f" ({pack_years} pack-years)" if pack_years else ""
            findings.append(f"• <b>Smoking History:</b> {smoking.replace('_', ' ').title()}{pack_str}")
    
    # Section 1 findings
    if section1:
        if getattr(section1, 'sarcopenia_risk', None):
            lmi = safe_get(section1, 'lean_mass_index')
            findings.append(f"• <b>Sarcopenia Risk:</b> LMI {lmi} - muscle mass below threshold")
        
        bf_cat = getattr(section1, 'body_fat_category', None)
        bf_pct = safe_get(section1, 'body_fat_pct')
        if bf_cat and 'high' in bf_cat.lower():
            findings.append(f"• <b>Body Fat:</b> {bf_pct}% ({bf_cat})")
    
    # Pillar 1 findings
    if pillar1:
        if getattr(pillar1, 'sarcopenia_flag', None):
            grip = safe_get(pillar1, 'grip_dominant_best')
            findings.append(f"• <b>Low Grip Strength:</b> {grip} kg - sarcopenia indicator")
        
        gait = safe_float(pillar1, 'gait_speed_ms')
        if gait > 0 and gait < 0.8:
            findings.append(f"• <b>Slow Gait:</b> {gait:.2f} m/s - fall risk factor")
        
        vo2 = safe_float(pillar1, 'vo2_max')
        if vo2 > 0 and vo2 < 25:
            findings.append(f"• <b>Low Cardiorespiratory Fitness:</b> VO2 max {vo2:.1f} mL/kg/min")
        
        tug = safe_float(pillar1, 'tug_faster_sec')
        if tug > 14:
            findings.append(f"• <b>Mobility Concern:</b> TUG {tug:.1f} sec")
    
    # Pillar 2 findings
    if pillar2:
        if getattr(pillar2, 'cognitive_concern_flag', None):
            dsst = safe_get(pillar2, 'dsst_score')
            findings.append(f"• <b>Processing Speed Concern:</b> DSST {dsst} - below expected")
        
        if getattr(pillar2, 'executive_dysfunction_flag', None):
            ba_ratio = safe_float(pillar2, 'trails_ba_ratio')
            findings.append(f"• <b>Executive Dysfunction:</b> B/A ratio {ba_ratio:.1f} - elevated")
        
        if getattr(pillar2, 'memory_deficit_flag', None):
            ds_total = safe_float(pillar2, 'digit_span_total')
            findings.append(f"• <b>Working Memory Deficit:</b> Digit span {ds_total:.0f}")
        
        if getattr(pillar2, 'language_concern_flag', None):
            vf = safe_float(pillar2, 'verbal_fluency_animals')
            findings.append(f"• <b>Language/Executive Concern:</b> Verbal fluency {vf:.0f} animals")
    
    if not findings:
        findings.append("• No significant concerns identified")
    
    for finding in findings:
        story.append(Paragraph(finding, styles['ReportBody']))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Critical Alerts
    alerts = []
    if pillar1:
        # Fall risk
        fall_factors = 0
        gait = safe_float(pillar1, 'gait_speed_ms')
        balance = safe_float(pillar1, 'single_leg_better_best')
        tug = safe_float(pillar1, 'tug_faster_sec')
        
        if gait > 0 and gait < 0.8:
            fall_factors += 1
        if balance > 0 and balance < 5:
            fall_factors += 1
        if tug > 20:
            fall_factors += 1
        
        if fall_factors >= 2:
            alerts.append("⚠️ HIGH FALL RISK - Multiple risk factors identified")
        
        if getattr(pillar1, 'low_vo2_flag', None):
            alerts.append("⚠️ SEVERELY IMPAIRED CARDIORESPIRATORY FITNESS - VO2 max < 20 mL/kg/min")
    
    if alerts:
        story.append(Paragraph("Critical Alerts", styles['SubHeading']))
        for alert in alerts:
            story.append(Paragraph(alert, styles['AlertText']))
    
    story.append(PageBreak())


def generate_section0_page(story: List, styles: Dict, section0, assessment, patient) -> None:
    """Generate Section 0: Baseline Health page."""
    story.append(Paragraph("Section 0: Baseline Health & Context", styles['SectionHeading']))
    
    if not section0:
        story.append(Paragraph("Section 0 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Calculate WHR if we have both measurements
    waist = getattr(section0, 'waist_circumference_cm', None)
    hip = getattr(section0, 'hip_circumference_cm', None)
    whr = None
    whr_risk = '—'
    if waist and hip and float(hip) > 0:
        whr = float(waist) / float(hip)
        sex = patient.sex if patient else 'male'
        whr_risk = calculate_whr_risk(waist, hip, sex)
    
    # Get BMI category
    bmi = getattr(section0, 'bmi', None)
    bmi_category = get_bmi_category(bmi)
    
    # Anthropometrics
    story.append(Paragraph("Anthropometric Measurements", styles['SubHeading']))
    
    anthro_data = [
        ['Measurement', 'Value', 'Classification'],
        ['Height', f"{safe_get(section0, 'height_cm')} cm", '—'],
        ['Weight', f"{safe_get(section0, 'weight_kg')} kg", '—'],
        ['BMI', f"{safe_get(section0, 'bmi')} kg/m²", bmi_category],
        ['Waist Circumference', f"{safe_get(section0, 'waist_circumference_cm')} cm", '—'],
        ['Hip Circumference', f"{safe_get(section0, 'hip_circumference_cm')} cm", '—'],
        ['Waist-Hip Ratio', f"{whr:.2f}" if whr else '—', whr_risk],
    ]
    
    t = Table(anthro_data, colWidths=[2.5 * inch, 1.5 * inch, 2 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Vital Signs
    story.append(Paragraph("Vital Signs", styles['SubHeading']))
    
    vitals_data = [
        ['Parameter', 'Value', 'Classification'],
        ['Blood Pressure', f"{safe_get(section0, 'bp_systolic_avg')}/{safe_get(section0, 'bp_diastolic_avg')} mmHg", safe_get(section0, 'bp_classification')],
        ['Heart Rate', f"{safe_get(section0, 'resting_heart_rate')} bpm", safe_get(section0, 'hr_rhythm', 'Regular')],
    ]
    
    t = Table(vitals_data, colWidths=[2.5 * inch, 1.5 * inch, 2 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Lifestyle & History
    story.append(Paragraph("Lifestyle & Medical History", styles['SubHeading']))
    
    # Format alcohol info
    alcohol_drinks = getattr(section0, 'alcohol_drinks_per_week', None)
    alcohol_str = f"{alcohol_drinks} drinks/week" if alcohol_drinks else 'Not reported'
    
    # Format medication info
    med_count = getattr(section0, 'medication_count', None)
    med_str = f"{med_count} medications" if med_count else 'Not reported'
    
    smoking_status = getattr(section0, 'smoking_status', None)
    smoking_str = smoking_status.replace('_', ' ').title() if smoking_status else 'Not reported'
    
    lifestyle_data = [
        ['Factor', 'Status'],
        ['Smoking Status', smoking_str],
        ['Pack-Years', safe_get(section0, 'pack_years')],
        ['Alcohol Use', alcohol_str],
        ['Medications', med_str],
    ]
    
    t = Table(lifestyle_data, colWidths=[2.5 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Functional Age Modifier
    modifier = safe_float(section0, 'functional_age_modifier')
    modifier_text = f"{'+' if modifier > 0 else ''}{modifier:.1f} years"
    
    story.append(Paragraph("Section 0 Functional Age Impact", styles['SubHeading']))
    story.append(Paragraph(f"Based on lifestyle factors and medical history, Section 0 contributes <b>{modifier_text}</b> to functional age.", 
                          styles['ReportBody']))
    
    story.append(PageBreak())


def generate_section1_page(story: List, styles: Dict, section1, patient) -> None:
    """Generate Section 1: Body Composition page."""
    story.append(Paragraph("Section 1: Body Composition Analysis", styles['SectionHeading']))
    
    if not section1:
        story.append(Paragraph("Section 1 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Method used
    method = getattr(section1, 'input_method', None)
    method_str = method.upper() if method else 'Unknown'
    story.append(Paragraph(f"Assessment Method: <b>{method_str}</b>", styles['ReportBody']))
    
    # Add method-specific note
    if method and method.lower() == 'manual':
        story.append(Paragraph(
            "<i>Note: Manual method provides estimates based on anthropometric measurements. "
            "DEXA or BIA recommended for precise body composition analysis.</i>",
            styles['ReportBody']
        ))
    story.append(Spacer(1, 0.2 * inch))
    
    # Body Composition Results
    story.append(Paragraph("Body Composition Results", styles['SubHeading']))
    
    # Get the final calculated values (these should be populated regardless of method)
    body_fat = getattr(section1, 'body_fat_pct', None)
    lmi = getattr(section1, 'lean_mass_index', None)
    bf_score = getattr(section1, 'body_fat_score', None)
    bf_cat = getattr(section1, 'body_fat_category', None)
    lmi_score = getattr(section1, 'lmi_score', None)
    lmi_cat = getattr(section1, 'lmi_category', None)
    
    # Get visceral fat based on method
    if method and method.lower() == 'dexa':
        visceral = getattr(section1, 'dexa_visceral_fat_area', None)
        visceral_str = f"{visceral} cm²" if visceral else '—'
    elif method and method.lower() == 'bia':
        visceral = getattr(section1, 'bia_visceral_fat_level', None)
        visceral_str = f"Level {visceral}" if visceral else '—'
    else:
        visceral_str = 'N/A (Manual method)'
    
    # Get fat distribution
    if method and method.lower() == 'dexa':
        fat_dist = getattr(section1, 'dexa_android_gynoid_ratio', None)
        fat_dist_str = f"{float(fat_dist):.2f}" if fat_dist else '—'
    else:
        fat_dist = getattr(section1, 'waist_hip_ratio', None)
        fat_dist_str = f"{float(fat_dist):.2f} (WHR)" if fat_dist else '—'
    
    # Build table with available data
    comp_data = [['Parameter', 'Value', 'Score', 'Category']]
    
    # Body Fat
    if body_fat is not None:
        comp_data.append([
            'Body Fat %', 
            f"{float(body_fat):.1f}%",
            f"{float(bf_score):.1f}/4" if bf_score else '—',
            bf_cat or '—'
        ])
    else:
        comp_data.append(['Body Fat %', 'Not measured', '—', '—'])
    
    # Lean Mass Index
    if lmi is not None:
        comp_data.append([
            'Lean Mass Index',
            f"{float(lmi):.2f} kg/m²",
            f"{float(lmi_score):.1f}/3" if lmi_score else '—',
            lmi_cat or '—'
        ])
    else:
        comp_data.append(['Lean Mass Index', 'Not measured', '—', '—'])
    
    # Visceral Fat
    vf_score = getattr(section1, 'visceral_fat_score', None)
    comp_data.append([
        'Visceral Fat',
        visceral_str,
        f"{float(vf_score):.1f}/2" if vf_score else '—',
        '—'
    ])
    
    # Fat Distribution
    fd_score = getattr(section1, 'fat_distribution_score', None)
    comp_data.append([
        'Fat Distribution',
        fat_dist_str,
        f"{float(fd_score):.1f}/2" if fd_score else '—',
        '—'
    ])
    
    t = Table(comp_data, colWidths=[2 * inch, 1.5 * inch, 1 * inch, 1.5 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Clinical Significance
    story.append(Paragraph("Clinical Significance", styles['SubHeading']))
    
    interpretations = []
    has_findings = False
    
    # Sarcopenia risk check
    sarcopenia_risk = getattr(section1, 'sarcopenia_risk', None)
    if sarcopenia_risk:
        has_findings = True
        interpretations.append(Paragraph(
            "⚠️ <b>Sarcopenia Risk Identified:</b> Low lean mass index suggests reduced muscle mass. "
            "Recommend strength training program and protein intake optimization.",
            styles['AlertText']
        ))
    elif lmi is not None:
        interpretations.append(Paragraph(
            f"✓ Lean mass index ({float(lmi):.2f} kg/m²) within acceptable range.",
            styles['SuccessText']
        ))
    
    # Body fat assessment
    if bf_cat:
        cat_lower = bf_cat.lower()
        if 'high' in cat_lower or 'obese' in cat_lower or 'above' in cat_lower:
            has_findings = True
            interpretations.append(Paragraph(
                f"⚠️ <b>Elevated Body Fat:</b> {float(body_fat):.1f}% ({bf_cat}). "
                "Consider nutrition counseling and increased physical activity.",
                styles['AlertText']
            ))
        elif body_fat is not None:
            interpretations.append(Paragraph(
                f"✓ Body fat percentage ({float(body_fat):.1f}%) is in the {bf_cat} range.",
                styles['SuccessText']
            ))
    
    # If no data available
    if not interpretations:
        interpretations.append(Paragraph(
            "Limited body composition data available. Consider DEXA or BIA assessment for detailed analysis.",
            styles['ReportBody']
        ))
    
    for interp in interpretations:
        story.append(interp)
    
    story.append(PageBreak())


def generate_pillar1_page(story: List, styles: Dict, pillar1, assessment, patient) -> None:
    """Generate Pillar 1: Movement & Strength page."""
    story.append(Paragraph("Pillar 1: Movement & Strength Assessment", styles['SectionHeading']))
    
    if not pillar1:
        story.append(Paragraph("Pillar 1 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Summary
    total = safe_float(pillar1, 'pillar1_total')
    category = safe_get(pillar1, 'pillar1_category', 'Not calculated')
    
    story.append(Paragraph(f"Total Score: <b>{total:.1f}/20</b> ({category})", styles['ReportBody']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Test Results Table
    story.append(Paragraph("Individual Test Results", styles['SubHeading']))
    
    tests_data = [
        ['Test', 'Result', 'Score', 'Category'],
        ['1. 30-Second Chair Stand', f"{safe_get(pillar1, 'chair_stand_reps')} reps", 
         f"{safe_get(pillar1, 'chair_stand_score')}/3.0", safe_get(pillar1, 'chair_stand_category')],
        ['2. Grip Strength', f"{safe_get(pillar1, 'grip_dominant_best')} kg", 
         f"{safe_get(pillar1, 'grip_score')}/3.0", safe_get(pillar1, 'grip_category')],
        ['3. 4-Meter Gait Speed', f"{safe_get(pillar1, 'gait_speed_ms')} m/s", 
         f"{safe_get(pillar1, 'gait_score')}/2.0", safe_get(pillar1, 'gait_category')],
        ['4. Balance (Single-Leg)', f"{safe_get(pillar1, 'single_leg_better_best')} sec", 
         f"{safe_get(pillar1, 'balance_total_score')}/3.0", safe_get(pillar1, 'balance_category')],
        ['5. Timed Up and Go', f"{safe_get(pillar1, 'tug_faster_sec')} sec", 
         f"{safe_get(pillar1, 'tug_score')}/2.0", safe_get(pillar1, 'tug_category')],
        ['6. VO2 Max', f"{safe_get(pillar1, 'vo2_max')} mL/kg/min", 
         f"{safe_get(pillar1, 'vo2_score')}/4.0", safe_get(pillar1, 'vo2_category')],
        ['7. Sit-and-Reach', f"{safe_get(pillar1, 'flexibility_best_cm')} cm", 
         f"{safe_get(pillar1, 'flexibility_score')}/2.0", safe_get(pillar1, 'flexibility_category')],
        ['8. 6-Minute Walk', f"{safe_get(pillar1, 'walk_6min_total_m')} m", 
         f"{safe_get(pillar1, 'walk_6min_score')}/3.0", safe_get(pillar1, 'walk_6min_category')],
    ]
    
    t = Table(tests_data, colWidths=[2.5 * inch, 1.5 * inch, 1 * inch, 1 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Score Chart
    story.append(Paragraph("Performance Overview", styles['SubHeading']))
    chart = create_pillar1_chart(pillar1)
    story.append(chart)
    story.append(Paragraph("Chart shows percentage of maximum points achieved for each test", styles['CenterText']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Functional Age Impact
    impact = safe_float(pillar1, 'functional_age_impact')
    impact_text = f"{'+' if impact > 0 else ''}{impact:.1f} years"
    
    story.append(Paragraph("Pillar 1 Functional Age Impact", styles['SubHeading']))
    story.append(Paragraph(f"Based on physical performance tests, Pillar 1 contributes <b>{impact_text}</b> to functional age.", 
                          styles['ReportBody']))
    
    story.append(PageBreak())


def generate_pillar2_page(story: List, styles: Dict, pillar2, assessment, patient) -> None:
    """Generate Pillar 2: Cognitive Function page."""
    story.append(Paragraph("Pillar 2: Cognitive Function Assessment", styles['SectionHeading']))
    
    if not pillar2:
        story.append(Paragraph("Pillar 2 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Summary
    total = safe_float(pillar2, 'pillar2_total')
    category = safe_get(pillar2, 'pillar2_category', 'Not calculated')
    
    story.append(Paragraph(f"Total Score: <b>{total:.1f}/20</b> ({category})", styles['ReportBody']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Test Results Table
    story.append(Paragraph("Individual Test Results", styles['SubHeading']))
    
    tests_data = [
        ['Test', 'Result', 'Score', 'Category'],
        ['1. Immediate Memory', f"{safe_get(pillar2, 'memory_immediate_count')}/10 words", 
         f"{safe_get(pillar2, 'memory_immediate_points')}/2.0", safe_get(pillar2, 'memory_immediate_category')],
        ['2. Delayed Memory', f"{safe_get(pillar2, 'memory_delayed_count')}/10 words", 
         f"{safe_get(pillar2, 'memory_delayed_points')}/2.0", safe_get(pillar2, 'memory_delayed_category')],
        ['3. Digit Span Forward', f"{safe_get(pillar2, 'digit_span_forward')} digits", 
         f"{safe_get(pillar2, 'digit_span_forward_points')}/1.0", safe_get(pillar2, 'digit_span_forward_category')],
        ['4. Digit Span Backward', f"{safe_get(pillar2, 'digit_span_backward')} digits", 
         f"{safe_get(pillar2, 'digit_span_backward_points')}/1.0", safe_get(pillar2, 'digit_span_backward_category')],
        ['5. Trail Making A', f"{safe_get(pillar2, 'trails_a_time')} sec", 
         f"{safe_get(pillar2, 'trails_a_points')}/3.0", safe_get(pillar2, 'trails_a_category')],
        ['6. Trail Making B', f"{safe_get(pillar2, 'trails_b_time')} sec", 
         f"{safe_get(pillar2, 'trails_b_points')}/3.0", safe_get(pillar2, 'trails_b_category')],
        ['   B/A Ratio', f"{safe_get(pillar2, 'trails_ba_ratio')}", '—', 
         'Normal' if safe_float(pillar2, 'trails_ba_ratio') <= 3.0 else 'Elevated'],
        ['7. DSST (Symbol Substitution)', f"{safe_get(pillar2, 'dsst_score')} correct", 
         f"{safe_get(pillar2, 'dsst_points')}/3.0", safe_get(pillar2, 'dsst_category')],
        ['8. Clock Drawing', f"{safe_get(pillar2, 'clock_score_raw')}/7 components", 
         f"{safe_get(pillar2, 'clock_points')}/2.0", safe_get(pillar2, 'clock_category')],
        ['9. Verbal Fluency (Animals)', f"{safe_get(pillar2, 'verbal_fluency_animals')} animals", 
         f"{safe_get(pillar2, 'verbal_fluency_points')}/2.0", safe_get(pillar2, 'verbal_fluency_category')],
        ['10. PHQ-2 Depression', f"{safe_get(pillar2, 'phq2_total')}/6", 
         f"{safe_get(pillar2, 'phq2_points')}/1.0", safe_get(pillar2, 'phq2_category')],
        ['11. GAD-2 Anxiety', f"{safe_get(pillar2, 'gad2_total')}/6", 
         f"{safe_get(pillar2, 'gad2_points')}/1.0", safe_get(pillar2, 'gad2_category')],
    ]
    
    t = Table(tests_data, colWidths=[2.3 * inch, 1.7 * inch, 1 * inch, 1 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PILLAR2),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Score Chart
    story.append(Paragraph("Cognitive Performance Overview", styles['SubHeading']))
    chart = create_pillar2_chart(pillar2)
    story.append(chart)
    story.append(Paragraph("Chart shows percentage of maximum points achieved for each test", styles['CenterText']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Clinical Findings
    story.append(Paragraph("Clinical Interpretation", styles['SubHeading']))
    
    findings = []
    
    # DSST
    dsst_cat = safe_get(pillar2, 'dsst_category', '')
    if dsst_cat in ('Poor', 'Very Poor'):
        findings.append(Paragraph(
            f"⚠️ <b>Processing Speed:</b> DSST performance ({dsst_cat}) indicates slowed cognitive processing. "
            "Consider formal neuropsychological evaluation.",
            styles['AlertText']
        ))
    elif dsst_cat:
        findings.append(Paragraph(f"✓ Processing speed within {dsst_cat.lower()} range.", styles['SuccessText']))
    
    # Trails B/A Ratio
    ba_ratio = safe_float(pillar2, 'trails_ba_ratio')
    if ba_ratio > 3.5:
        findings.append(Paragraph(
            f"⚠️ <b>Executive Function:</b> B/A ratio of {ba_ratio:.1f} suggests significant executive dysfunction. "
            "Further evaluation recommended.",
            styles['AlertText']
        ))
    elif ba_ratio > 3.0:
        findings.append(Paragraph(
            f"⚠️ <b>Executive Function:</b> B/A ratio of {ba_ratio:.1f} mildly elevated - monitor for changes.",
            styles['AlertText']
        ))
    elif ba_ratio > 0:
        findings.append(Paragraph(f"✓ Executive function (B/A ratio {ba_ratio:.1f}) within normal limits.", styles['SuccessText']))
    
    # Digit Span
    ds_total = safe_float(pillar2, 'digit_span_total')
    ds_cat = safe_get(pillar2, 'digit_span_category', '')
    if ds_total < 10:
        findings.append(Paragraph(
            f"⚠️ <b>Working Memory:</b> Digit span total of {ds_total:.0f} indicates working memory deficit.",
            styles['AlertText']
        ))
    elif ds_cat:
        findings.append(Paragraph(f"✓ Working memory ({ds_cat.lower()}) within acceptable range.", styles['SuccessText']))
    
    # Verbal Fluency
    vf_animals = safe_float(pillar2, 'verbal_fluency_animals')
    vf_cat = safe_get(pillar2, 'verbal_fluency_category', '')
    if vf_animals < 12:
        findings.append(Paragraph(
            f"⚠️ <b>Verbal Fluency:</b> {vf_animals:.0f} animals in 60 seconds indicates language/executive concern.",
            styles['AlertText']
        ))
    elif vf_cat:
        findings.append(Paragraph(f"✓ Verbal fluency ({vf_cat.lower()}) within expected range.", styles['SuccessText']))
    
    if not findings:
        findings.append(Paragraph("Cognitive assessment data incomplete.", styles['ReportBody']))
    
    for finding in findings:
        story.append(finding)
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Functional Age Impact
    modifier = safe_float(pillar2, 'functional_age_modifier')
    modifier_text = f"{'+' if modifier > 0 else ''}{modifier:.1f} years"
    
    story.append(Paragraph("Pillar 2 Functional Age Impact", styles['SubHeading']))
    story.append(Paragraph(f"Based on cognitive performance tests, Pillar 2 contributes <b>{modifier_text}</b> to functional age.", 
                          styles['ReportBody']))
    
    story.append(PageBreak())


def generate_pillar3_page(story: List, styles: Dict, pillar3, assessment, patient) -> None:
    """Generate Pillar 3: Metabolic & Digestive Health page."""
    story.append(Paragraph("Pillar 3: Metabolic & Digestive Health", styles['SectionHeading']))
    
    if not pillar3:
        story.append(Paragraph("Pillar 3 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Summary
    total = safe_float(pillar3, 'pillar3_total')
    category = safe_get(pillar3, 'pillar3_category', 'Not calculated')
    
    story.append(Paragraph(f"Total Score: <b>{total:.1f}/20</b> ({category})", styles['ReportBody']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Test Results Table
    story.append(Paragraph("Individual Test Results", styles['SubHeading']))
    
    # Glucose display
    glucose_exact = getattr(pillar3, 'fasting_glucose', None)
    hba1c = getattr(pillar3, 'hba1c', None)
    glucose_cat = getattr(pillar3, 'glucose_category', None)
    if glucose_exact and hba1c:
        glucose_result = f"Fasting: {float(glucose_exact):.0f} mg/dL, HbA1c: {float(hba1c):.1f}%"
    elif glucose_cat:
        glucose_result = glucose_cat
    else:
        glucose_result = 'Not assessed'
    
    # Liver display
    liver_alt = getattr(pillar3, 'alt_value', None)
    liver_ast = getattr(pillar3, 'ast_value', None)
    liver_cat_input = getattr(pillar3, 'liver_category_input', None)
    if liver_alt and liver_ast:
        liver_result = f"ALT: {float(liver_alt):.0f}, AST: {float(liver_ast):.0f} U/L"
    elif liver_cat_input:
        liver_result = liver_cat_input
    else:
        liver_result = 'Not assessed'
    
    # CRP display
    crp_exact = getattr(pillar3, 'hs_crp', None)
    crp_cat_input = getattr(pillar3, 'crp_category_input', None)
    if crp_exact:
        crp_result = f"{float(crp_exact):.1f} mg/L"
    elif crp_cat_input:
        crp_result = crp_cat_input
    else:
        crp_result = 'Not assessed'
    
    # Helper function to format score
    def format_score(points, max_points):
        if points is None:
            return f"—/{max_points:.1f}"
        return f"{float(points):.1f}/{max_points:.1f}"
    
    tests_data = [
        ['Test', 'Result', 'Score', 'Category'],
        ['1. Glucose Control', glucose_result,
         format_score(getattr(pillar3, 'glucose_blood_points', None), 3.0),
         safe_get(pillar3, 'glucose_blood_category')],
        ['2. Functional Energy', 
         f"{safe_get(pillar3, 'post_meal_feeling')}, {safe_get(pillar3, 'fasting_tolerance')}" if getattr(pillar3, 'post_meal_feeling', None) else 'Not assessed',
         format_score(getattr(pillar3, 'glucose_functional_points', None), 2.0), '—'],
        ['3. Bowel Frequency', safe_get(pillar3, 'bowel_frequency'),
         format_score(getattr(pillar3, 'bowel_points', None), 2.0), '—'],
        ['4. Stool Consistency', safe_get(pillar3, 'stool_consistency'),
         format_score(getattr(pillar3, 'stool_points', None), 1.0), '—'],
        ['5. Acid Reflux', safe_get(pillar3, 'reflux_frequency'),
         format_score(getattr(pillar3, 'reflux_points', None), 2.0), '—'],
        ['6. Meal Comfort', safe_get(pillar3, 'meal_comfort'),
         format_score(getattr(pillar3, 'meal_comfort_points', None), 1.0), '—'],
        ['7. Bloating', safe_get(pillar3, 'bloating_frequency'),
         format_score(getattr(pillar3, 'bloating_points', None), 2.0), '—'],
        ['8. Abdominal Pain', safe_get(pillar3, 'abdominal_pain'),
         format_score(getattr(pillar3, 'pain_points', None), 1.0), '—'],
        ['9. Food Intolerances', safe_get(pillar3, 'food_intolerances'),
         format_score(getattr(pillar3, 'intolerance_points', None), 1.0), '—'],
        ['10. Liver Function', liver_result,
         format_score(getattr(pillar3, 'liver_points', None), 3.0),
         safe_get(pillar3, 'liver_category')],
        ['11. Inflammation (hs-CRP)', crp_result,
         format_score(getattr(pillar3, 'crp_points', None), 2.0),
         safe_get(pillar3, 'crp_risk_level')],
    ]
    
    t = Table(tests_data, colWidths=[2.3 * inch, 1.7 * inch, 1 * inch, 1 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PILLAR3),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Score Chart
    story.append(Paragraph("Metabolic & Digestive Performance Overview", styles['SubHeading']))
    chart = create_pillar3_chart(pillar3)
    story.append(chart)
    story.append(Paragraph("Chart shows percentage of maximum points achieved for each test category", styles['CenterText']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Clinical Interpretation
    story.append(Paragraph("Clinical Interpretation", styles['SubHeading']))
    
    findings = []
    
    # Glucose/Diabetes
    if getattr(pillar3, 'diabetes_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Diabetes:</b> Fasting glucose and/or HbA1c in diabetic range. "
            "Requires medical management and monitoring.",
            styles['AlertText']
        ))
    elif getattr(pillar3, 'prediabetes_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Prediabetes:</b> Elevated glucose levels indicate increased diabetes risk. "
            "Lifestyle modifications recommended: weight loss, exercise, dietary changes.",
            styles['AlertText']
        ))
    else:
        glucose_score = safe_float(pillar3, 'glucose_control_score')
        if glucose_score >= 2.5:
            findings.append(Paragraph("✓ Glucose control within optimal range.", styles['SuccessText']))
        elif glucose_score > 0:
            findings.append(Paragraph(f"Glucose control adequate but room for improvement.", styles['ReportBody']))
    
    # Liver Function
    if getattr(pillar3, 'liver_concern_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Liver Enzymes Elevated:</b> ALT/AST above normal range. "
            "Consider further evaluation: hepatitis screening, ultrasound, alcohol reduction.",
            styles['AlertText']
        ))
    else:
        liver_score = safe_float(pillar3, 'liver_function_score')
        if liver_score >= 2.5:
            findings.append(Paragraph("✓ Liver function within normal range.", styles['SuccessText']))
        elif liver_score > 0:
            findings.append(Paragraph(f"Liver enzymes acceptable.", styles['ReportBody']))
    
    # Inflammation
    crp_val = safe_float(pillar3, 'hs_crp')
    if crp_val > 3.0:
        findings.append(Paragraph(
            f"⚠️ <b>High Inflammation:</b> hs-CRP {crp_val:.1f} mg/L indicates elevated cardiovascular risk. "
            "Address: weight loss, exercise, anti-inflammatory diet, stress reduction.",
            styles['AlertText']
        ))
    elif crp_val > 1.0:
        findings.append(Paragraph(
            f"⚠️ <b>Moderate Inflammation:</b> hs-CRP {crp_val:.1f} mg/L - consider lifestyle modifications.",
            styles['AlertText']
        ))
    elif crp_val > 0:
        findings.append(Paragraph(f"✓ Inflammation markers low (hs-CRP {crp_val:.1f} mg/L).", styles['SuccessText']))
    
    # Digestive Function
    if getattr(pillar3, 'digestive_disorder_flag', None):
        # Check for specific patterns
        bowel_score = safe_float(pillar3, 'bowel_points')
        bloating_score = safe_float(pillar3, 'bloating_points')
        pain_score = safe_float(pillar3, 'pain_points')
        
        if bowel_score <= 0.5 and (bloating_score == 0 or pain_score == 0):
            findings.append(Paragraph(
                "⚠️ <b>IBS Pattern:</b> Abnormal bowel frequency and gut symptoms suggest irritable bowel syndrome. "
                "Consider: food diary, FODMAP diet, gastroenterology referral.",
                styles['AlertText']
            ))
        else:
            findings.append(Paragraph(
                "⚠️ <b>Digestive Symptoms:</b> Multiple digestive issues identified. "
                "Consider gastroenterology consultation.",
                styles['AlertText']
            ))
    else:
        digestive_total = (safe_float(pillar3, 'bowel_points') + 
                          safe_float(pillar3, 'stool_points') +
                          safe_float(pillar3, 'reflux_points') +
                          safe_float(pillar3, 'meal_comfort_points'))
        gut_total = (safe_float(pillar3, 'bloating_points') + 
                    safe_float(pillar3, 'pain_points') +
                    safe_float(pillar3, 'intolerance_points'))
        combined_digestive = digestive_total + gut_total
        
        if combined_digestive >= 8.0:
            findings.append(Paragraph("✓ Digestive function and gut health optimal.", styles['SuccessText']))
        elif combined_digestive >= 6.0:
            findings.append(Paragraph("Digestive function acceptable with minor issues.", styles['ReportBody']))
        else:
            findings.append(Paragraph(
                "⚠️ Multiple digestive symptoms reported. Consider elimination diet, probiotic trial, "
                "or gastroenterology consultation.",
                styles['AlertText']
            ))
    
    if not findings:
        findings.append(Paragraph("Metabolic and digestive assessment data incomplete.", styles['ReportBody']))
    
    for finding in findings:
        story.append(finding)
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Clinical Alerts Summary
    alerts = []
    if getattr(pillar3, 'diabetes_flag', None):
        alerts.append("• Diabetes - medical management required")
    if getattr(pillar3, 'prediabetes_flag', None):
        alerts.append("• Prediabetes - lifestyle intervention needed")
    if getattr(pillar3, 'liver_concern_flag', None):
        alerts.append("• Elevated liver enzymes - further workup indicated")
    if getattr(pillar3, 'inflammation_flag', None):
        alerts.append("• High inflammation (hs-CRP > 3 mg/L) - CV risk factor")
    if getattr(pillar3, 'digestive_disorder_flag', None):
        alerts.append("• Digestive disorder symptoms - GI evaluation recommended")
    
    if alerts:
        story.append(Paragraph("Clinical Alerts", styles['SubHeading']))
        for alert in alerts:
            story.append(Paragraph(alert, styles['AlertText']))
        story.append(Spacer(1, 0.2 * inch))
    
    # Functional Age Impact
    impact = safe_float(pillar3, 'functional_age_modifier')
    impact_text = f"{'+' if impact > 0 else ''}{impact:.1f} years"
    percentage = (total / 20.0 * 100) if total > 0 else 0
    
    story.append(Paragraph("Pillar 3 Functional Age Impact", styles['SubHeading']))
    story.append(Paragraph(
        f"Based on metabolic and digestive health ({total:.1f}/20, {percentage:.0f}%), "
        f"Pillar 3 contributes <b>{impact_text}</b> to functional age.",
        styles['ReportBody']
    ))
    
    story.append(PageBreak())


def generate_pillar4_page(story: List, styles: Dict, pillar4, assessment, patient) -> None:
    """Generate Pillar 4: Vitality & Hormones page."""
    story.append(Paragraph("Pillar 4: Vitality & Hormones", styles['SectionHeading']))
    
    if not pillar4:
        story.append(Paragraph("Pillar 4 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Summary
    total = safe_float(pillar4, 'pillar4_total')
    category = safe_get(pillar4, 'pillar4_category', 'Not calculated')
    
    story.append(Paragraph(f"Total Score: <b>{total:.1f}/20</b> ({category})", styles['ReportBody']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Test Results Table
    story.append(Paragraph("Individual Test Results", styles['SubHeading']))
    
    # Helper function to format score
    def format_score(points, max_points):
        if points is None:
            return f"—/{max_points:.1f}"
        return f"{float(points):.1f}/{max_points:.1f}"
    
    # Thyroid display
    thyroid_mode = safe_get(pillar4, 'thyroid_input_mode', 'category')
    if thyroid_mode == 'exact':
        tsh = safe_float(pillar4, 'tsh')
        t4 = safe_float(pillar4, 'free_t4')
        t3 = safe_float(pillar4, 'free_t3')
        thyroid_result = f"TSH: {tsh:.2f}" if tsh else "Not assessed"
        if t4:
            thyroid_result += f", T4: {t4:.2f}"
        if t3:
            thyroid_result += f", T3: {t3:.2f}"
    else:
        thyroid_result = safe_get(pillar4, 'thyroid_category_input', 'Not assessed')
    
    # Hormones display (sex-specific)
    if patient.sex == 'male':
        hormone_mode = safe_get(pillar4, 'hormone_input_mode', 'category')
        if hormone_mode == 'exact':
            total_t = safe_float(pillar4, 'total_testosterone')
            hormone_result = f"Total T: {total_t:.0f} ng/dL" if total_t else "Not assessed"
        else:
            hormone_result = safe_get(pillar4, 'testosterone_category', 'Not assessed')
    else:  # female
        female_mode = safe_get(pillar4, 'female_hormone_input_mode', 'symptoms')
        if female_mode == 'exact':
            fsh = safe_float(pillar4, 'fsh')
            estradiol = safe_float(pillar4, 'estradiol_female')
            hormone_result = ""
            if fsh:
                hormone_result += f"FSH: {fsh:.1f}"
            if estradiol:
                hormone_result += f", E2: {estradiol:.0f}" if hormone_result else f"E2: {estradiol:.0f}"
            if not hormone_result:
                hormone_result = "Labs assessed"
        else:
            meno_status = safe_get(pillar4, 'menopause_status', 'Not assessed')
            symptoms = safe_get(pillar4, 'female_symptoms', '')
            hormone_result = f"{meno_status}, {symptoms} symptoms"
    
    # Sexual health display
    sexual_status = safe_get(pillar4, 'sexual_health', 'Not assessed')
    if sexual_status == 'skip':
        sexual_result = 'Prefer not to answer'
    else:
        sexual_result = sexual_status
    
    # Vitamin D display
    vitd_mode = safe_get(pillar4, 'vitd_input_mode', 'category')
    if vitd_mode == 'exact':
        vitd = safe_float(pillar4, 'vitamin_d')
        vitd_result = f"{vitd:.0f} ng/mL" if vitd else "Not assessed"
    else:
        vitd_result = safe_get(pillar4, 'vitd_category_input', 'Not assessed')
    
    # Iron display
    iron_mode = safe_get(pillar4, 'iron_input_mode', 'category')
    if iron_mode == 'exact':
        hb = safe_float(pillar4, 'hemoglobin')
        iron_result = f"Hb: {hb:.1f} g/dL" if hb else "Not assessed"
    else:
        iron_result = safe_get(pillar4, 'iron_category_input', 'Not assessed')
    
    # Exercise display
    ex_freq = safe_get(pillar4, 'exercise_frequency', 'Not assessed')
    cardio = getattr(pillar4, 'exercise_cardio', False)
    strength = getattr(pillar4, 'exercise_strength', False)
    flex = getattr(pillar4, 'exercise_flexibility', False)
    types = []
    if cardio:
        types.append('cardio')
    if strength:
        types.append('strength')
    if flex:
        types.append('flexibility')
    exercise_result = f"{ex_freq} days/wk" if ex_freq != 'Not assessed' else ex_freq
    if types:
        exercise_result += f" ({', '.join(types)})"
    
    # Sleep display
    sleep_dur = safe_get(pillar4, 'sleep_duration', 'Not assessed')
    sleep_quality = safe_get(pillar4, 'sleep_quality', '')
    if sleep_dur != 'Not assessed':
        sleep_result = f"{sleep_dur} hrs, {sleep_quality} rested"
    else:
        sleep_result = 'Not assessed'
    
    # Appearance display
    skin = safe_get(pillar4, 'skin_elasticity', '')
    hair = safe_get(pillar4, 'hair_health', '')
    if skin or hair:
        appearance_result = f"{skin} skin, {hair} hair"
    else:
        appearance_result = 'Not assessed'
    
    # Stress display
    stress_lvl = safe_float(pillar4, 'stress_level')
    if stress_lvl is not None:
        stress_result = f"{int(stress_lvl)}/10"
    else:
        stress_result = 'Not assessed'
    
    tests_data = [
        ['Test', 'Result', 'Score', 'Category'],
        ['1. Thyroid Function', thyroid_result,
         format_score(getattr(pillar4, 'thyroid_points', None), 4.0),
         safe_get(pillar4, 'thyroid_category')],
        ['2. Sex Hormones', hormone_result,
         format_score(getattr(pillar4, 'hormone_points', None), 4.0),
         safe_get(pillar4, 'hormone_assessment')],
        ['3. Sexual Health', sexual_result,
         format_score(getattr(pillar4, 'sexual_health_points', None), 1.0), '—'],
        ['4. Vitamin D', vitd_result,
         format_score(getattr(pillar4, 'vitd_points', None), 2.0),
         safe_get(pillar4, 'vitd_category')],
        ['5. Hemoglobin & Iron', iron_result,
         format_score(getattr(pillar4, 'iron_points', None), 2.0),
         safe_get(pillar4, 'iron_category')],
        ['6. Exercise Habits', exercise_result,
         format_score(getattr(pillar4, 'exercise_points', None), 2.0), '—'],
        ['7. Sleep Quality', sleep_result,
         format_score(getattr(pillar4, 'sleep_points', None), 3.0), '—'],
        ['8. Skin & Hair Health', appearance_result,
         format_score(getattr(pillar4, 'appearance_points', None), 1.0), '—'],
        ['9. Stress Level', stress_result,
         format_score(getattr(pillar4, 'stress_points', None), 1.0),
         safe_get(pillar4, 'stress_category')],
    ]
    
    t = Table(tests_data, colWidths=[2.2 * inch, 1.8 * inch, 1 * inch, 1 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PILLAR4),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Score Chart
    story.append(Paragraph("Vitality & Hormones Performance Overview", styles['SubHeading']))
    chart = create_pillar4_chart(pillar4)
    story.append(chart)
    story.append(Paragraph("Chart shows percentage of maximum points achieved for each test", styles['CenterText']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Clinical Interpretation
    story.append(Paragraph("Clinical Interpretation", styles['SubHeading']))
    
    findings = []
    
    # Clinical Alerts
    if getattr(pillar4, 'thyroid_dysfunction_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Thyroid Dysfunction:</b> TSH out of optimal range. "
            "Requires medical evaluation and possible thyroid medication adjustment.",
            styles['AlertText']
        ))
    else:
        thyroid_score = safe_float(pillar4, 'thyroid_points')
        if thyroid_score >= 3.5:
            findings.append(Paragraph("✓ Thyroid function optimal.", styles['SuccessText']))
    
    if getattr(pillar4, 'low_testosterone_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Low Testosterone/Hypogonadism:</b> Testosterone below normal for age. "
            "Consider endocrinology referral for hormone replacement therapy evaluation.",
            styles['AlertText']
        ))
    elif getattr(pillar4, 'hormonal_imbalance_flag', None):
        if patient.sex == 'female':
            findings.append(Paragraph(
                "⚠️ <b>Hormonal Imbalance:</b> Hormone levels or symptoms indicate imbalance. "
                "Consider gynecology/endocrinology consultation.",
                styles['AlertText']
            ))
    else:
        hormone_score = safe_float(pillar4, 'hormone_points')
        if hormone_score >= 3.0:
            findings.append(Paragraph("✓ Hormone levels within healthy range.", styles['SuccessText']))
    
    if getattr(pillar4, 'vitamin_d_deficiency_flag', None):
        vitd_val = safe_float(pillar4, 'vitamin_d')
        if vitd_val and vitd_val < 20:
            findings.append(Paragraph(
                f"⚠️ <b>Vitamin D Deficiency:</b> Level {vitd_val:.0f} ng/mL (severe deficiency). "
                "Start 4,000-5,000 IU/day supplementation and recheck in 8-12 weeks.",
                styles['AlertText']
            ))
        else:
            findings.append(Paragraph(
                "⚠️ <b>Vitamin D Insufficiency:</b> Below optimal. "
                "Recommend 2,000-4,000 IU/day supplementation.",
                styles['AlertText']
            ))
    else:
        vitd_score = safe_float(pillar4, 'vitd_points')
        if vitd_score >= 1.8:
            findings.append(Paragraph("✓ Vitamin D levels optimal.", styles['SuccessText']))
    
    if getattr(pillar4, 'anemia_flag', None):
        hb_val = safe_float(pillar4, 'hemoglobin')
        if hb_val and hb_val < 10:
            findings.append(Paragraph(
                f"⚠️ <b>Severe Anemia:</b> Hemoglobin {hb_val:.1f} g/dL. "
                "Urgent: Check iron, B12, folate. Consider iron infusion or transfusion if symptomatic.",
                styles['AlertText']
            ))
        else:
            findings.append(Paragraph(
                "⚠️ <b>Anemia:</b> Low hemoglobin. "
                "Check iron studies, B12, folate. Consider iron supplementation.",
                styles['AlertText']
            ))
    else:
        iron_score = safe_float(pillar4, 'iron_points')
        if iron_score >= 1.8:
            findings.append(Paragraph("✓ Hemoglobin and iron status normal.", styles['SuccessText']))
    
    if getattr(pillar4, 'sleep_disorder_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Sleep Disorder:</b> Poor sleep duration or quality. "
            "Consider: sleep hygiene, screen time reduction, sleep study if snoring/apnea suspected.",
            styles['AlertText']
        ))
    else:
        sleep_score = safe_float(pillar4, 'sleep_points')
        if sleep_score >= 2.5:
            findings.append(Paragraph("✓ Sleep duration and quality good.", styles['SuccessText']))
    
    if getattr(pillar4, 'chronic_stress_flag', None):
        findings.append(Paragraph(
            "⚠️ <b>Chronic High Stress:</b> Stress level ≥8/10. "
            "Recommend: counseling, mindfulness/meditation, stress management program.",
            styles['AlertText']
        ))
    else:
        stress_score = safe_float(pillar4, 'stress_points')
        if stress_score >= 0.75:
            findings.append(Paragraph("✓ Stress levels manageable.", styles['SuccessText']))
    
    # Exercise assessment
    exercise_score = safe_float(pillar4, 'exercise_points')
    if exercise_score < 1.0:
        findings.append(Paragraph(
            "⚠️ <b>Insufficient Exercise:</b> Below recommended activity levels. "
            "Target: 150 min/week moderate cardio + 2 days strength training.",
            styles['AlertText']
        ))
    elif exercise_score >= 1.75:
        findings.append(Paragraph("✓ Exercise habits excellent.", styles['SuccessText']))
    
    if not findings:
        findings.append(Paragraph("All vitality and hormone markers within healthy ranges.", styles['ReportBody']))
    
    for finding in findings:
        story.append(finding)
        story.append(Spacer(1, 0.1 * inch))
    
    # Functional Age Impact
    impact = safe_float(pillar4, 'functional_age_modifier')
    if impact > 0:
        impact_text = f"+{impact:.1f} years"
    elif impact < 0:
        impact_text = f"{impact:.1f} years"
    else:
        impact_text = "0 years"
    
    percentage = (total / 20.0 * 100) if total > 0 else 0
    
    story.append(Paragraph("Pillar 4 Functional Age Impact", styles['SubHeading']))
    story.append(Paragraph(
        f"Based on vitality and hormone health ({total:.1f}/20, {percentage:.0f}%), "
        f"Pillar 4 contributes <b>{impact_text}</b> to functional age.",
        styles['ReportBody']
    ))
    
    story.append(PageBreak())


def generate_pillar5_page(story: List, styles: Dict, pillar5, assessment, patient) -> None:
    """Generate Pillar 5: Disease Prevention & Clinical Biomarkers page."""
    story.append(Paragraph("Pillar 5: Disease Prevention & Clinical Biomarkers", styles['SectionHeading']))
    
    if not pillar5:
        story.append(Paragraph("Pillar 5 data not available.", styles['ReportBody']))
        story.append(PageBreak())
        return
    
    # Summary
    total = safe_float(pillar5, 'pillar5_total')
    category = safe_get(pillar5, 'pillar5_category', 'Not calculated')
    
    story.append(Paragraph(f"Total Score: <b>{total:.1f}/20</b> ({category})", styles['ReportBody']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Test Results Table
    story.append(Paragraph("Individual Test Results", styles['SubHeading']))
    
    # Helper function to format score
    def format_score(points, max_points):
        if points is None:
            return f"—/{max_points:.1f}"
        return f"{float(points):.1f}/{max_points:.1f}"
    
    # Standard Lipids
    lipids_mode = safe_get(pillar5, 'lipids_input_mode', 'category')
    if lipids_mode == 'exact':
        ldl = safe_float(pillar5, 'ldl_cholesterol')
        hdl = safe_float(pillar5, 'hdl_cholesterol')
        tg = safe_float(pillar5, 'triglycerides')
        lipids_result = f"LDL:{ldl:.0f}, HDL:{hdl:.0f}, TG:{tg:.0f}" if ldl and hdl and tg else "Not assessed"
    else:
        lipids_result = safe_get(pillar5, 'lipids_category_input', 'Not assessed')
    
    # Advanced Lipids
    apob = safe_float(pillar5, 'apob')
    lpa = safe_float(pillar5, 'lp_a')
    if apob or lpa:
        adv_lipids = []
        if apob:
            adv_lipids.append(f"ApoB:{apob:.0f}")
        if lpa:
            adv_lipids.append(f"Lp(a):{lpa:.0f}")
        adv_lipids_result = ", ".join(adv_lipids)
    else:
        adv_lipids_result = "Not assessed"
    
    # Cardiac Imaging
    cac = safe_float(pillar5, 'cac_score')
    if cac is not None:
        cardiac_result = f"CAC:{cac:.0f}"
    else:
        cardiac_result = safe_get(pillar5, 'cac_category', 'Not performed')
    
    # Kidney
    egfr = safe_float(pillar5, 'egfr')
    if egfr:
        kidney_result = f"eGFR:{egfr:.0f} mL/min/1.73m²"
    else:
        kidney_result = safe_get(pillar5, 'kidney_category_input', 'Not assessed')
    
    # Cancer Screening
    compliance = safe_float(pillar5, 'screening_compliance_pct')
    if compliance is not None:
        screening_result = f"{compliance:.0f}% compliant"
    else:
        screening_result = "Not assessed"
    
    # Organ Imaging
    abdomen = safe_get(pillar5, 'abdomen_imaging', 'Not performed')
    chest = safe_get(pillar5, 'chest_imaging', 'Not performed')
    imaging_result = f"Abd:{abdomen}, Chest:{chest}"
    
    # Bone
    tscore = safe_float(pillar5, 'dexa_t_score')
    if tscore is not None:
        bone_result = f"T-score:{tscore:.1f}"
    else:
        bone_result = safe_get(pillar5, 'bone_category', 'Not performed')
    
    # Sensory
    vision = safe_get(pillar5, 'vision_status', 'Not assessed')
    hearing = safe_get(pillar5, 'hearing_status', 'Not assessed')
    sensory_result = f"{vision}/{hearing}"
    
    # Chronic Disease
    has_disease = getattr(pillar5, 'has_chronic_disease', False)
    if has_disease:
        mgmt = safe_get(pillar5, 'disease_management', 'Not assessed')
        chronic_result = f"Present, {mgmt} management"
    else:
        chronic_result = "No chronic disease"
    
    tests_data = [
        ['Test', 'Result', 'Score', 'Notes'],
        ['1. Standard Lipids', lipids_result,
         format_score(getattr(pillar5, 'lipids_total_points', None), 4.0),
         safe_get(pillar5, 'lipids_category')],
        ['2. Advanced Lipids', adv_lipids_result,
         format_score(getattr(pillar5, 'advanced_lipids_points', None), 2.0), '—'],
        ['3. Cardiac Imaging', cardiac_result,
         format_score(getattr(pillar5, 'cardiac_imaging_points', None), 3.0), '—'],
        ['4. Kidney Function', kidney_result,
         format_score(getattr(pillar5, 'kidney_points', None), 2.0),
         safe_get(pillar5, 'kidney_category')],
        ['5. Cancer Screening', screening_result,
         format_score(getattr(pillar5, 'screening_points', None), 4.0), '—'],
        ['6. Organ Imaging', imaging_result,
         format_score(getattr(pillar5, 'organ_imaging_points', None), 2.0), '—'],
        ['7. Bone Health', bone_result,
         format_score(getattr(pillar5, 'bone_points', None), 1.0),
         safe_get(pillar5, 'bone_category')],
        ['8. Sensory', sensory_result,
         format_score(getattr(pillar5, 'sensory_points', None), 1.0), '—'],
        ['9. Chronic Disease', chronic_result,
         format_score(getattr(pillar5, 'chronic_disease_points', None), 1.0), '—'],
    ]
    
    BRAND_PILLAR5 = colors.HexColor('#16a085')  # Green
    
    t = Table(tests_data, colWidths=[2.2 * inch, 1.8 * inch, 1 * inch, 1 * inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_PILLAR5),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3 * inch))
    
    # Clinical Alerts
    if getattr(pillar5, 'clinical_alerts', None):
        story.append(Paragraph("Clinical Alerts", styles['SubHeading']))
        for alert in pillar5.clinical_alerts:
            alert_text = f"⚠️ <b>{alert.get('code', 'ALERT')}:</b> {alert.get('message', '')}"
            story.append(Paragraph(alert_text, styles['AlertText']))
        story.append(Spacer(1, 0.2 * inch))
    
    # Functional Age Impact
    impact = safe_float(pillar5, 'functional_age_modifier')
    percentage = (total / 20) * 100 if total else 0
    
    if impact > 0:
        impact_text = f"+{impact:.1f} years (aging faster)"
    elif impact < 0:
        impact_text = f"{impact:.1f} years (aging slower)"
    else:
        impact_text = "0 years (neutral)"
    
    story.append(Paragraph("Pillar 5 Functional Age Impact", styles['SubHeading']))
    story.append(Paragraph(
        f"Based on disease prevention and clinical biomarkers ({total:.1f}/20, {percentage:.0f}%), "
        f"Pillar 5 contributes <b>{impact_text}</b> to functional age.",
        styles['ReportBody']
    ))
    
    story.append(PageBreak())


def generate_recommendations_page(story: List, styles: Dict, section0, section1, pillar1, pillar2, patient) -> None:
    """Generate Clinical Alerts & Recommendations page."""
    story.append(Paragraph("Clinical Alerts & Recommendations", styles['SectionHeading']))
    
    # Collect all areas for improvement
    areas_for_improvement = []
    
    # =========================================================================
    # Fall Risk Assessment (expanded criteria)
    # =========================================================================
    story.append(Paragraph("Fall Risk Assessment", styles['SubHeading']))
    
    fall_factors = []
    if pillar1:
        gait = safe_float(pillar1, 'gait_speed_ms')
        balance = safe_float(pillar1, 'single_leg_better_best')
        tug = safe_float(pillar1, 'tug_faster_sec')
        gait_cat = safe_get(pillar1, 'gait_category', '')
        balance_cat = safe_get(pillar1, 'balance_category', '')
        tug_cat = safe_get(pillar1, 'tug_category', '')
        
        # Critical thresholds
        if gait > 0 and gait < 0.8:
            fall_factors.append(f"Gait speed {gait:.2f} m/s (< 0.8 m/s HIGH RISK threshold)")
        elif gait > 0 and gait < 1.0:
            fall_factors.append(f"Gait speed {gait:.2f} m/s (< 1.0 m/s - below optimal)")
            
        if balance > 0 and balance < 5:
            fall_factors.append(f"Single-leg balance {balance:.1f} sec (< 5 sec HIGH RISK threshold)")
        elif balance > 0 and balance < 10:
            fall_factors.append(f"Single-leg balance {balance:.1f} sec (< 10 sec - below optimal)")
            
        if tug > 20:
            fall_factors.append(f"TUG time {tug:.1f} sec (> 20 sec HIGH RISK threshold)")
        elif tug > 12:
            fall_factors.append(f"TUG time {tug:.1f} sec (> 12 sec - mobility concern)")
    
    if len(fall_factors) >= 2:
        story.append(Paragraph("⚠️ <b>HIGH FALL RISK</b> - Multiple risk factors identified:", styles['AlertText']))
        for factor in fall_factors:
            story.append(Paragraph(f"  • {factor}", styles['AlertText']))
        story.append(Paragraph("<b>Recommendation:</b> Comprehensive fall prevention program, home safety assessment, "
                              "physical therapy referral for balance and gait training.", styles['ReportBody']))
        areas_for_improvement.append(('Fall Prevention', 'HIGH PRIORITY', 
            'Balance exercises, gait training, home safety modifications'))
    elif len(fall_factors) == 1:
        story.append(Paragraph("⚠️ <b>MODERATE FALL RISK</b> - Risk factor identified:", styles['AlertText']))
        story.append(Paragraph(f"  • {fall_factors[0]}", styles['ReportBody']))
        story.append(Paragraph("<b>Recommendation:</b> Balance and gait training exercises, consider Tai Chi or yoga.", 
                              styles['ReportBody']))
        areas_for_improvement.append(('Balance/Mobility', 'MODERATE', 
            'Balance exercises, Tai Chi, gait training'))
    else:
        story.append(Paragraph("✓ No significant fall risk factors identified.", styles['SuccessText']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # =========================================================================
    # Sarcopenia Assessment
    # =========================================================================
    story.append(Paragraph("Sarcopenia Assessment", styles['SubHeading']))
    
    sarcopenia_indicators = []
    if pillar1 and getattr(pillar1, 'sarcopenia_flag', None):
        grip = safe_get(pillar1, 'grip_dominant_best')
        sarcopenia_indicators.append(f"Low grip strength: {grip} kg (below EWGSOP2 threshold)")
    if section1 and getattr(section1, 'sarcopenia_risk', None):
        lmi = safe_get(section1, 'lean_mass_index')
        sarcopenia_indicators.append(f"Low lean mass index: {lmi} kg/m²")
    if pillar1:
        gait = safe_float(pillar1, 'gait_speed_ms')
        if gait > 0 and gait < 0.8:
            sarcopenia_indicators.append(f"Slow gait speed: {gait:.2f} m/s (functional impairment)")
    
    if sarcopenia_indicators:
        story.append(Paragraph("⚠️ <b>SARCOPENIA SCREENING POSITIVE</b>:", styles['AlertText']))
        for indicator in sarcopenia_indicators:
            story.append(Paragraph(f"  • {indicator}", styles['ReportBody']))
        story.append(Paragraph("<b>Recommendation:</b> DEXA body composition if not done, progressive resistance training "
                              "2-3x/week, protein intake 1.0-1.2 g/kg/day, vitamin D assessment.", 
                              styles['ReportBody']))
        areas_for_improvement.append(('Muscle Mass/Strength', 'HIGH PRIORITY',
            'Resistance training, protein optimization, vitamin D check'))
    else:
        story.append(Paragraph("✓ No sarcopenia indicators identified.", styles['SuccessText']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # =========================================================================
    # Cardiorespiratory Fitness (sex-adjusted)
    # =========================================================================
    story.append(Paragraph("Cardiorespiratory Fitness", styles['SubHeading']))
    
    sex = patient.sex if patient else 'male'
    vo2_threshold_poor = 20 if sex == 'male' else 17
    vo2_threshold_below_avg = 30 if sex == 'male' else 25
    
    if pillar1:
        vo2 = safe_float(pillar1, 'vo2_max')
        vo2_cat = safe_get(pillar1, 'vo2_category', '')
        
        if vo2 > 0:
            if vo2 < vo2_threshold_poor:
                story.append(Paragraph(f"⚠️ <b>SEVERELY IMPAIRED</b>: VO2 max {vo2:.1f} mL/kg/min ({vo2_cat})", 
                                      styles['AlertText']))
                story.append(Paragraph("<b>Recommendation:</b> Cardiac evaluation recommended before exercise program. "
                                      "Begin with supervised low-intensity aerobic activity (walking, stationary cycling).", 
                                      styles['ReportBody']))
                areas_for_improvement.append(('Cardiorespiratory Fitness', 'HIGH PRIORITY',
                    'Cardiac evaluation, supervised low-intensity aerobic program'))
            elif vo2 < vo2_threshold_below_avg:
                story.append(Paragraph(f"⚠️ <b>BELOW AVERAGE</b>: VO2 max {vo2:.1f} mL/kg/min ({vo2_cat})", 
                                      styles['AlertText']))
                story.append(Paragraph("<b>Recommendation:</b> Structured aerobic exercise program 3-5x/week, "
                                      "30+ minutes per session. Target 150 min/week moderate or 75 min/week vigorous activity.", 
                                      styles['ReportBody']))
                areas_for_improvement.append(('Cardiorespiratory Fitness', 'MODERATE',
                    '150 min/week moderate aerobic activity'))
            else:
                story.append(Paragraph(f"✓ Cardiorespiratory fitness adequate: VO2 max {vo2:.1f} mL/kg/min ({vo2_cat})", 
                                      styles['SuccessText']))
        else:
            story.append(Paragraph("VO2 max not assessed.", styles['ReportBody']))
    else:
        story.append(Paragraph("VO2 max not assessed.", styles['ReportBody']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # =========================================================================
    # Endurance Assessment (6MWT)
    # =========================================================================
    story.append(Paragraph("Endurance Assessment", styles['SubHeading']))
    
    if pillar1:
        walk_dist = safe_float(pillar1, 'walk_6min_total_m')
        walk_cat = safe_get(pillar1, 'walk_6min_category', '')
        walk_pct = safe_float(pillar1, 'walk_6min_pct_predicted')
        
        if walk_dist > 0:
            if walk_dist < 300:
                story.append(Paragraph(f"⚠️ <b>SEVERE ENDURANCE DEFICIT</b>: 6MWT {walk_dist:.0f}m ({walk_cat})", 
                                      styles['AlertText']))
                story.append(Paragraph("<b>Recommendation:</b> Consider cardiac/pulmonary evaluation. "
                                      "Progressive walking program starting with tolerable distances.", 
                                      styles['ReportBody']))
                areas_for_improvement.append(('Endurance', 'HIGH PRIORITY',
                    'Medical evaluation, progressive walking program'))
            elif walk_dist < 400:
                story.append(Paragraph(f"⚠️ <b>BELOW AVERAGE ENDURANCE</b>: 6MWT {walk_dist:.0f}m ({walk_cat})", 
                                      styles['AlertText']))
                story.append(Paragraph("<b>Recommendation:</b> Daily walking program, gradually increasing distance and pace.", 
                                      styles['ReportBody']))
                areas_for_improvement.append(('Endurance', 'MODERATE',
                    'Daily walking, gradually increase distance'))
            elif walk_pct > 0 and walk_pct < 80:
                story.append(Paragraph(f"⚠️ 6MWT {walk_dist:.0f}m ({walk_pct:.0f}% of predicted) - below expected for age", 
                                      styles['AlertText']))
                areas_for_improvement.append(('Endurance', 'LOW',
                    'Increase walking/aerobic activity'))
            else:
                story.append(Paragraph(f"✓ Endurance adequate: 6MWT {walk_dist:.0f}m ({walk_cat})", 
                                      styles['SuccessText']))
        else:
            story.append(Paragraph("6-Minute Walk Test not performed.", styles['ReportBody']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # =========================================================================
    # Strength Assessment
    # =========================================================================
    story.append(Paragraph("Strength Assessment", styles['SubHeading']))
    
    strength_concerns = []
    if pillar1:
        chair_reps = safe_float(pillar1, 'chair_stand_reps')
        chair_score = safe_float(pillar1, 'chair_stand_score')
        chair_cat = safe_get(pillar1, 'chair_stand_category', '')
        grip_score = safe_float(pillar1, 'grip_score')
        grip_cat = safe_get(pillar1, 'grip_category', '')
        
        if chair_score > 0 and chair_score < 1.5:
            strength_concerns.append(f"Lower body: Chair stand {chair_reps:.0f} reps ({chair_cat})")
        if grip_score > 0 and grip_score < 1.5:
            strength_concerns.append(f"Upper body: Grip strength ({grip_cat})")
    
    if strength_concerns:
        story.append(Paragraph("⚠️ <b>STRENGTH DEFICITS IDENTIFIED</b>:", styles['AlertText']))
        for concern in strength_concerns:
            story.append(Paragraph(f"  • {concern}", styles['ReportBody']))
        story.append(Paragraph("<b>Recommendation:</b> Progressive resistance training 2-3x/week targeting major muscle groups. "
                              "Include squats, lunges, rows, and presses.", styles['ReportBody']))
        areas_for_improvement.append(('Strength', 'MODERATE',
            'Resistance training 2-3x/week'))
    else:
        story.append(Paragraph("✓ Strength adequate for functional activities.", styles['SuccessText']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # =========================================================================
    # Flexibility Assessment
    # =========================================================================
    story.append(Paragraph("Flexibility Assessment", styles['SubHeading']))
    
    if pillar1:
        flex_score = safe_float(pillar1, 'flexibility_score')
        flex_cm = safe_float(pillar1, 'flexibility_best_cm')
        flex_cat = safe_get(pillar1, 'flexibility_category', '')
        
        if flex_score > 0 and flex_score < 1.0:
            story.append(Paragraph(f"⚠️ <b>LIMITED FLEXIBILITY</b>: Sit-and-reach {flex_cm:.1f} cm ({flex_cat})", 
                                  styles['AlertText']))
            story.append(Paragraph("<b>Recommendation:</b> Daily stretching routine, focus on hamstrings, hip flexors, "
                                  "and lower back. Consider yoga or Pilates.", styles['ReportBody']))
            areas_for_improvement.append(('Flexibility', 'LOW',
                'Daily stretching, yoga/Pilates'))
        elif flex_score > 0:
            story.append(Paragraph(f"✓ Flexibility adequate: Sit-and-reach {flex_cm:.1f} cm ({flex_cat})", 
                                  styles['SuccessText']))
        else:
            story.append(Paragraph("Flexibility not assessed.", styles['ReportBody']))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # =========================================================================
    # Cognitive Function Assessment (Pillar 2)
    # =========================================================================
    story.append(Paragraph("Cognitive Function Assessment", styles['SubHeading']))
    
    if pillar2:
        cognitive_concerns = []
        
        # DSST - Processing Speed
        dsst_cat = safe_get(pillar2, 'dsst_category', '')
        if dsst_cat in ('Poor', 'Very Poor'):
            cognitive_concerns.append(f"Processing speed: DSST performance {dsst_cat}")
        
        # Executive Function - Trails B/A Ratio
        ba_ratio = safe_float(pillar2, 'trails_ba_ratio')
        if ba_ratio > 3.5:
            cognitive_concerns.append(f"Executive function: B/A ratio {ba_ratio:.1f} significantly elevated")
        elif ba_ratio > 3.0:
            cognitive_concerns.append(f"Executive function: B/A ratio {ba_ratio:.1f} mildly elevated")
        
        # Working Memory - Digit Span
        ds_total = safe_float(pillar2, 'digit_span_total')
        if ds_total > 0 and ds_total < 10:
            cognitive_concerns.append(f"Working memory: Digit span {ds_total:.0f} (deficit indicated)")
        
        # Verbal Fluency
        vf_animals = safe_float(pillar2, 'verbal_fluency_animals')
        if vf_animals > 0 and vf_animals < 12:
            cognitive_concerns.append(f"Verbal fluency: {vf_animals:.0f} animals in 60 sec (below expected)")
        
        if cognitive_concerns:
            story.append(Paragraph("⚠️ <b>COGNITIVE CONCERNS IDENTIFIED</b>:", styles['AlertText']))
            for concern in cognitive_concerns:
                story.append(Paragraph(f"  • {concern}", styles['ReportBody']))
            story.append(Paragraph("<b>Recommendation:</b> Consider formal neuropsychological evaluation. "
                                  "Rule out reversible causes (B12 deficiency, thyroid, depression, sleep apnea). "
                                  "Encourage cognitive engagement: puzzles, reading, social activities.", 
                                  styles['ReportBody']))
            areas_for_improvement.append(('Cognitive Function', 'MODERATE',
                'Neuropsychology referral, rule out reversible causes, cognitive engagement'))
        else:
            pillar2_total = safe_float(pillar2, 'pillar2_total')
            pillar2_cat = safe_get(pillar2, 'pillar2_category', '')
            if pillar2_total > 0:
                story.append(Paragraph(f"✓ Cognitive function adequate: {pillar2_total:.1f}/10 ({pillar2_cat})", 
                                      styles['SuccessText']))
            else:
                story.append(Paragraph("Cognitive assessment incomplete.", styles['ReportBody']))
    else:
        story.append(Paragraph("Pillar 2 (Cognitive Function) not assessed.", styles['ReportBody']))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # =========================================================================
    # Summary: Areas for Improvement
    # =========================================================================
    if areas_for_improvement:
        story.append(Paragraph("Summary: Personalized Action Plan", styles['SubHeading']))
        
        # Sort by priority
        priority_order = {'HIGH PRIORITY': 0, 'MODERATE': 1, 'LOW': 2}
        areas_for_improvement.sort(key=lambda x: priority_order.get(x[1], 3))
        
        action_data = [['Priority', 'Area', 'Recommended Action']]
        for area, priority, action in areas_for_improvement:
            action_data.append([priority, area, action])
        
        t = Table(action_data, colWidths=[1.2 * inch, 1.8 * inch, 3 * inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            # Color code priority
            ('TEXTCOLOR', (0, 1), (0, -1), BRAND_DANGER),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("Summary", styles['SubHeading']))
        story.append(Paragraph("✓ <b>No significant deficits identified.</b> Continue current activity levels and "
                              "schedule follow-up assessment in 12 months.", styles['SuccessText']))
    
    story.append(Spacer(1, 0.2 * inch))
    
    # General follow-up recommendations
    story.append(Paragraph("Follow-Up Recommendations", styles['SubHeading']))
    
    recommendations = [
        "• Schedule reassessment in 6-12 months to track progress",
        "• Monitor any high-priority areas more frequently",
        "• Maintain daily physical activity (walking, household tasks)",
        "• Ensure adequate nutrition: protein (1.0-1.2 g/kg), calcium, vitamin D",
        "• Stay socially engaged and mentally active",
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['ReportBody']))
    
    story.append(PageBreak())


def add_page_number(canvas, doc):
    """Add page number to each page."""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.gray)
    canvas.drawRightString(A4[0] - 0.5 * inch, 0.5 * inch, text)
    canvas.drawString(0.5 * inch, 0.5 * inch, "Jiyo100Saal Functional Aging Assessment")
    canvas.restoreState()


def generate_action_plan_page(story: List, styles: Dict, assessment, pillar1, pillar2, pillar3, pillar4, pillar5) -> None:
    """Generate prioritized action plan based on weak pillars."""
    story.append(PageBreak())
    
    # Title
    story.append(Paragraph("YOUR PERSONALIZED ACTION PLAN", styles['SectionHeading']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Collect recommendations based on pillar scores
    critical = []  # Score < 50%
    important = []  # Score 50-70%
    optimize = []  # Score 70-89%
    
    # Pillar 1: Movement & Strength
    if pillar1 and getattr(pillar1, 'pillar1_pct', None):
        pct = float(pillar1.pillar1_pct)
        if pct < 50:
            critical.append("🔴 <b>CRITICAL:</b> Start daily 20-minute walks and basic bodyweight exercises (squats, push-ups)")
        elif pct < 70:
            important.append("🟡 <b>IMPORTANT:</b> Add 2-3 strength training sessions per week, improve cardiovascular fitness")
        elif pct < 90:
            optimize.append("🟢 <b>OPTIMIZE:</b> Increase exercise intensity, add balance and flexibility training")
    
    # Pillar 2: Cognitive Function
    if pillar2 and getattr(pillar2, 'pillar2_pct', None):
        pct = float(pillar2.pillar2_pct)
        if pct < 50:
            critical.append("🔴 <b>CRITICAL:</b> Consult neurologist, begin daily cognitive exercises (puzzles, reading)")
        elif pct < 70:
            important.append("🟡 <b>IMPORTANT:</b> Engage in mentally stimulating activities, learn new skills, improve sleep quality")
        elif pct < 90:
            optimize.append("🟢 <b>OPTIMIZE:</b> Challenge brain with complex tasks, maintain social engagement")
    
    # Pillar 3: Metabolic Health
    if pillar3 and getattr(pillar3, 'pillar3_pct', None):
        pct = float(pillar3.pillar3_pct)
        if pct < 50:
            critical.append("🔴 <b>CRITICAL:</b> Consult endocrinologist, improve diet immediately, test for diabetes/prediabetes")
        elif pct < 70:
            important.append("🟡 <b>IMPORTANT:</b> Adopt Mediterranean diet, reduce sugar intake, increase fiber consumption")
        elif pct < 90:
            optimize.append("🟢 <b>OPTIMIZE:</b> Fine-tune nutrition timing, consider metabolic testing")
    
    # Pillar 4: Vitality & Hormones
    if pillar4 and getattr(pillar4, 'pillar4_pct', None):
        pct = float(pillar4.pillar4_pct)
        if pct < 50:
            critical.append("🔴 <b>CRITICAL:</b> Consult endocrinologist for hormone evaluation, prioritize 7-8 hours sleep")
        elif pct < 70:
            important.append("🟡 <b>IMPORTANT:</b> Optimize sleep schedule, reduce stress, consider vitamin D supplementation")
        elif pct < 90:
            optimize.append("🟢 <b>OPTIMIZE:</b> Fine-tune exercise routine, maintain hormone-healthy lifestyle")
    
    # Pillar 5: Disease Prevention
    if pillar5 and getattr(pillar5, 'pillar5_pct', None):
        pct = float(pillar5.pillar5_pct)
        if pct < 50:
            critical.append("🔴 <b>CRITICAL:</b> Schedule overdue cancer screenings immediately, complete cardiac workup")
        elif pct < 70:
            important.append("🟡 <b>IMPORTANT:</b> Update preventive screenings, address abnormal lab values")
        elif pct < 90:
            optimize.append("🟢 <b>OPTIMIZE:</b> Maintain screening schedule, follow up on minor findings")
    
    # Display recommendations
    if critical:
        story.append(Paragraph("PRIORITY 1: CRITICAL ACTIONS (This Week)", styles['SubHeading']))
        for item in critical:
            story.append(Paragraph(f"• {item}", styles['ReportBody']))
            story.append(Spacer(1, 0.1 * inch))
    
    if important:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("PRIORITY 2: IMPORTANT ACTIONS (This Month)", styles['SubHeading']))
        for item in important:
            story.append(Paragraph(f"• {item}", styles['ReportBody']))
            story.append(Spacer(1, 0.1 * inch))
    
    if optimize:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("PRIORITY 3: OPTIMIZATION (Ongoing)", styles['SubHeading']))
        for item in optimize:
            story.append(Paragraph(f"• {item}", styles['ReportBody']))
            story.append(Spacer(1, 0.1 * inch))
    
    # If all pillars are >90%, show congratulations
    if not critical and not important and not optimize:
        story.append(Paragraph("<b>Congratulations!</b> Your functional health assessment shows excellent results across all pillars.", styles['SuccessText']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("Continue maintaining your current healthy habits and consider these optimization strategies:", styles['ReportBody']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("• Maintain regular physical activity and strength training", styles['ReportBody']))
        story.append(Paragraph("• Continue mental stimulation and social engagement", styles['ReportBody']))
        story.append(Paragraph("• Keep up preventive health screenings", styles['ReportBody']))
        story.append(Paragraph("• Stay engaged with stress management practices", styles['ReportBody']))
    
    # Next steps
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("NEXT STEPS:", styles['SubHeading']))
    story.append(Paragraph("1. Review this plan with your healthcare provider at Gini Advanced Care Hospital", styles['ReportBody']))
    story.append(Paragraph("2. Schedule follow-up functional assessment in 3-6 months to track progress", styles['ReportBody']))
    story.append(Paragraph("3. Consider enrolling in Jiyo100Saal's personalized longevity programs", styles['ReportBody']))
    story.append(Paragraph("4. Contact us for the 100ers program - advanced longevity optimization", styles['ReportBody']))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Contact info
    story.append(Paragraph("<b>Contact Gini Advanced Care Hospital</b>", styles['SubHeading']))
    story.append(Paragraph("Phone: +91-172-XXXXXXX | Email: info@ginihealth.com", styles['ReportBody']))
    story.append(Paragraph("Address: Mohali, Punjab, India", styles['ReportBody']))
    story.append(Paragraph("<i>Your partner in functional aging and longevity</i>", styles['CenterText']))


def generate_assessment_report(assessment) -> BytesIO:
    """
    Generate a complete PDF assessment report.
    
    Args:
        assessment: Assessment model with related data loaded
        
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    
    # Get styles
    styles = get_styles()
    
    # Build story (content)
    story = []
    
    # Get related data
    patient = assessment.patient if assessment else None
    section0 = assessment.section0_results if assessment else None
    section1 = assessment.section1_results if assessment else None
    pillar1 = assessment.pillar1_results if assessment else None
    pillar2 = assessment.pillar2_results if assessment else None
    pillar3 = assessment.pillar3_results if assessment else None
    pillar4 = assessment.pillar4_results if assessment else None
    pillar5 = assessment.pillar5_results if assessment else None
    
    # Generate pages
    generate_cover_page(story, styles, assessment, patient)
    generate_executive_summary(story, styles, assessment, patient, section0, section1, pillar1, pillar2, pillar3, pillar4, pillar5)
    generate_section0_page(story, styles, section0, assessment, patient)
    generate_section1_page(story, styles, section1, patient)
    generate_pillar1_page(story, styles, pillar1, assessment, patient)
    generate_pillar2_page(story, styles, pillar2, assessment, patient)
    generate_pillar3_page(story, styles, pillar3, assessment, patient)
    if pillar4:
        generate_pillar4_page(story, styles, pillar4, assessment, patient)
    if pillar5:
        generate_pillar5_page(story, styles, pillar5, assessment, patient)
    generate_recommendations_page(story, styles, section0, section1, pillar1, pillar2, patient)
    
    # Generate personalized action plan
    generate_action_plan_page(story, styles, assessment, pillar1, pillar2, pillar3, pillar4, pillar5)
    
    # Build PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    buffer.seek(0)
    return buffer
