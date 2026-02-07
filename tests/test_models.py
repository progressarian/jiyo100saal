"""
Model Tests
===========

Basic CRUD tests and validation tests for all models.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.base import db, Base
from models.patient import Patient
from models.assessment import Assessment
from models.section0 import Section0Results, FamilyHistory
from models.section1 import Section1Results
from models.pillar1 import Pillar1Results
from models.alerts import ClinicalAlert


# =========================================================================
# FIXTURES
# =========================================================================

@pytest.fixture(scope='function')
def session():
    """Create a fresh database session for each test."""
    db.init_app('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(db.engine)
    
    session = db.session()
    yield session
    
    session.close()
    Base.metadata.drop_all(db.engine)


@pytest.fixture
def sample_patient(session):
    """Create a sample patient for testing."""
    patient = Patient(
        first_name='Rajesh',
        last_name='Kumar',
        date_of_birth=date(1971, 3, 15),  # ~55 years old in 2026
        sex='male',
        phone='+91-9876543210',
        email='rajesh.kumar@example.com',
    )
    session.add(patient)
    session.commit()
    return patient


@pytest.fixture
def sample_assessment(session, sample_patient):
    """Create a sample assessment for testing."""
    assessment = Assessment(
        patient_id=sample_patient.id,
        assessment_date=date(2026, 2, 1),
        assessment_type='comprehensive',
        status='in_progress',
        clinician_name='Dr. Sharma',
    )
    session.add(assessment)
    session.commit()
    return assessment


# =========================================================================
# PATIENT MODEL TESTS
# =========================================================================

class TestPatientModel:
    """Tests for Patient model."""
    
    def test_create_patient(self, session):
        """Test creating a basic patient."""
        patient = Patient(
            first_name='Test',
            last_name='Patient',
            date_of_birth=date(1970, 1, 1),
            sex='male',
        )
        session.add(patient)
        session.commit()
        
        assert patient.id is not None
        assert patient.first_name == 'Test'
        assert patient.full_name == 'Test Patient'
        assert patient.created_at is not None
    
    def test_patient_age_calculation(self, session):
        """Test age calculation from date of birth."""
        patient = Patient(
            first_name='Test',
            last_name='Patient',
            date_of_birth=date(1971, 3, 15),
            sex='male',
        )
        session.add(patient)
        session.commit()
        
        # Age at specific date
        age = patient.age_at_date(date(2026, 2, 1))
        assert age == 54  # Birthday is March 15, so still 54 on Feb 1
        
        age_after_bday = patient.age_at_date(date(2026, 4, 1))
        assert age_after_bday == 55  # After March 15
    
    def test_patient_sex_validation(self, session):
        """Test sex field validation."""
        with pytest.raises(ValueError, match="must be 'male' or 'female'"):
            Patient(
                first_name='Test',
                last_name='Patient',
                date_of_birth=date(1970, 1, 1),
                sex='invalid',
            )
    
    def test_patient_email_validation(self, session):
        """Test email validation."""
        with pytest.raises(ValueError, match="Invalid email"):
            Patient(
                first_name='Test',
                last_name='Patient',
                date_of_birth=date(1970, 1, 1),
                sex='male',
                email='not-an-email',
            )
    
    def test_patient_to_dict(self, sample_patient):
        """Test patient serialization."""
        data = sample_patient.to_dict()
        
        assert data['id'] == sample_patient.id
        assert data['full_name'] == 'Rajesh Kumar'
        assert data['sex'] == 'male'
        assert 'current_age' in data


# =========================================================================
# ASSESSMENT MODEL TESTS
# =========================================================================

class TestAssessmentModel:
    """Tests for Assessment model."""
    
    def test_create_assessment(self, session, sample_patient):
        """Test creating an assessment."""
        assessment = Assessment(
            patient_id=sample_patient.id,
            assessment_date=date(2026, 2, 1),
            assessment_type='comprehensive',
            status='draft',
        )
        session.add(assessment)
        session.commit()
        
        assert assessment.id is not None
        assert assessment.patient == sample_patient
    
    def test_assessment_age_at_assessment(self, sample_assessment):
        """Test age calculation at assessment date."""
        # Patient DOB: 1971-03-15
        # Assessment date: 2026-02-01
        # Age should be 54 (birthday not yet)
        assert sample_assessment.age_at_assessment == 54
    
    def test_assessment_age_group(self, sample_assessment):
        """Test age group determination."""
        # Age 54 = group '50-64'
        assert sample_assessment.get_age_group() == '50-64'
    
    def test_assessment_type_validation(self, session, sample_patient):
        """Test assessment type validation."""
        with pytest.raises(ValueError, match="must be one of"):
            Assessment(
                patient_id=sample_patient.id,
                assessment_date=date(2026, 2, 1),
                assessment_type='invalid_type',
                status='draft',
            )
    
    def test_assessment_status_validation(self, session, sample_patient):
        """Test status validation."""
        with pytest.raises(ValueError, match="must be one of"):
            Assessment(
                patient_id=sample_patient.id,
                assessment_date=date(2026, 2, 1),
                assessment_type='comprehensive',
                status='invalid_status',
            )
    
    def test_assessment_cascade_delete(self, session, sample_patient):
        """Test that deleting patient cascades to assessments."""
        assessment = Assessment(
            patient_id=sample_patient.id,
            assessment_date=date(2026, 2, 1),
            assessment_type='comprehensive',
            status='draft',
        )
        session.add(assessment)
        session.commit()
        assessment_id = assessment.id
        
        session.delete(sample_patient)
        session.commit()
        
        # Assessment should be deleted
        assert session.get(Assessment, assessment_id) is None


# =========================================================================
# SECTION 0 MODEL TESTS
# =========================================================================

class TestSection0Model:
    """Tests for Section0Results model."""
    
    def test_create_section0(self, session, sample_assessment):
        """Test creating Section 0 results."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
            waist_circumference_cm=Decimal('90.0'),
            bp_systolic_1=130,
            bp_diastolic_1=85,
            bp_systolic_2=128,
            bp_diastolic_2=82,
            resting_heart_rate=72,
            medication_count=2,
            smoking_status='never',
            relationship_status='married',
        )
        session.add(section0)
        session.commit()
        
        assert section0.id is not None
        assert section0.assessment == sample_assessment
    
    def test_bmi_calculation(self, session, sample_assessment):
        """Test BMI auto-calculation."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
        )
        session.add(section0)
        session.commit()
        
        # BMI = 75 / (1.75)² = 24.49
        assert section0.calculated_bmi == pytest.approx(Decimal('24.5'), abs=0.1)
        assert section0.bmi_category == 'Overweight'  # 23-25 for Asia-Pacific
    
    def test_bp_average_calculation(self, session, sample_assessment):
        """Test blood pressure average calculation."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
            bp_systolic_1=130,
            bp_diastolic_1=85,
            bp_systolic_2=128,
            bp_diastolic_2=82,
        )
        section0.calculate_bp_average()
        
        assert section0.bp_systolic_avg == 129
        assert section0.bp_diastolic_avg == 83
        assert section0.bp_classification == 'Stage 1 Hypertension'
    
    def test_bp_classification_normal(self, session, sample_assessment):
        """Test normal BP classification."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
            bp_systolic_1=118,
            bp_diastolic_1=78,
        )
        section0.calculate_bp_average()
        
        assert section0.bp_classification == 'Normal'
    
    def test_bp_classification_crisis(self, session, sample_assessment):
        """Test hypertensive crisis classification."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
            bp_systolic_1=185,
            bp_diastolic_1=125,
        )
        section0.calculate_bp_average()
        
        assert section0.bp_classification == 'Hypertensive Crisis'
    
    def test_height_validation(self, session, sample_assessment):
        """Test height validation."""
        with pytest.raises(ValueError, match="Height must be between"):
            Section0Results(
                assessment_id=sample_assessment.id,
                height_cm=Decimal('50.0'),  # Too short
                weight_kg=Decimal('75.0'),
            )
    
    def test_polypharmacy_levels(self, session, sample_assessment):
        """Test polypharmacy level categorization."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
        )
        
        section0.medication_count = 0
        assert section0.polypharmacy_level == 'None'
        
        section0.medication_count = 2
        assert section0.polypharmacy_level == 'Low'
        
        section0.medication_count = 4
        assert section0.polypharmacy_level == 'Moderate'
        
        section0.medication_count = 7
        assert section0.polypharmacy_level == 'Polypharmacy'
        
        section0.medication_count = 12
        assert section0.polypharmacy_level == 'High Polypharmacy'


# =========================================================================
# FAMILY HISTORY MODEL TESTS
# =========================================================================

class TestFamilyHistoryModel:
    """Tests for FamilyHistory model."""
    
    def test_create_family_history(self, session, sample_assessment):
        """Test creating family history."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
        )
        session.add(section0)
        session.commit()
        
        family = FamilyHistory(
            section_0_id=section0.id,
            father_status='deceased',
            father_age_at_death=72,
            mother_status='living',
            mother_current_age=78,
        )
        session.add(family)
        session.commit()
        
        assert family.id is not None
        assert family.section0 == section0
    
    def test_longevity_modifier_both_parents_90plus(self, session, sample_assessment):
        """Test longevity modifier when both parents lived to 90+."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
        )
        session.add(section0)
        session.commit()
        
        family = FamilyHistory(
            section_0_id=section0.id,
            father_status='deceased',
            father_age_at_death=92,
            mother_status='deceased',
            mother_age_at_death=95,
        )
        
        modifier = family.calculate_longevity_modifier()
        assert modifier == -5  # -5 years for both 90+
    
    def test_longevity_modifier_both_parents_died_young(self, session, sample_assessment):
        """Test longevity modifier when both parents died young."""
        section0 = Section0Results(
            assessment_id=sample_assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
        )
        session.add(section0)
        session.commit()
        
        family = FamilyHistory(
            section_0_id=section0.id,
            father_status='deceased',
            father_age_at_death=55,
            mother_status='deceased',
            mother_age_at_death=58,
        )
        
        modifier = family.calculate_longevity_modifier()
        assert modifier == 5  # +5 years for both <60


# =========================================================================
# SECTION 1 MODEL TESTS
# =========================================================================

class TestSection1Model:
    """Tests for Section1Results model."""
    
    def test_create_section1_dexa(self, session, sample_assessment):
        """Test creating Section 1 with DEXA data."""
        section1 = Section1Results(
            assessment_id=sample_assessment.id,
            input_method='dexa',
            dexa_body_fat_pct=Decimal('22.5'),
            dexa_lean_mass_kg=Decimal('58.0'),
            dexa_visceral_fat_area=120,
        )
        session.add(section1)
        session.commit()
        
        assert section1.id is not None
        assert section1.input_method == 'dexa'
    
    def test_body_fat_scoring_male_50(self, session, sample_assessment):
        """Test body fat scoring for male age 50-64."""
        section1 = Section1Results(
            assessment_id=sample_assessment.id,
            input_method='dexa',
            body_fat_pct=Decimal('18.0'),
        )
        
        score, category = section1.score_body_fat(age=55, sex='male')
        
        # Male 50-69: <16% = Excellent, 16-19% = Good
        assert category == 'Good'
        assert score == Decimal('85')
    
    def test_lmi_scoring_male(self, session, sample_assessment):
        """Test LMI scoring."""
        section1 = Section1Results(
            assessment_id=sample_assessment.id,
            input_method='dexa',
            lean_mass_index=Decimal('18.5'),
        )
        
        score, category = section1.score_lmi(sex='male')
        
        # Male: 18-20 = Good
        assert category == 'Good'
        assert score == Decimal('85')
    
    def test_sarcopenia_detection_male(self, session, sample_assessment):
        """Test sarcopenia detection for male."""
        section1 = Section1Results(
            assessment_id=sample_assessment.id,
            input_method='dexa',
            lean_mass_index=Decimal('13.5'),  # Below 14 threshold
        )
        
        result = section1.assess_sarcopenia_risk(sex='male')
        assert result is True
        assert section1.sarcopenia_risk is True


# =========================================================================
# PILLAR 1 MODEL TESTS
# =========================================================================

class TestPillar1Model:
    """Tests for Pillar1Results model."""
    
    def test_create_pillar1(self, session, sample_assessment):
        """Test creating Pillar 1 results."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            chair_stand_reps=23,
            grip_dominant_hand='right',
            grip_right_1=Decimal('45.0'),
            grip_right_2=Decimal('47.0'),
            grip_right_3=Decimal('46.0'),
        )
        session.add(pillar1)
        session.commit()
        
        assert pillar1.id is not None
    
    def test_grip_best_calculation(self, session, sample_assessment):
        """Test grip strength best calculation."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            grip_dominant_hand='right',
            grip_left_1=Decimal('42.0'),
            grip_left_2=Decimal('44.0'),
            grip_left_3=Decimal('43.0'),
            grip_right_1=Decimal('45.0'),
            grip_right_2=Decimal('47.0'),
            grip_right_3=Decimal('46.0'),
        )
        
        pillar1.calculate_grip_best()
        
        assert pillar1.grip_left_best == Decimal('44.0')
        assert pillar1.grip_right_best == Decimal('47.0')
        assert pillar1.grip_dominant_best == Decimal('47.0')  # Right is dominant
    
    def test_gait_speed_calculation(self, session, sample_assessment):
        """Test gait speed calculation."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            gait_trial_1_sec=Decimal('3.2'),
            gait_trial_2_sec=Decimal('2.96'),  # Faster
        )
        
        pillar1.calculate_gait_speed()
        
        assert pillar1.gait_faster_sec == Decimal('2.96')
        # Speed = 4 / 2.96 = 1.35 m/s
        assert pillar1.gait_speed_ms == pytest.approx(Decimal('1.35'), abs=0.01)
    
    def test_single_leg_better_calculation(self, session, sample_assessment):
        """Test single-leg stance best calculation (use BETTER leg)."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            single_leg_left_1=Decimal('20.0'),
            single_leg_left_2=Decimal('22.0'),
            single_leg_right_1=Decimal('25.0'),
            single_leg_right_2=Decimal('28.0'),
        )
        
        pillar1.calculate_single_leg_best()
        
        assert pillar1.single_leg_left_best == Decimal('22.0')
        assert pillar1.single_leg_right_best == Decimal('28.0')
        assert pillar1.single_leg_better_best == Decimal('28.0')  # Right is better
    
    def test_tug_faster_calculation(self, session, sample_assessment):
        """Test TUG faster time calculation."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            tug_trial_1_sec=Decimal('9.5'),
            tug_trial_2_sec=Decimal('9.2'),
        )
        
        pillar1.calculate_tug_faster()
        
        assert pillar1.tug_faster_sec == Decimal('9.2')
    
    def test_vo2_mets_calculation(self, session, sample_assessment):
        """Test METs calculation from VO2 max."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            vo2_max=Decimal('35.0'),
        )
        
        pillar1.calculate_vo2_mets()
        
        # METs = 35 / 3.5 = 10
        assert pillar1.vo2_mets == Decimal('10.0')
    
    def test_pillar1_total_calculation(self, session, sample_assessment):
        """Test total Pillar 1 score calculation."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            chair_stand_score=Decimal('2.7'),
            grip_score=Decimal('2.7'),
            gait_score=Decimal('2.0'),
            balance_total_score=Decimal('2.0'),
            tug_score=Decimal('1.9'),
            vo2_score=Decimal('3.3'),
            flexibility_score=Decimal('1.5'),
            walk_6min_score=Decimal('2.4'),
        )
        
        total = pillar1.calculate_pillar1_total()
        
        # Sum: 2.7 + 2.7 + 2.0 + 2.0 + 1.9 + 3.3 + 1.5 + 2.4 = 18.5
        assert total == Decimal('18.5')
        assert pillar1.pillar1_pct == Decimal('92.5')
        assert pillar1.pillar1_category == 'Excellent'
    
    def test_functional_age_impact(self, session, sample_assessment):
        """Test functional age impact calculation."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            pillar1_pct=Decimal('85.0'),  # Very Good (82.5-92%)
        )
        
        impact = pillar1.calculate_functional_age_impact()
        
        assert impact == -2  # Very Good = -1 to -2
    
    def test_sarcopenia_alert_detection(self, session, sample_assessment):
        """Test sarcopenia alert detection."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            grip_dominant_best=Decimal('25.0'),  # Below 27 kg male threshold
        )
        
        alerts = pillar1.detect_clinical_alerts(age=55, sex='male')
        
        assert pillar1.sarcopenia_flag is True
        assert any(a['code'] == 'SARCOPENIA' for a in alerts)
    
    def test_fall_risk_alert_detection(self, session, sample_assessment):
        """Test high fall risk detection."""
        pillar1 = Pillar1Results(
            assessment_id=sample_assessment.id,
            gait_speed_ms=Decimal('0.7'),  # <0.8
            single_leg_better_best=Decimal('4.0'),  # <5
            tug_faster_sec=Decimal('25.0'),  # >20
        )
        
        alerts = pillar1.detect_clinical_alerts(age=68, sex='female')
        
        assert pillar1.fall_risk_flag == 'very_high'
        assert any(a['code'] == 'FALL_RISK_VERY_HIGH' for a in alerts)


