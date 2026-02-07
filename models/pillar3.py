"""
Pillar 3 Model - Metabolic & Digestive Health
==============================================

5 test components with scoring and clinical alerts.
Maximum 20 points total.
"""

from decimal import Decimal
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import (
    String, Integer, Boolean, ForeignKey,
    CheckConstraint, Numeric, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from models.base import Base

if TYPE_CHECKING:
    from models.assessment import Assessment


class Pillar3Results(Base):
    """
    Pillar 3: Metabolic & Digestive Health Assessment
    
    5 Test Components (20 points total):
    1. Glucose Metabolism & Energy (5 pts)
       - Blood Glucose Control (3 pts)
       - Functional Energy (2 pts)
    2. Digestive Function (6 pts)
       - Bowel frequency (2 pts)
       - Stool consistency (1 pt)
       - Acid reflux (2 pts)
       - Post-meal comfort (1 pt)
    3. Gut Symptoms (4 pts)
       - Bloating/gas (2 pts)
       - Abdominal pain (1 pt)
       - Food intolerances (1 pt)
    4. Liver Function (3 pts)
       - ALT + AST enzymes (3 pts)
    5. Metabolic Inflammation (2 pts)
       - hs-CRP (2 pts)
    
    Note: All scoring functions enforce maximum caps to prevent scores exceeding limits.
    """
    
    __tablename__ = 'pillar_3_results'
    
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
    # TEST 1: GLUCOSE METABOLISM & ENERGY (5 points)
    # =========================================================================
    
    # Part A: Blood Glucose Control (3 pts) - Support both exact values and categories
    glucose_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    fasting_glucose: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL
    hba1c: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)  # %
    glucose_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # If using category mode
    glucose_blood_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    glucose_blood_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Part B: Functional Energy (2 pts)
    post_meal_feeling: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # energized/comfortable/tired/coma
    fasting_tolerance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # fine/hungry/difficult/cannot
    glucose_functional_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # Total Glucose
    glucose_total_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 2: DIGESTIVE FUNCTION (6 points)
    # =========================================================================
    
    bowel_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # 1-2daily/oncedaily/3-4daily/2-3days/5plus/weekly
    bowel_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    stool_consistency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # normal/slightly/abnormal
    stool_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    reflux_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # never/occasional/frequent/daily
    reflux_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    meal_comfort: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # comfortable/mild/bloated/significant
    meal_comfort_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    digestive_total_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 3: GUT SYMPTOMS (4 points)
    # =========================================================================
    
    bloating_frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # rarely/occasional/frequent/daily
    bloating_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    abdominal_pain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # no/rarely/occasional/frequent
    pain_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    food_intolerances: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # none/few/several/many
    intolerance_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    gut_symptoms_total_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 4: LIVER FUNCTION (3 points)
    # =========================================================================
    
    liver_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    alt_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # U/L
    ast_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # U/L
    liver_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # If using category mode
    liver_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    liver_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 5: METABOLIC INFLAMMATION (2 points)
    # =========================================================================
    
    crp_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    hs_crp: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # mg/L
    crp_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # If using category mode
    crp_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    crp_risk_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TOTALS & CLINICAL FLAGS
    # =========================================================================
    
    pillar3_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    pillar3_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    pillar3_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    functional_age_modifier: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    clinical_alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Individual clinical flags
    diabetes_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    prediabetes_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    liver_concern_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    inflammation_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    digestive_disorder_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="pillar3_results",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Pillar3Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"total={self.pillar3_total}/20, category={self.pillar3_category})>"
        )
    
    # =========================================================================
    # CALCULATED VALUES
    # =========================================================================
    
    def calculate_glucose_total(self) -> None:
        """Calculate total glucose score (blood + functional)."""
        blood = float(self.glucose_blood_points) if self.glucose_blood_points else 0
        functional = float(self.glucose_functional_points) if self.glucose_functional_points else 0
        self.glucose_total_points = Decimal(str(round(blood + functional, 2)))
    
    def calculate_digestive_total(self) -> None:
        """Calculate total digestive function score."""
        scores = [
            self.bowel_points,
            self.stool_points,
            self.reflux_points,
            self.meal_comfort_points,
        ]
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        self.digestive_total_points = Decimal(str(round(total, 2)))
    
    def calculate_gut_symptoms_total(self) -> None:
        """Calculate total gut symptoms score."""
        scores = [
            self.bloating_points,
            self.pain_points,
            self.intolerance_points,
        ]
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        self.gut_symptoms_total_points = Decimal(str(round(total, 2)))
    
    # =========================================================================
    # TOTAL SCORE CALCULATION
    # =========================================================================
    
    def calculate_pillar3_total(self) -> Decimal:
        """
        Calculate total Pillar 3 score (sum of all 5 test components).
        
        Max 20 points.
        """
        scores = [
            self.glucose_total_points,
            self.digestive_total_points,
            self.gut_symptoms_total_points,
            self.liver_points,
            self.crp_points,
        ]
        
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        
        self.pillar3_total = Decimal(str(round(total, 2)))
        self.pillar3_pct = Decimal(str(round((total / 20) * 100, 2)))
        self.pillar3_category = self._categorize_total(total)
        
        return self.pillar3_total
    
    def _categorize_total(self, total: float) -> str:
        """Categorize total score (out of 20)."""
        pct = (total / 20) * 100
        
        if pct >= 90:
            return 'Excellent'
        elif pct >= 80:
            return 'Good'
        elif pct >= 70:
            return 'Average'
        elif pct >= 60:
            return 'Below Average'
        elif pct >= 50:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def calculate_functional_age_modifier(self) -> Decimal:
        """
        Calculate metabolic/digestive impact on functional age.
        
        Score ranges:
        - 18-20 (90-100%): -2 years
        - 16-17.9 (80-89%): -1 year
        - 14-15.9 (70-79%): 0 years
        - 12-13.9 (60-69%): +1 year
        - 10-11.9 (50-59%): +2 years
        - <10 (<50%): +3 years
        """
        if self.pillar3_total is None:
            return Decimal('0')
        
        total = float(self.pillar3_total)
        
        if total >= 18:
            modifier = -2.0
        elif total >= 16:
            modifier = -1.0
        elif total >= 14:
            modifier = 0.0
        elif total >= 12:
            modifier = 1.0
        elif total >= 10:
            modifier = 2.0
        else:
            modifier = 3.0
        
        self.functional_age_modifier = Decimal(str(modifier))
        return self.functional_age_modifier
    
    # =========================================================================
    # CLINICAL ALERT DETECTION
    # =========================================================================
    
    def detect_clinical_alerts(self) -> List[dict]:
        """Detect all clinical alerts based on test results."""
        alerts = []
        
        # Diabetes/Prediabetes
        if self.glucose_blood_points is not None:
            blood_score = float(self.glucose_blood_points)
            if blood_score <= 1.5 and self.hba1c and float(self.hba1c) >= 6.1:
                self.prediabetes_flag = True
                alerts.append({
                    'code': 'PREDIABETES',
                    'level': 'high',
                    'message': 'Pre-diabetes detected. Recommend lifestyle intervention.',
                })
            
            if blood_score <= 1.0:
                self.diabetes_flag = True
                if self.hba1c and float(self.hba1c) > 7.5:
                    alerts.append({
                        'code': 'DIABETES_POOR_CONTROL',
                        'level': 'urgent',
                        'message': 'URGENT: Poor diabetes control. Immediate medical attention needed.',
                    })
                else:
                    alerts.append({
                        'code': 'DIABETES',
                        'level': 'high',
                        'message': 'Diabetes detected. Recommend comprehensive diabetes management.',
                    })
        
        # Liver concerns
        if self.liver_points is not None and float(self.liver_points) <= 1.5:
            self.liver_concern_flag = True
            if float(self.liver_points) == 0:
                alerts.append({
                    'code': 'LIVER_SEVERE',
                    'level': 'urgent',
                    'message': 'URGENT: Severely elevated liver enzymes. Immediate evaluation needed.',
                })
            else:
                alerts.append({
                    'code': 'LIVER_ELEVATED',
                    'level': 'high',
                    'message': 'Elevated liver enzymes. Recommend liver function panel and ultrasound.',
                })
        
        # Inflammation
        if self.crp_points is not None and float(self.crp_points) <= 0.5:
            self.inflammation_flag = True
            if self.hs_crp and float(self.hs_crp) > 10:
                alerts.append({
                    'code': 'CRP_VERY_HIGH',
                    'level': 'urgent',
                    'message': 'URGENT: Very high CRP. Rule out infection or acute inflammation.',
                })
            else:
                alerts.append({
                    'code': 'INFLAMMATION',
                    'level': 'high',
                    'message': 'Elevated inflammation marker. Cardiovascular risk increased.',
                })
        
        # Digestive disorders
        symptoms = []
        if self.bloating_points is not None and float(self.bloating_points) == 0:
            symptoms.append('daily bloating')
        if self.pain_points is not None and float(self.pain_points) == 0:
            symptoms.append('frequent abdominal pain')
        if self.bowel_points is not None and float(self.bowel_points) <= 0.5:
            symptoms.append('abnormal bowel frequency')
        if self.reflux_points is not None and float(self.reflux_points) == 0:
            symptoms.append('daily reflux')
        
        if symptoms:
            self.digestive_disorder_flag = True
            alerts.append({
                'code': 'DIGESTIVE_DISORDER',
                'level': 'high',
                'message': f"Digestive symptoms: {', '.join(symptoms)}. Consider GI evaluation.",
            })
        
        self.clinical_alerts = alerts
        return alerts
    
    # =========================================================================
    # CONVERSION
    # =========================================================================
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            # Glucose
            'glucose_input_mode': self.glucose_input_mode,
            'fasting_glucose': float(self.fasting_glucose) if self.fasting_glucose else None,
            'hba1c': float(self.hba1c) if self.hba1c else None,
            'glucose_category': self.glucose_category,
            'glucose_blood_points': float(self.glucose_blood_points) if self.glucose_blood_points else None,
            'glucose_blood_category': self.glucose_blood_category,
            'post_meal_feeling': self.post_meal_feeling,
            'fasting_tolerance': self.fasting_tolerance,
            'glucose_functional_points': float(self.glucose_functional_points) if self.glucose_functional_points else None,
            'glucose_total_points': float(self.glucose_total_points) if self.glucose_total_points else None,
            # Digestive
            'bowel_frequency': self.bowel_frequency,
            'bowel_points': float(self.bowel_points) if self.bowel_points else None,
            'stool_consistency': self.stool_consistency,
            'stool_points': float(self.stool_points) if self.stool_points else None,
            'reflux_frequency': self.reflux_frequency,
            'reflux_points': float(self.reflux_points) if self.reflux_points else None,
            'meal_comfort': self.meal_comfort,
            'meal_comfort_points': float(self.meal_comfort_points) if self.meal_comfort_points else None,
            'digestive_total_points': float(self.digestive_total_points) if self.digestive_total_points else None,
            # Gut symptoms
            'bloating_frequency': self.bloating_frequency,
            'bloating_points': float(self.bloating_points) if self.bloating_points else None,
            'abdominal_pain': self.abdominal_pain,
            'pain_points': float(self.pain_points) if self.pain_points else None,
            'food_intolerances': self.food_intolerances,
            'intolerance_points': float(self.intolerance_points) if self.intolerance_points else None,
            'gut_symptoms_total_points': float(self.gut_symptoms_total_points) if self.gut_symptoms_total_points else None,
            # Liver
            'liver_input_mode': self.liver_input_mode,
            'alt_value': float(self.alt_value) if self.alt_value else None,
            'ast_value': float(self.ast_value) if self.ast_value else None,
            'liver_category_input': self.liver_category_input,
            'liver_points': float(self.liver_points) if self.liver_points else None,
            'liver_category': self.liver_category,
            # Inflammation
            'crp_input_mode': self.crp_input_mode,
            'hs_crp': float(self.hs_crp) if self.hs_crp else None,
            'crp_category_input': self.crp_category_input,
            'crp_points': float(self.crp_points) if self.crp_points else None,
            'crp_risk_level': self.crp_risk_level,
            # Totals
            'pillar3_total': float(self.pillar3_total) if self.pillar3_total else None,
            'pillar3_pct': float(self.pillar3_pct) if self.pillar3_pct else None,
            'pillar3_category': self.pillar3_category,
            'functional_age_modifier': float(self.functional_age_modifier) if self.functional_age_modifier else None,
            # Alerts
            'clinical_alerts': self.clinical_alerts,
            'diabetes_flag': self.diabetes_flag,
            'prediabetes_flag': self.prediabetes_flag,
            'liver_concern_flag': self.liver_concern_flag,
            'inflammation_flag': self.inflammation_flag,
            'digestive_disorder_flag': self.digestive_disorder_flag,
        }
