"""
Section 0 Models - Baseline Health & Context
=============================================

Demographics, vitals, medications, family history, and risk modifiers.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Date, Text, Integer, Boolean, ForeignKey,
    CheckConstraint, Numeric, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from models.base import Base

if TYPE_CHECKING:
    from models.assessment import Assessment


class Section0Results(Base):
    """
    Section 0: Baseline Health & Context
    
    Captures demographics, anthropometrics, vitals, medications,
    substance use, social factors, pregnancy history, and injuries.
    """
    
    __tablename__ = 'section_0_results'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key to assessment (1:1)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey('assessments.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # =========================================================================
    # ANTHROPOMETRICS
    # =========================================================================
    
    height_cm: Mapped[Decimal] = mapped_column(
        Numeric(5, 1),
        nullable=False,
    )  # e.g., 175.5
    
    weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(5, 1),
        nullable=False,
    )  # e.g., 75.3
    
    waist_circumference_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    hip_circumference_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    # Calculated BMI (stored for performance)
    bmi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    # =========================================================================
    # VITAL SIGNS
    # =========================================================================
    
    # Blood pressure readings
    bp_systolic_1: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bp_diastolic_1: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bp_systolic_2: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bp_diastolic_2: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Calculated averages
    bp_systolic_avg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bp_diastolic_avg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bp_classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # BP measurement details
    bp_arm_used: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'left' or 'right'
    bp_cuff_size: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'standard', 'large', 'small'
    
    # Heart rate
    resting_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hr_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'pulse_ox', 'bp_monitor', 'manual'
    hr_rhythm: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'regular', 'irregular'
    
    # =========================================================================
    # MEDICATIONS
    # =========================================================================
    
    medication_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0, 1-2, 3-4, 5-9, 10+
    medication_categories: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Array of categories
    
    # =========================================================================
    # SMOKING
    # =========================================================================
    
    smoking_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'never', 'quit_15plus', 'quit_5_15', 'quit_under_5', 'current'
    
    pack_years: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    quit_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # =========================================================================
    # ALCOHOL
    # =========================================================================
    
    alcohol_drinks_per_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alcohol_pattern: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'spread', 'weekend', 'binge'
    
    # =========================================================================
    # FAMILY & SOCIAL
    # =========================================================================
    
    relationship_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'married', 'single', 'divorced', 'widowed'
    
    has_children: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    children_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    living_situation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    caregiving_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # =========================================================================
    # PREGNANCY HISTORY (females only)
    # =========================================================================
    
    pregnancy_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    live_births: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    age_first_pregnancy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gestational_diabetes: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    preeclampsia: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    pcos: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # =========================================================================
    # INJURIES
    # =========================================================================
    
    tbi_history: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'none', 'single', 'multiple', 'repeated'
    
    fragility_fracture: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fracture_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # =========================================================================
    # MOTIVATIONS (optional)
    # =========================================================================
    
    motivations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    personal_goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # =========================================================================
    # CALCULATED RISK MODIFIERS
    # =========================================================================
    
    functional_age_modifier: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # Total +/- years from all Section 0 factors
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="section0_results",
    )
    
    family_history: Mapped[Optional["FamilyHistory"]] = relationship(
        "FamilyHistory",
        back_populates="section0",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Section0Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"bmi={self.bmi}, bp={self.bp_systolic_avg}/{self.bp_diastolic_avg})>"
        )
    
    # =========================================================================
    # CALCULATED PROPERTIES
    # =========================================================================
    
    @property
    def calculated_bmi(self) -> Optional[Decimal]:
        """
        Calculate BMI from height and weight.
        
        Formula: BMI = weight (kg) / height (m)²
        """
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            bmi = float(self.weight_kg) / (height_m ** 2)
            return Decimal(str(round(bmi, 1)))
        return None
    
    @property
    def bmi_category(self) -> Optional[str]:
        """
        BMI category using Asia-Pacific cutoffs.
        
        Returns category: Underweight, Normal, Overweight, Obese I/II/III
        """
        bmi = self.bmi or self.calculated_bmi
        if bmi is None:
            return None
        
        bmi_float = float(bmi)
        
        if bmi_float < 18.5:
            return 'Underweight'
        elif bmi_float < 23.0:
            return 'Normal'
        elif bmi_float < 25.0:
            return 'Overweight'
        elif bmi_float < 30.0:
            return 'Obese Class I'
        elif bmi_float < 35.0:
            return 'Obese Class II'
        else:
            return 'Obese Class III'
    
    @property
    def waist_risk(self) -> Optional[str]:
        """
        Waist circumference risk category.
        
        Uses sex-specific thresholds.
        """
        if not self.waist_circumference_cm:
            return None
        
        waist = float(self.waist_circumference_cm)
        sex = self.assessment.sex if self.assessment else None
        
        if sex == 'male':
            if waist < 90:
                return 'Low'
            elif waist <= 102:
                return 'Increased'
            else:
                return 'Substantially Increased'
        elif sex == 'female':
            if waist < 80:
                return 'Low'
            elif waist <= 88:
                return 'Increased'
            else:
                return 'Substantially Increased'
        
        return None
    
    @property
    def waist_hip_ratio(self) -> Optional[Decimal]:
        """Calculate waist-to-hip ratio."""
        if self.waist_circumference_cm and self.hip_circumference_cm:
            ratio = float(self.waist_circumference_cm) / float(self.hip_circumference_cm)
            return Decimal(str(round(ratio, 2)))
        return None
    
    @property
    def polypharmacy_level(self) -> str:
        """
        Categorize medication count.
        
        Returns: 'None', 'Low', 'Moderate', 'Polypharmacy', 'High Polypharmacy'
        """
        count = self.medication_count or 0
        
        if count == 0:
            return 'None'
        elif count <= 2:
            return 'Low'
        elif count <= 4:
            return 'Moderate'
        elif count <= 9:
            return 'Polypharmacy'
        else:
            return 'High Polypharmacy'
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    @validates('height_cm')
    def validate_height(self, key: str, value: Decimal) -> Decimal:
        """Validate height is reasonable (100-250 cm)."""
        if value is not None:
            height = float(value)
            if not (100 <= height <= 250):
                raise ValueError(f"Height must be between 100-250 cm, got {height}")
        return value
    
    @validates('weight_kg')
    def validate_weight(self, key: str, value: Decimal) -> Decimal:
        """Validate weight is reasonable (30-300 kg)."""
        if value is not None:
            weight = float(value)
            if not (30 <= weight <= 300):
                raise ValueError(f"Weight must be between 30-300 kg, got {weight}")
        return value
    
    @validates('bp_systolic_1', 'bp_systolic_2', 'bp_systolic_avg')
    def validate_systolic(self, key: str, value: Optional[int]) -> Optional[int]:
        """Validate systolic BP (60-250 mmHg)."""
        if value is not None and not (60 <= value <= 250):
            raise ValueError(f"Systolic BP must be between 60-250, got {value}")
        return value
    
    @validates('bp_diastolic_1', 'bp_diastolic_2', 'bp_diastolic_avg')
    def validate_diastolic(self, key: str, value: Optional[int]) -> Optional[int]:
        """Validate diastolic BP (40-150 mmHg)."""
        if value is not None and not (40 <= value <= 150):
            raise ValueError(f"Diastolic BP must be between 40-150, got {value}")
        return value
    
    @validates('resting_heart_rate')
    def validate_heart_rate(self, key: str, value: Optional[int]) -> Optional[int]:
        """Validate resting HR (30-200 bpm)."""
        if value is not None and not (30 <= value <= 200):
            raise ValueError(f"Heart rate must be between 30-200, got {value}")
        return value
    
    # =========================================================================
    # METHODS
    # =========================================================================
    
    def calculate_bp_average(self) -> None:
        """Calculate average blood pressure from two readings."""
        if self.bp_systolic_1 and self.bp_systolic_2:
            self.bp_systolic_avg = (self.bp_systolic_1 + self.bp_systolic_2) // 2
        elif self.bp_systolic_1:
            self.bp_systolic_avg = self.bp_systolic_1
        
        if self.bp_diastolic_1 and self.bp_diastolic_2:
            self.bp_diastolic_avg = (self.bp_diastolic_1 + self.bp_diastolic_2) // 2
        elif self.bp_diastolic_1:
            self.bp_diastolic_avg = self.bp_diastolic_1
        
        self.bp_classification = self.classify_blood_pressure()
    
    def classify_blood_pressure(self) -> Optional[str]:
        """
        Classify blood pressure per 2017 ACC/AHA guidelines.
        
        Returns: 'Normal', 'Elevated', 'Stage 1 Hypertension', 
                 'Stage 2 Hypertension', 'Hypertensive Crisis'
        """
        sys = self.bp_systolic_avg
        dia = self.bp_diastolic_avg
        
        if sys is None or dia is None:
            return None
        
        if sys > 180 or dia > 120:
            return 'Hypertensive Crisis'
        elif sys >= 140 or dia >= 90:
            return 'Stage 2 Hypertension'
        elif sys >= 130 or dia >= 80:
            return 'Stage 1 Hypertension'
        elif sys >= 120 and dia < 80:
            return 'Elevated'
        else:
            return 'Normal'
    
    def calculate_bmi_and_store(self) -> None:
        """Calculate and store BMI."""
        self.bmi = self.calculated_bmi
    
    def calculate_functional_age_modifier(self) -> int:
        """
        Calculate total functional age modifier from Section 0 factors.
        
        Positive = adds years (worse)
        Negative = subtracts years (better)
        """
        modifier = 0
        
        # Medication count impact
        med_modifiers = {
            'None': 0,
            'Low': 0,
            'Moderate': 1,
            'Polypharmacy': 2,
            'High Polypharmacy': 3,
        }
        modifier += med_modifiers.get(self.polypharmacy_level, 0)
        
        # Smoking impact
        smoking_modifiers = {
            'never': 0,
            'quit_15plus': 1,
            'quit_5_15': 3,
            'quit_under_5': 5,
            'current': 8,  # Average of 7-10
        }
        if self.smoking_status:
            modifier += smoking_modifiers.get(self.smoking_status, 0)
        
        # Alcohol impact
        if self.alcohol_drinks_per_week:
            sex = self.assessment.sex if self.assessment else 'male'
            heavy_threshold = 15 if sex == 'male' else 11
            
            if self.alcohol_drinks_per_week >= heavy_threshold:
                modifier += 4  # Average of 3-5
            
            if self.alcohol_pattern == 'binge':
                modifier += 5  # Average of 5-7, but don't double-count
        
        # Relationship status
        if self.relationship_status == 'married':
            modifier -= 1
        
        # Pregnancy complications (females)
        if self.gestational_diabetes:
            modifier += 1
        if self.preeclampsia:
            modifier += 2
        
        # TBI history
        tbi_modifiers = {
            'none': 0,
            'single': 0,
            'multiple': 3,
            'repeated': 3,
        }
        if self.tbi_history:
            modifier += tbi_modifiers.get(self.tbi_history, 0)
        
        # Fragility fracture
        if self.fragility_fracture:
            modifier += 2
        
        # Family history modifier (from linked FamilyHistory)
        if self.family_history:
            modifier += self.family_history.longevity_modifier or 0
        
        self.functional_age_modifier = modifier
        return modifier
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'height_cm': float(self.height_cm) if self.height_cm else None,
            'weight_kg': float(self.weight_kg) if self.weight_kg else None,
            'bmi': float(self.bmi) if self.bmi else None,
            'bmi_category': self.bmi_category,
            'waist_circumference_cm': float(self.waist_circumference_cm) if self.waist_circumference_cm else None,
            'waist_risk': self.waist_risk,
            'waist_hip_ratio': float(self.waist_hip_ratio) if self.waist_hip_ratio else None,
            'bp_systolic_avg': self.bp_systolic_avg,
            'bp_diastolic_avg': self.bp_diastolic_avg,
            'bp_classification': self.bp_classification,
            'resting_heart_rate': self.resting_heart_rate,
            'medication_count': self.medication_count,
            'polypharmacy_level': self.polypharmacy_level,
            'smoking_status': self.smoking_status,
            'pack_years': float(self.pack_years) if self.pack_years else None,
            'alcohol_drinks_per_week': self.alcohol_drinks_per_week,
            'functional_age_modifier': self.functional_age_modifier,
        }


class FamilyHistory(Base):
    """
    Family Health History
    
    Parents' health status, conditions, and longevity data.
    Separate table for cleaner data organization.
    """
    
    __tablename__ = 'family_history'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key to Section 0 (1:1)
    section_0_id: Mapped[int] = mapped_column(
        ForeignKey('section_0_results.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # =========================================================================
    # FATHER
    # =========================================================================
    
    father_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'living', 'deceased', 'unknown'
    
    father_current_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    father_age_at_death: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    father_cause_of_death: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    father_conditions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # =========================================================================
    # MOTHER
    # =========================================================================
    
    mother_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'living', 'deceased', 'unknown'
    
    mother_current_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mother_age_at_death: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mother_cause_of_death: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mother_conditions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # =========================================================================
    # GRANDPARENTS (optional)
    # =========================================================================
    
    grandfather_paternal_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grandmother_paternal_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grandfather_maternal_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grandmother_maternal_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    exceptional_longevity: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )  # 'none', 'one_90_94', 'one_95plus', 'multiple_95plus', 'unknown'
    
    # =========================================================================
    # CALCULATED FIELDS
    # =========================================================================
    
    parents_avg_lifespan: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    cvd_family_risk: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'negative', 'positive_1', 'positive_2plus'
    
    diabetes_family_risk: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'none', 'second_degree', 'one_parent', 'both_parents'
    
    dementia_family_risk: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Additional parent conditions (for easier querying and reporting)
    parent_lung_disease: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    parent_cancer: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    parent_cancer_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    longevity_modifier: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # +/- years based on family longevity
    
    # =========================================================================
    # RELATIONSHIP
    # =========================================================================
    
    section0: Mapped["Section0Results"] = relationship(
        "Section0Results",
        back_populates="family_history",
    )
    
    def __repr__(self) -> str:
        return (
            f"<FamilyHistory(id={self.id}, section_0_id={self.section_0_id}, "
            f"longevity_modifier={self.longevity_modifier})>"
        )
    
    # =========================================================================
    # METHODS
    # =========================================================================
    
    def calculate_parents_avg_lifespan(self) -> Optional[Decimal]:
        """
        Calculate average lifespan of parents if both deceased.
        """
        if (self.father_status == 'deceased' and self.father_age_at_death and
            self.mother_status == 'deceased' and self.mother_age_at_death):
            avg = (self.father_age_at_death + self.mother_age_at_death) / 2
            self.parents_avg_lifespan = Decimal(str(round(avg, 1)))
            return self.parents_avg_lifespan
        return None
    
    def calculate_longevity_modifier(self) -> int:
        """
        Calculate functional age modifier based on parents' longevity.
        
        Per spec:
        - Both parents 90+: -5 years
        - Both parents 80-89: -2 years
        - Both parents 70-79: 0 years
        - Both parents 60-69: +3 years
        - Both parents <60: +5 years
        - Both alive at 85+: -3 years
        - Both alive at 90+: -5 years
        """
        modifier = 0
        
        # Check if both parents still living at advanced age
        if self.father_status == 'living' and self.mother_status == 'living':
            if self.father_current_age and self.mother_current_age:
                if self.father_current_age >= 90 and self.mother_current_age >= 90:
                    modifier = -5
                elif self.father_current_age >= 85 and self.mother_current_age >= 85:
                    modifier = -3
        
        # Check if both deceased
        elif self.father_status == 'deceased' and self.mother_status == 'deceased':
            if self.father_age_at_death and self.mother_age_at_death:
                father_age = self.father_age_at_death
                mother_age = self.mother_age_at_death
                
                if father_age >= 90 and mother_age >= 90:
                    modifier = -5
                elif father_age >= 80 and mother_age >= 80:
                    modifier = -2
                elif father_age >= 70 and mother_age >= 70:
                    modifier = 0
                elif father_age >= 60 and mother_age >= 60:
                    modifier = 3
                else:  # At least one < 60
                    if father_age < 60 and mother_age < 60:
                        modifier = 5
                    else:
                        modifier = 3  # One < 60, one >= 60
        
        self.longevity_modifier = modifier
        return modifier
    
    def assess_cvd_family_risk(self) -> str:
        """
        Assess CVD family risk based on early-onset disease.
        
        Positive if:
        - Father/brother MI <55
        - Mother/sister MI <65
        """
        early_cvd_count = 0
        
        # Check father
        if self.father_conditions:
            father_cvd_age = self.father_conditions.get('heart_disease_age')
            if father_cvd_age and father_cvd_age < 55:
                early_cvd_count += 1
        
        # Check mother
        if self.mother_conditions:
            mother_cvd_age = self.mother_conditions.get('heart_disease_age')
            if mother_cvd_age and mother_cvd_age < 65:
                early_cvd_count += 1
        
        if early_cvd_count >= 2:
            self.cvd_family_risk = 'positive_2plus'
        elif early_cvd_count == 1:
            self.cvd_family_risk = 'positive_1'
        else:
            self.cvd_family_risk = 'negative'
        
        return self.cvd_family_risk
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'section_0_id': self.section_0_id,
            'father_status': self.father_status,
            'father_age_at_death': self.father_age_at_death,
            'father_current_age': self.father_current_age,
            'mother_status': self.mother_status,
            'mother_age_at_death': self.mother_age_at_death,
            'mother_current_age': self.mother_current_age,
            'parents_avg_lifespan': float(self.parents_avg_lifespan) if self.parents_avg_lifespan else None,
            'cvd_family_risk': self.cvd_family_risk,
            'diabetes_family_risk': self.diabetes_family_risk,
            'longevity_modifier': self.longevity_modifier,
        }