# =========================================================================
# CLINICAL ALERT MODEL TESTS
# =========================================================================

class TestClinicalAlertModel:
    """Tests for ClinicalAlert model."""
    
    def test_create_alert(self, session, sample_assessment):
        """Test creating a clinical alert."""
        alert = ClinicalAlert(
            assessment_id=sample_assessment.id,
            source_section='pillar1',
            alert_code='SARCOPENIA',
            alert_level='high',
            alert_message='Low grip strength indicates possible sarcopenia',
            triggering_values={'grip_kg': 25.0, 'threshold': 27},
        )
        session.add(alert)
        session.commit()
        
        assert alert.id is not None
        assert alert.assessment == sample_assessment
    
    def test_alert_to_dict(self, session, sample_assessment):
        """Test alert serialization."""
        alert = ClinicalAlert(
            assessment_id=sample_assessment.id,
            source_section='pillar1',
            alert_code='SARCOPENIA',
            alert_level='high',
            alert_message='Low grip strength',
            triggering_values={'grip_kg': 25.0},
        )
        session.add(alert)
        session.commit()
        
        data = alert.to_dict()
        
        assert data['alert_code'] == 'SARCOPENIA'
        assert data['alert_level'] == 'high'
        assert data['triggering_values'] == {'grip_kg': 25.0}


