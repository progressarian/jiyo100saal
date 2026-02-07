"""
Pillar 4 Model - Vitality & Hormones
=====================================

9 test components with scoring and clinical alerts.
Maximum 20 points total.
Sex-specific scoring for hormones and hemoglobin.
"""

from decimal import Decimal
from typing import Optional, TYPE_CHECKING, List

from sqlalchemy import (
    String, Integer, Boolean, ForeignKey,
    CheckConstraint, Numeric, JSON, DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from datetime import datetime

from models.base import Base

if TYPE_CHECKING:
    from models.assessment import Assessment


class Pillar4Results(Base):
    """
    Pillar 4: Vitality & Hormones Assessment
    
    9 Test Components (20 points total):
    1. Thyroid Function (4 pts)
    2. Sex Hormones (4 pts) - Sex-specific
    3. Sexual Health (1 pt) - Sex-specific
    4. Vitamin D (2 pts)
    5. Hemoglobin & Iron (2 pts) - Sex-adjusted
    6. Exercise Habits (2 pts)
    7. Sleep Duration & Quality (3 pts)
    8. Skin & Hair Health (1 pt)
    9. Stress & Overwhelm (1 pt)
    
    Note: Sex-specific fields for hormones and sexual health.
    Age-adjusted testosterone scoring for males.
    """
    
    __tablename__ = 'pillar_4_results'
    
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
    # TEST 1: THYROID FUNCTION (4 points)
    # =========================================================================
    
    thyroid_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    tsh: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # mIU/L
    free_t4: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)  # ng/dL
    free_t3: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)  # pg/mL
    thyroid_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # If using category mode
    t3_t4_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # optimal/suboptimal/notTested
    thyroid_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    thyroid_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 2: SEX HORMONES (4 points) - Sex-specific
    # =========================================================================
    
    hormone_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    
    # Male fields
    total_testosterone: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # ng/dL
    free_testosterone: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # pg/mL
    estradiol_male: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)  # pg/mL
    testosterone_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Female fields
    menopause_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # pre/peri/post
    cycle_regularity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # yes/mostly/no
    female_symptoms: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # minimal/mild/moderate/severe
    female_hormone_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    female_hormone_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'symptoms'
    
    # Female exact hormone values
    estradiol_female: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # pg/mL
    progesterone: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # ng/mL
    fsh: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mIU/mL
    lh: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mIU/mL
    testosterone_female: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # ng/dL
    amh: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # ng/mL
    
    # Common
    hormone_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    hormone_assessment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # =========================================================================
    # TEST 3: SEXUAL HEALTH (1 point) - Sex-specific
    # =========================================================================
    
    sexual_health: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # normal/mild/moderate/significant/skip
    sexual_health_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 4: VITAMIN D (2 points)
    # =========================================================================
    
    vitd_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    vitamin_d: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # ng/mL
    vitd_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vitd_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    vitd_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 5: HEMOGLOBIN & IRON (2 points) - Sex-adjusted
    # =========================================================================
    
    iron_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    hemoglobin: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)  # g/dL
    ferritin: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # ng/mL (optional)
    iron_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    iron_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    iron_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 6: EXERCISE HABITS (2 points)
    # =========================================================================
    
    exercise_frequency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 6-7/4-5/2-3/0-1 days
    exercise_cardio: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    exercise_strength: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    exercise_flexibility: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    exercise_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    # =========================================================================
    # TEST 7: SLEEP DURATION & QUALITY (3 points)
    # =========================================================================
    
    sleep_duration: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 7.5-8.5/7-7.4/8.6-9/6-6.9/less6/more9
    sleep_quality: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # most/sometimes/rarely
    sleep_onset: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # fast/medium/slow
    sleep_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    # =========================================================================
    # TEST 8: SKIN & HAIR HEALTH (1 point)
    # =========================================================================
    
    skin_elasticity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # excellent/moderate/poor
    hair_health: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # thick/thinning/loss/significant/na
    appearance_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 9: STRESS & OVERWHELM (1 point)
    # =========================================================================
    
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-10 scale
    stress_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stress_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TOTALS & CLINICAL FLAGS
    # =========================================================================
    
    pillar4_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    pillar4_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    pillar4_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    functional_age_modifier: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    clinical_alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Individual clinical flags
    thyroid_dysfunction_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    low_testosterone_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    hormonal_imbalance_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    vitamin_d_deficiency_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    anemia_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    sleep_disorder_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    chronic_stress_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="pillar4_results",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Pillar4Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"total={self.pillar4_total}/20, category={self.pillar4_category})>"
        )
    
    # =========================================================================
    # TOTAL SCORE CALCULATION
    # =========================================================================
    
    def calculate_pillar4_total(self) -> Decimal:
        """
        Calculate total Pillar 4 score (sum of all 9 test components).
        
        Max 20 points.
        """
        scores = [
            self.thyroid_points,
            self.hormone_points,
            self.sexual_health_points,
            self.vitd_points,
            self.iron_points,
            self.exercise_points,
            self.sleep_points,
            self.appearance_points,
            self.stress_points,
        ]
        
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        
        self.pillar4_total = Decimal(str(round(total, 1)))
        self.pillar4_pct = Decimal(str(round((total / 20) * 100, 2)))
        self.pillar4_category = self._categorize_total(total)
        
        return self.pillar4_total
    
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
        Calculate vitality/hormonal impact on functional age.
        
        Score ranges:
        - 18-20 (90-100%): -2 years
        - 16-17.9 (80-89%): -1 year
        - 14-15.9 (70-79%): 0 years
        - 12-13.9 (60-69%): +1 year
        - 10-11.9 (50-59%): +2 years
        - <10 (<50%): +3 years
        """
        if self.pillar4_total is None:
            return Decimal('0')
        
        total = float(self.pillar4_total)
        
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
        
        # Thyroid dysfunction
        if self.thyroid_points is not None and float(self.thyroid_points) <= 1.5:
            self.thyroid_dysfunction_flag = True
            if float(self.thyroid_points) == 0:
                alerts.append({
                    'code': 'THYROID_CLINICAL',
                    'level': 'urgent',
                    'message': 'URGENT: Clinical thyroid dysfunction. Endocrinology referral needed.',
                })
            else:
                alerts.append({
                    'code': 'THYROID_SUBCLINICAL',
                    'level': 'high',
                    'message': 'Subclinical thyroid dysfunction. Recommend full thyroid panel and follow-up.',
                })
        
        # Low testosterone (male)
        if self.total_testosterone is not None and float(self.total_testosterone) < 300:
            self.low_testosterone_flag = True
            if float(self.total_testosterone) < 264:
                alerts.append({
                    'code': 'HYPOGONADISM',
                    'level': 'high',
                    'message': 'Hypogonadism diagnosed. Endocrinology referral recommended.',
                })
            else:
                alerts.append({
                    'code': 'LOW_TESTOSTERONE',
                    'level': 'moderate',
                    'message': 'Low-normal testosterone. Consider lifestyle optimization and retest.',
                })
        
        # Hormonal imbalance (female)
        if self.female_symptoms in ['moderate', 'severe'] or self.female_hormone_category in ['imbalanced', 'deficient']:
            self.hormonal_imbalance_flag = True
            alerts.append({
                'code': 'HORMONAL_IMBALANCE',
                'level': 'high',
                'message': 'Hormonal imbalance detected. Consider gynecology or endocrinology referral.',
            })
        
        # Vitamin D deficiency
        if self.vitamin_d is not None and float(self.vitamin_d) < 20:
            self.vitamin_d_deficiency_flag = True
            alerts.append({
                'code': 'VITAMIN_D_DEFICIENCY',
                'level': 'moderate',
                'message': 'Vitamin D deficiency. Recommend supplementation: 2000-4000 IU daily.',
            })
        
        # Anemia
        if self.hemoglobin is not None:
            hb = float(self.hemoglobin)
            if hb < 10:
                self.anemia_flag = True
                alerts.append({
                    'code': 'ANEMIA_SEVERE',
                    'level': 'urgent',
                    'message': 'URGENT: Severe anemia. Immediate evaluation needed.',
                })
            elif hb < 12:
                self.anemia_flag = True
                alerts.append({
                    'code': 'ANEMIA',
                    'level': 'high',
                    'message': 'Anemia detected. Work-up for cause recommended.',
                })
        
        # Sleep disorder
        if self.sleep_points is not None and float(self.sleep_points) <= 1.0:
            self.sleep_disorder_flag = True
            alerts.append({
                'code': 'SLEEP_DISORDER',
                'level': 'moderate',
                'message': 'Poor sleep quality/duration. Screen for sleep apnea, insomnia, or depression.',
            })
        
        # Chronic stress
        if self.stress_level is not None and self.stress_level >= 8:
            self.chronic_stress_flag = True
            alerts.append({
                'code': 'CHRONIC_STRESS',
                'level': 'high',
                'message': 'High chronic stress. Recommend stress management counseling and evaluation for burnout.',
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
            # Thyroid
            'thyroid_input_mode': self.thyroid_input_mode,
            'tsh': float(self.tsh) if self.tsh else None,
            'free_t4': float(self.free_t4) if self.free_t4 else None,
            'free_t3': float(self.free_t3) if self.free_t3 else None,
            'thyroid_category_input': self.thyroid_category_input,
            't3_t4_status': self.t3_t4_status,
            'thyroid_points': float(self.thyroid_points) if self.thyroid_points else None,
            'thyroid_category': self.thyroid_category,
            # Sex Hormones
            'hormone_input_mode': self.hormone_input_mode,
            'total_testosterone': float(self.total_testosterone) if self.total_testosterone else None,
            'free_testosterone': float(self.free_testosterone) if self.free_testosterone else None,
            'estradiol_male': float(self.estradiol_male) if self.estradiol_male else None,
            'testosterone_category': self.testosterone_category,
            'menopause_status': self.menopause_status,
            'cycle_regularity': self.cycle_regularity,
            'female_symptoms': self.female_symptoms,
            'female_hormone_category': self.female_hormone_category,
            'hormone_points': float(self.hormone_points) if self.hormone_points else None,
            'hormone_assessment': self.hormone_assessment,
            # Sexual Health
            'sexual_health': self.sexual_health,
            'sexual_health_points': float(self.sexual_health_points) if self.sexual_health_points else None,
            # Vitamin D
            'vitd_input_mode': self.vitd_input_mode,
            'vitamin_d': float(self.vitamin_d) if self.vitamin_d else None,
            'vitd_category_input': self.vitd_category_input,
            'vitd_points': float(self.vitd_points) if self.vitd_points else None,
            'vitd_category': self.vitd_category,
            # Iron
            'iron_input_mode': self.iron_input_mode,
            'hemoglobin': float(self.hemoglobin) if self.hemoglobin else None,
            'ferritin': float(self.ferritin) if self.ferritin else None,
            'iron_category_input': self.iron_category_input,
            'iron_points': float(self.iron_points) if self.iron_points else None,
            'iron_category': self.iron_category,
            # Exercise
            'exercise_frequency': self.exercise_frequency,
            'exercise_cardio': self.exercise_cardio,
            'exercise_strength': self.exercise_strength,
            'exercise_flexibility': self.exercise_flexibility,
            'exercise_points': float(self.exercise_points) if self.exercise_points else None,
            # Sleep
            'sleep_duration': self.sleep_duration,
            'sleep_quality': self.sleep_quality,
            'sleep_onset': self.sleep_onset,
            'sleep_points': float(self.sleep_points) if self.sleep_points else None,
            # Appearance
            'skin_elasticity': self.skin_elasticity,
            'hair_health': self.hair_health,
            'appearance_points': float(self.appearance_points) if self.appearance_points else None,
            # Stress
            'stress_level': self.stress_level,
            'stress_category': self.stress_category,
            'stress_points': float(self.stress_points) if self.stress_points else None,
            # Totals
            'pillar4_total': float(self.pillar4_total) if self.pillar4_total else None,
            'pillar4_pct': float(self.pillar4_pct) if self.pillar4_pct else None,
            'pillar4_category': self.pillar4_category,
            'functional_age_modifier': float(self.functional_age_modifier) if self.functional_age_modifier else None,
            # Alerts
            'clinical_alerts': self.clinical_alerts,
            'thyroid_dysfunction_flag': self.thyroid_dysfunction_flag,
            'low_testosterone_flag': self.low_testosterone_flag,
            'hormonal_imbalance_flag': self.hormonal_imbalance_flag,
            'vitamin_d_deficiency_flag': self.vitamin_d_deficiency_flag,
            'anemia_flag': self.anemia_flag,
            'sleep_disorder_flag': self.sleep_disorder_flag,
            'chronic_stress_flag': self.chronic_stress_flag,
        }
