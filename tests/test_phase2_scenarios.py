"""
Phase 2 Validation Test Script
==============================

Tests Section 0 implementation with 3 test scenarios from the specification:
1. 55M High-Functioning (Rajesh Kumar)
2. 68F Sedentary with risks (Jane Smith)
3. 42M Athletic Runner (Mike Johnson)

Validates:
- Age calculation
- BMI calculation
- BP classification
- Risk modifiers calculation
- Data persistence after save/reload
"""

import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.base import db, Base
from models.patient import Patient
from models.assessment import Assessment
from models.section0 import Section0Results, FamilyHistory


def setup_database():
    """Initialize fresh test database."""
    db.init_app('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(db.engine)
    return db.session()


def create_scenario_1_55m_high_functioning(session):
    """
    Scenario 1: 55-year-old Male, High-Functioning
    
    Profile:
    - Excellent health, minimal medications
    - Parents lived long
    - Never smoked
    - Moderate alcohol
    - Married with children
    """
    print("\n" + "="*70)
    print("SCENARIO 1: 55M HIGH-FUNCTIONING (Rajesh Kumar)")
    print("="*70)
    
    # Create patient
    patient = Patient(
        first_name='Rajesh',
        last_name='Kumar',
        date_of_birth=date(1971, 1, 15),  # Will be 55 on assessment date
        sex='male',
        phone='+91-9876543210',
        email='rajesh.kumar@example.com',
    )
    session.add(patient)
    session.commit()
    
    # Create assessment (date: Feb 1, 2026)
    assessment = Assessment(
        patient_id=patient.id,
        assessment_date=date(2026, 2, 1),
        assessment_type='comprehensive',
        status='in_progress',
        clinician_name='Dr. Sharma',
    )
    session.add(assessment)
    session.commit()
    
    # Verify age at assessment
    age = assessment.age_at_assessment
    print(f"\n✓ Patient Age at Assessment: {age} years (expected: 55)")
    assert age == 55, f"Age should be 55, got {age}"
    
    # Create Section 0 Results
    section0 = Section0Results(
        assessment_id=assessment.id,
        # Anthropometrics - Healthy weight
        height_cm=Decimal('175.0'),
        weight_kg=Decimal('75.0'),
        waist_circumference_cm=Decimal('88.0'),
        hip_circumference_cm=Decimal('98.0'),
        # Vital Signs - Normal
        bp_systolic_1=118,
        bp_diastolic_1=76,
        bp_systolic_2=120,
        bp_diastolic_2=78,
        bp_arm_used='right',
        bp_cuff_size='standard',
        resting_heart_rate=62,
        hr_method='pulse_ox',
        hr_rhythm='regular',
        # Medications - Minimal
        medication_count=1,  # Just vitamins
        medication_categories=['supplements'],
        # Smoking - Never
        smoking_status='never',
        pack_years=None,
        # Alcohol - Light
        alcohol_drinks_per_week=4,
        alcohol_pattern='spread',
        # Social - Married
        relationship_status='married',
        has_children=True,
        children_details='2 adult children (28, 25)',
        living_situation='spouse',
        caregiving_role='none',
        # No injuries
        tbi_history='none',
        fragility_fracture=False,
        # Motivations
        motivations=['children', 'active_retirement', 'fitness'],
        personal_goal='Stay active to play with future grandchildren',
    )
    session.add(section0)
    session.commit()
    
    # Calculate BMI
    section0.calculate_bmi_and_store()
    print(f"\n✓ Height: {section0.height_cm} cm")
    print(f"✓ Weight: {section0.weight_kg} kg")
    print(f"✓ Calculated BMI: {section0.bmi} (expected: ~24.5)")
    print(f"✓ BMI Category: {section0.bmi_category}")
    assert float(section0.bmi) == 24.5, f"BMI should be 24.5, got {section0.bmi}"
    
    # Calculate BP
    section0.calculate_bp_average()
    print(f"\n✓ BP Reading 1: {section0.bp_systolic_1}/{section0.bp_diastolic_1}")
    print(f"✓ BP Reading 2: {section0.bp_systolic_2}/{section0.bp_diastolic_2}")
    print(f"✓ BP Average: {section0.bp_systolic_avg}/{section0.bp_diastolic_avg}")
    print(f"✓ BP Classification: {section0.bp_classification} (expected: Normal)")
    assert section0.bp_classification == 'Normal', f"BP should be Normal, got {section0.bp_classification}"
    
    # Waist risk
    print(f"\n✓ Waist: {section0.waist_circumference_cm} cm")
    print(f"✓ Waist Risk: {section0.waist_risk} (expected: Low for male <90)")
    assert section0.waist_risk == 'Low', f"Waist risk should be Low, got {section0.waist_risk}"
    
    # Create Family History - Parents lived long
    family_history = FamilyHistory(
        section_0_id=section0.id,
        # Father - lived to 85
        father_status='deceased',
        father_age_at_death=85,
        father_cause_of_death='Natural causes',
        father_conditions={'hypertension': True},  # Late onset, not early CVD
        # Mother - still living at 82
        mother_status='living',
        mother_current_age=82,
        mother_conditions={'osteoarthritis': True},
        # Grandparents - good longevity
        grandfather_paternal_age=78,
        grandmother_paternal_age=88,
        grandfather_maternal_age=75,
        grandmother_maternal_age=92,
        exceptional_longevity='one_90_94',
    )
    session.add(family_history)
    session.commit()
    
    # Calculate family history modifiers
    family_history.calculate_longevity_modifier()
    family_history.assess_cvd_family_risk()
    print(f"\n✓ Father: Deceased at {family_history.father_age_at_death}")
    print(f"✓ Mother: Living, age {family_history.mother_current_age}")
    print(f"✓ CVD Family Risk: {family_history.cvd_family_risk}")
    print(f"✓ Longevity Modifier: {family_history.longevity_modifier} years")
    
    # Calculate total Section 0 modifier
    section0.calculate_functional_age_modifier()
    session.commit()
    
    print(f"\n✓ Polypharmacy Level: {section0.polypharmacy_level}")
    print(f"✓ Smoking Status: {section0.smoking_status}")
    print(f"✓ Relationship: {section0.relationship_status}")
    
    print(f"\n{'='*40}")
    print(f"TOTAL FUNCTIONAL AGE MODIFIER: {section0.functional_age_modifier:+d} years")
    print(f"{'='*40}")
    
    # Expected: Married (-1), Never smoked (0), Low meds (0), Good family history (0 or small negative)
    # Total should be around -1 to -2
    
    # Verify data persistence
    session.expire_all()
    reloaded = session.get(Section0Results, section0.id)
    assert reloaded.bmi == section0.bmi, "BMI should persist"
    assert reloaded.bp_classification == section0.bp_classification, "BP classification should persist"
    print("\n✓ Data persists after reload")
    
    return {
        'patient_name': patient.full_name,
        'age': age,
        'sex': patient.sex,
        'bmi': float(section0.bmi),
        'bmi_category': section0.bmi_category,
        'bp_avg': f"{section0.bp_systolic_avg}/{section0.bp_diastolic_avg}",
        'bp_classification': section0.bp_classification,
        'waist_risk': section0.waist_risk,
        'polypharmacy': section0.polypharmacy_level,
        'smoking': section0.smoking_status,
        'longevity_modifier': family_history.longevity_modifier,
        'total_modifier': section0.functional_age_modifier,
    }


def create_scenario_2_68f_sedentary(session):
    """
    Scenario 2: 68-year-old Female, Sedentary with Risk Factors
    
    Profile:
    - Overweight, high BP
    - Multiple medications (polypharmacy)
    - Former smoker
    - History of gestational diabetes
    - Parents died early from CVD
    - Widowed
    """
    print("\n" + "="*70)
    print("SCENARIO 2: 68F SEDENTARY WITH RISKS (Jane Smith)")
    print("="*70)
    
    # Create patient
    patient = Patient(
        first_name='Jane',
        last_name='Smith',
        date_of_birth=date(1958, 2, 2),  # Will be 67 turning 68
        sex='female',
        phone='+91-9123456789',
    )
    session.add(patient)
    session.commit()
    
    # Create assessment
    assessment = Assessment(
        patient_id=patient.id,
        assessment_date=date(2026, 2, 2),  # On her 68th birthday
        assessment_type='comprehensive',
        status='in_progress',
    )
    session.add(assessment)
    session.commit()
    
    age = assessment.age_at_assessment
    print(f"\n✓ Patient Age at Assessment: {age} years (expected: 68)")
    assert age == 68, f"Age should be 68, got {age}"
    
    # Create Section 0 Results - High risk profile
    section0 = Section0Results(
        assessment_id=assessment.id,
        # Anthropometrics - Overweight
        height_cm=Decimal('162.0'),
        weight_kg=Decimal('78.0'),
        waist_circumference_cm=Decimal('95.0'),  # High for female
        hip_circumference_cm=Decimal('105.0'),
        # Vital Signs - Stage 2 Hypertension
        bp_systolic_1=152,
        bp_diastolic_1=94,
        bp_systolic_2=148,
        bp_diastolic_2=92,
        bp_arm_used='left',
        bp_cuff_size='standard',
        resting_heart_rate=78,
        hr_method='bp_monitor',
        hr_rhythm='regular',
        # Medications - Polypharmacy (7 meds)
        medication_count=7,
        medication_categories=['bp_meds', 'cholesterol', 'diabetes_oral', 'thyroid', 'pain_nsaids'],
        # Smoking - Former, quit 8 years ago
        smoking_status='quit_5_15',
        pack_years=Decimal('15.0'),  # 20 cigs/day for 15 years
        quit_date=date(2018, 3, 1),
        # Alcohol - None
        alcohol_drinks_per_week=0,
        alcohol_pattern=None,
        # Social - Widowed
        relationship_status='widowed',
        has_children=True,
        children_details='3 adult children',
        living_situation='alone',
        caregiving_role='none',
        # Pregnancy history
        pregnancy_count=3,
        live_births=3,
        age_first_pregnancy=24,
        gestational_diabetes=True,  # +1 year modifier
        preeclampsia=False,
        pcos=False,
        # Injuries
        tbi_history='none',
        fragility_fracture=True,  # +2 years modifier
        fracture_location='Wrist',
    )
    session.add(section0)
    session.commit()
    
    # Calculate BMI
    section0.calculate_bmi_and_store()
    expected_bmi = 78.0 / (1.62 ** 2)
    print(f"\n✓ Height: {section0.height_cm} cm")
    print(f"✓ Weight: {section0.weight_kg} kg")
    print(f"✓ Calculated BMI: {section0.bmi} (expected: ~{expected_bmi:.1f})")
    print(f"✓ BMI Category: {section0.bmi_category}")
    assert abs(float(section0.bmi) - expected_bmi) < 0.2, f"BMI mismatch"
    
    # Calculate BP
    section0.calculate_bp_average()
    print(f"\n✓ BP Average: {section0.bp_systolic_avg}/{section0.bp_diastolic_avg}")
    print(f"✓ BP Classification: {section0.bp_classification} (expected: Stage 2 Hypertension)")
    assert section0.bp_classification == 'Stage 2 Hypertension', f"BP should be Stage 2 HTN"
    
    # Waist risk
    print(f"\n✓ Waist: {section0.waist_circumference_cm} cm")
    print(f"✓ Waist Risk: {section0.waist_risk} (expected: Substantially Increased for female >88)")
    assert section0.waist_risk == 'Substantially Increased', f"Waist risk should be Substantially Increased"
    
    # Create Family History - Parents died early
    family_history = FamilyHistory(
        section_0_id=section0.id,
        # Father - died at 62 from heart attack
        father_status='deceased',
        father_age_at_death=62,
        father_cause_of_death='Heart attack',
        father_conditions={
            'heart_disease': True,
            'heart_disease_age': 58,  # Early onset CVD
            'diabetes': True,
        },
        # Mother - died at 65 from stroke
        mother_status='deceased',
        mother_age_at_death=65,
        mother_cause_of_death='Stroke',
        mother_conditions={
            'stroke': True,
            'diabetes': True,
            'hypertension': True,
        },
        exceptional_longevity='none',
    )
    session.add(family_history)
    session.commit()
    
    # Calculate family history modifiers
    family_history.calculate_parents_avg_lifespan()
    family_history.calculate_longevity_modifier()
    family_history.assess_cvd_family_risk()
    
    print(f"\n✓ Father: Deceased at {family_history.father_age_at_death} (Heart attack)")
    print(f"✓ Mother: Deceased at {family_history.mother_age_at_death} (Stroke)")
    print(f"✓ Parents Avg Lifespan: {family_history.parents_avg_lifespan}")
    print(f"✓ CVD Family Risk: {family_history.cvd_family_risk} (expected: positive)")
    print(f"✓ Longevity Modifier: {family_history.longevity_modifier} years (expected: +3 to +5)")
    
    # Should be +3 (both 60-69) or +5 if one < 60
    assert family_history.longevity_modifier >= 3, f"Should be +3 or more for parents dying 60-69"
    
    # Calculate total Section 0 modifier
    section0.calculate_functional_age_modifier()
    session.commit()
    
    print(f"\n✓ Polypharmacy Level: {section0.polypharmacy_level} (5-9 meds = +2)")
    print(f"✓ Smoking: {section0.smoking_status} (quit 5-15 yrs = +3)")
    print(f"✓ Gestational Diabetes: {section0.gestational_diabetes} (+1)")
    print(f"✓ Fragility Fracture: {section0.fragility_fracture} (+2)")
    
    print(f"\n{'='*40}")
    print(f"TOTAL FUNCTIONAL AGE MODIFIER: {section0.functional_age_modifier:+d} years")
    print(f"{'='*40}")
    
    # Expected: Polypharmacy (+2) + Quit smoking 5-15 (+3) + Gestational diabetes (+1) 
    # + Fragility fracture (+2) + Parents died early (+3) = +11 or so
    
    return {
        'patient_name': patient.full_name,
        'age': age,
        'sex': patient.sex,
        'bmi': float(section0.bmi),
        'bmi_category': section0.bmi_category,
        'bp_avg': f"{section0.bp_systolic_avg}/{section0.bp_diastolic_avg}",
        'bp_classification': section0.bp_classification,
        'waist_risk': section0.waist_risk,
        'polypharmacy': section0.polypharmacy_level,
        'smoking': section0.smoking_status,
        'longevity_modifier': family_history.longevity_modifier,
        'total_modifier': section0.functional_age_modifier,
    }


def create_scenario_3_42m_athletic(session):
    """
    Scenario 3: 42-year-old Male, Athletic Runner
    
    Profile:
    - Lean, fit, excellent vitals
    - No medications
    - Never smoked
    - Parents alive and healthy
    - Married
    """
    print("\n" + "="*70)
    print("SCENARIO 3: 42M ATHLETIC RUNNER (Mike Johnson)")
    print("="*70)
    
    # Create patient
    patient = Patient(
        first_name='Mike',
        last_name='Johnson',
        date_of_birth=date(1984, 2, 2),
        sex='male',
    )
    session.add(patient)
    session.commit()
    
    # Create assessment
    assessment = Assessment(
        patient_id=patient.id,
        assessment_date=date(2026, 2, 2),  # On his 42nd birthday
        assessment_type='comprehensive',
        status='in_progress',
    )
    session.add(assessment)
    session.commit()
    
    age = assessment.age_at_assessment
    print(f"\n✓ Patient Age at Assessment: {age} years (expected: 42)")
    assert age == 42, f"Age should be 42, got {age}"
    
    # Create Section 0 Results - Athletic profile
    section0 = Section0Results(
        assessment_id=assessment.id,
        # Anthropometrics - Lean
        height_cm=Decimal('180.0'),
        weight_kg=Decimal('72.0'),
        waist_circumference_cm=Decimal('78.0'),  # Very lean
        hip_circumference_cm=Decimal('92.0'),
        # Vital Signs - Athletic (low resting HR)
        bp_systolic_1=112,
        bp_diastolic_1=68,
        bp_systolic_2=110,
        bp_diastolic_2=70,
        bp_arm_used='right',
        bp_cuff_size='standard',
        resting_heart_rate=52,  # Athletic bradycardia
        hr_method='pulse_ox',
        hr_rhythm='regular',
        # Medications - None
        medication_count=0,
        medication_categories=None,
        # Smoking - Never
        smoking_status='never',
        # Alcohol - Minimal
        alcohol_drinks_per_week=2,
        alcohol_pattern='spread',
        # Social - Married
        relationship_status='married',
        has_children=True,
        children_details='2 young children (8, 5)',
        living_situation='spouse',
        caregiving_role='children',
        # No injuries
        tbi_history='none',
        fragility_fracture=False,
        # Motivations - Athletic
        motivations=['fitness', 'children', 'cognitive'],
        personal_goal='Qualify for Boston Marathon, stay active with kids',
    )
    session.add(section0)
    session.commit()
    
    # Calculate BMI
    section0.calculate_bmi_and_store()
    expected_bmi = 72.0 / (1.80 ** 2)
    print(f"\n✓ Height: {section0.height_cm} cm")
    print(f"✓ Weight: {section0.weight_kg} kg")
    print(f"✓ Calculated BMI: {section0.bmi} (expected: ~{expected_bmi:.1f})")
    print(f"✓ BMI Category: {section0.bmi_category} (expected: Normal)")
    assert section0.bmi_category == 'Normal', f"BMI category should be Normal"
    
    # Calculate BP
    section0.calculate_bp_average()
    print(f"\n✓ BP Average: {section0.bp_systolic_avg}/{section0.bp_diastolic_avg}")
    print(f"✓ BP Classification: {section0.bp_classification} (expected: Normal)")
    assert section0.bp_classification == 'Normal', f"BP should be Normal"
    
    # Waist risk
    print(f"\n✓ Waist: {section0.waist_circumference_cm} cm")
    print(f"✓ Waist Risk: {section0.waist_risk} (expected: Low)")
    assert section0.waist_risk == 'Low', f"Waist risk should be Low"
    
    # Athletic heart rate
    print(f"\n✓ Resting HR: {section0.resting_heart_rate} bpm (athletic)")
    
    # Create Family History - Parents healthy and alive
    family_history = FamilyHistory(
        section_0_id=section0.id,
        # Father - alive at 70
        father_status='living',
        father_current_age=70,
        father_conditions={'hypertension': True},  # Controlled
        # Mother - alive at 68
        mother_status='living',
        mother_current_age=68,
        mother_conditions=None,  # Healthy
        # Grandparents - decent longevity
        grandfather_paternal_age=82,
        grandmother_paternal_age=88,
        grandfather_maternal_age=79,
        grandmother_maternal_age=85,
        exceptional_longevity='none',
    )
    session.add(family_history)
    session.commit()
    
    # Calculate family history modifiers
    family_history.calculate_longevity_modifier()
    family_history.assess_cvd_family_risk()
    
    print(f"\n✓ Father: Living, age {family_history.father_current_age}")
    print(f"✓ Mother: Living, age {family_history.mother_current_age}")
    print(f"✓ CVD Family Risk: {family_history.cvd_family_risk}")
    print(f"✓ Longevity Modifier: {family_history.longevity_modifier} years")
    
    # Calculate total Section 0 modifier
    section0.calculate_functional_age_modifier()
    session.commit()
    
    print(f"\n✓ Polypharmacy Level: {section0.polypharmacy_level}")
    print(f"✓ Smoking: {section0.smoking_status}")
    print(f"✓ Relationship: {section0.relationship_status}")
    
    print(f"\n{'='*40}")
    print(f"TOTAL FUNCTIONAL AGE MODIFIER: {section0.functional_age_modifier:+d} years")
    print(f"{'='*40}")
    
    # Expected: Married (-1), everything else neutral = -1
    
    return {
        'patient_name': patient.full_name,
        'age': age,
        'sex': patient.sex,
        'bmi': float(section0.bmi),
        'bmi_category': section0.bmi_category,
        'bp_avg': f"{section0.bp_systolic_avg}/{section0.bp_diastolic_avg}",
        'bp_classification': section0.bp_classification,
        'waist_risk': section0.waist_risk,
        'polypharmacy': section0.polypharmacy_level,
        'smoking': section0.smoking_status,
        'longevity_modifier': family_history.longevity_modifier,
        'total_modifier': section0.functional_age_modifier,
    }


def print_summary(results):
    """Print comparison summary table."""
    print("\n")
    print("="*90)
    print("PHASE 2 VALIDATION SUMMARY")
    print("="*90)
    print(f"\n{'Metric':<25} {'55M High-Func':<20} {'68F Sedentary':<20} {'42M Athletic':<20}")
    print("-"*90)
    
    metrics = [
        ('Age', 'age'),
        ('Sex', 'sex'),
        ('BMI', 'bmi'),
        ('BMI Category', 'bmi_category'),
        ('BP Average', 'bp_avg'),
        ('BP Classification', 'bp_classification'),
        ('Waist Risk', 'waist_risk'),
        ('Polypharmacy', 'polypharmacy'),
        ('Smoking', 'smoking'),
        ('Longevity Modifier', 'longevity_modifier'),
        ('TOTAL MODIFIER', 'total_modifier'),
    ]
    
    for label, key in metrics:
        vals = [str(r.get(key, '-')) for r in results]
        if key == 'total_modifier':
            vals = [f"{r.get(key, 0):+d} years" for r in results]
        elif key == 'longevity_modifier':
            vals = [f"{r.get(key, 0):+d} years" if r.get(key) is not None else '0 years' for r in results]
        print(f"{label:<25} {vals[0]:<20} {vals[1]:<20} {vals[2]:<20}")
    
    print("-"*90)
    
    # Validation checks
    print("\n✅ VALIDATION CHECKS:")
    
    checks = [
        ("Age calculations correct", 
         results[0]['age'] == 55 and results[1]['age'] == 68 and results[2]['age'] == 42),
        ("BMI calculations accurate",
         20 < results[0]['bmi'] < 30 and 25 < results[1]['bmi'] < 35 and 18 < results[2]['bmi'] < 25),
        ("BP classifications correct",
         results[0]['bp_classification'] == 'Normal' and 
         results[1]['bp_classification'] == 'Stage 2 Hypertension' and
         results[2]['bp_classification'] == 'Normal'),
        ("Risk modifiers vary by profile",
         results[0]['total_modifier'] < results[1]['total_modifier'] and
         results[2]['total_modifier'] < results[1]['total_modifier']),
        ("High-risk patient has highest modifier",
         results[1]['total_modifier'] > 5),
        ("Athletic patient has low/negative modifier",
         results[2]['total_modifier'] <= 0),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*90)
    if all_passed:
        print("🎉 ALL VALIDATION CHECKS PASSED! Section 0 is ready for Phase 3.")
    else:
        print("⚠️  SOME CHECKS FAILED. Review the results above.")
    print("="*90)
    
    return all_passed


def main():
    """Run all scenarios and print summary."""
    print("\n" + "#"*90)
    print("#" + " "*30 + "PHASE 2 VALIDATION TEST" + " "*30 + "#")
    print("#" + " "*20 + "Section 0: Baseline Health & Context" + " "*20 + "#")
    print("#"*90)
    
    session = setup_database()
    
    try:
        results = []
        
        # Run all 3 scenarios
        results.append(create_scenario_1_55m_high_functioning(session))
        results.append(create_scenario_2_68f_sedentary(session))
        results.append(create_scenario_3_42m_athletic(session))
        
        # Print summary
        all_passed = print_summary(results)
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()


if __name__ == '__main__':
    exit(main())