# =========================================================================
# INTEGRATION TESTS
# =========================================================================

class TestIntegration:
    """Integration tests for complete assessment flow."""
    
    def test_complete_assessment_flow(self, session):
        """Test creating a complete assessment with all sections."""
        # Create patient
        patient = Patient(
            first_name='Integration',
            last_name='Test',
            date_of_birth=date(1971, 3, 15),
            sex='male',
        )
        session.add(patient)
        session.commit()
        
        # Create assessment
        assessment = Assessment(
            patient_id=patient.id,
            assessment_date=date(2026, 2, 1),
            assessment_type='comprehensive',
            status='in_progress',
        )
        session.add(assessment)
        session.commit()
        
        # Create Section 0
        section0 = Section0Results(
            assessment_id=assessment.id,
            height_cm=Decimal('175.0'),
            weight_kg=Decimal('75.0'),
            waist_circumference_cm=Decimal('90.0'),
            bp_systolic_1=125,
            bp_diastolic_1=80,
            resting_heart_rate=68,
            smoking_status='never',
            relationship_status='married',
        )
        section0.calculate_bmi_and_store()
        section0.calculate_bp_average()
        session.add(section0)
        session.commit()
        
        # Create Section 1
        section1 = Section1Results(
            assessment_id=assessment.id,
            input_method='dexa',
            dexa_body_fat_pct=Decimal('22.0'),
            dexa_lean_mass_kg=Decimal('58.0'),
            body_fat_pct=Decimal('22.0'),
            lean_mass_index=Decimal('18.9'),
        )
        session.add(section1)
        session.commit()
        
        # Create Pillar 1
        pillar1 = Pillar1Results(
            assessment_id=assessment.id,
            chair_stand_reps=23,
            chair_stand_score=Decimal('2.7'),
            grip_dominant_best=Decimal('47.0'),
            grip_score=Decimal('3.0'),
            gait_speed_ms=Decimal('1.35'),
            gait_score=Decimal('2.0'),
            balance_total_score=Decimal('2.0'),
            tug_faster_sec=Decimal('9.2'),
            tug_score=Decimal('1.9'),
            vo2_max=Decimal('42.0'),
            vo2_score=Decimal('3.3'),
            flexibility_best_cm=Decimal('28.0'),
            flexibility_score=Decimal('2.0'),
            walk_6min_total_m=680,
            walk_6min_score=Decimal('2.7'),
        )
        pillar1.calculate_pillar1_total()
        pillar1.calculate_functional_age_impact()
        pillar1.detect_clinical_alerts(age=55, sex='male')
        session.add(pillar1)
        session.commit()
        
        # Update assessment with totals
        assessment.pillar1_total_score = pillar1.pillar1_total
        assessment.status = 'completed'
        assessment.calculate_functional_age()
        session.commit()
        
        # Verify
        assert assessment.is_complete is True
        assert assessment.pillar1_total_score is not None
        assert assessment.functional_age is not None
        assert assessment.section0_results is not None
        assert assessment.section1_results is not None
        assert assessment.pillar1_results is not None
    
    def test_cascade_delete_removes_all_results(self, session):
        """Test that deleting assessment cascades to all result tables."""
        # Create patient with full assessment
        patient = Patient(
            first_name='Cascade',
            last_name='Test',
            date_of_birth=date(1970, 1, 1),
            sex='female',
        )
        session.add(patient)
        session.commit()
        
        assessment = Assessment(
            patient_id=patient.id,
            assessment_date=date(2026, 2, 1),
            assessment_type='comprehensive',
            status='draft',
        )
        session.add(assessment)
        session.commit()
        
        section0 = Section0Results(
            assessment_id=assessment.id,
            height_cm=Decimal('165.0'),
            weight_kg=Decimal('60.0'),
        )
        session.add(section0)
        session.commit()
        
        section1 = Section1Results(
            assessment_id=assessment.id,
            input_method='bia',
        )
        session.add(section1)
        session.commit()
        
        pillar1 = Pillar1Results(
            assessment_id=assessment.id,
        )
        session.add(pillar1)
        session.commit()
        
        # Store IDs
        section0_id = section0.id
        section1_id = section1.id
        pillar1_id = pillar1.id
        
        # Delete assessment
        session.delete(assessment)
        session.commit()
        
        # All results should be gone
        assert session.get(Section0Results, section0_id) is None
        assert session.get(Section1Results, section1_id) is None
        assert session.get(Pillar1Results, pillar1_id) is None


# =========================================================================
# RUN TESTS
# =========================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
