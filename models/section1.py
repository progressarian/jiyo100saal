"""
Section 1 Model - Body Composition
==================================

DEXA, BIA, and manual body composition measurements and scoring.
"""

from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Integer, Boolean, ForeignKey,
    CheckConstraint, Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from models.base import Base

if TYPE_CHECKING:
    from models.assessment import Assessment


class Section1Results(Base):
    """
    Section 1: Body Composition
    
    Supports three input methods:
    - DEXA (gold standard)
    - BIA (bioelectrical impedance)
    - Manual (skinfolds and circumferences)
    """
    
    __tablename__ = 'section_1_results'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key to assessment (1:1)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey('assessments.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Input method used
    input_method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )  # 'dexa', 'bia', 'manual'
    
    # =========================================================================
    # DEXA FIELDS
    # =========================================================================
    
    dexa_body_fat_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    dexa_total_fat_mass_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    dexa_lean_mass_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    dexa_asmi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )  # Appendicular Skeletal Muscle Mass Index (kg/m²)
    
    dexa_visceral_fat_area: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # cm²
    
    dexa_android_gynoid_ratio: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
    
    # Bone density T-scores
    dexa_lumbar_tscore: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
    )
    
    dexa_hip_tscore: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
    )
    
    # =========================================================================
    # BIA FIELDS
    # =========================================================================
    
    bia_body_fat_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    bia_lean_mass_kg: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    bia_water_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    bia_visceral_fat_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # Proprietary 1-30 scale
    
    # =========================================================================
    # MANUAL FIELDS (Skinfolds)
    # =========================================================================
    
    skinfold_chest_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    skinfold_abdomen_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    skinfold_thigh_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    skinfold_triceps_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    skinfold_subscapular_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    skinfold_suprailiac_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    skinfold_midaxillary_mm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    # Additional circumference for Navy method
    neck_circumference_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    # =========================================================================
    # CALCULATED FIELDS (all methods)
    # =========================================================================
    
    # Final body fat % (from whichever method used)
    body_fat_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    # Lean Mass Index = lean mass / height²
    lean_mass_index: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
    
    # Waist-to-hip ratio (uses Section 0 waist + hip)
    waist_hip_ratio: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
    
    # Body density (intermediate calc for skinfolds)
    body_density: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 5),
        nullable=True,
    )
    
    # =========================================================================
    # SCORING
    # =========================================================================
    
    body_fat_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )  # 0-100%
    
    body_fat_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # Excellent, Good, Fair, Poor, Very Poor
    
    lmi_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    lmi_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    visceral_fat_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    fat_distribution_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    # =========================================================================
    # CLINICAL FLAGS
    # =========================================================================
    
    sarcopenia_risk: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    
    metabolic_syndrome_criteria_met: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # How many of 5 criteria met
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="section1_results",
    )
    
    # =========================================================================
    # CONSTRAINTS
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            "input_method IN ('dexa', 'bia', 'manual')",
            name='check_input_method_valid',
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Section1Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"method={self.input_method}, body_fat={self.body_fat_pct}%)>"
        )
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    @validates('input_method')
    def validate_input_method(self, key: str, value: str) -> str:
        """Validate input method."""
        valid_methods = ('dexa', 'bia', 'manual')
        if value not in valid_methods:
            raise ValueError(f"input_method must be one of {valid_methods}, got '{value}'")
        return value
    
    @validates('dexa_body_fat_pct', 'bia_body_fat_pct', 'body_fat_pct')
    def validate_body_fat(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Validate body fat percentage (3-60%)."""
        if value is not None:
            val = float(value)
            if not (3 <= val <= 60):
                raise ValueError(f"Body fat % must be between 3-60, got {val}")
        return value
    
    # =========================================================================
    # CALCULATED PROPERTIES
    # =========================================================================
    
    @property
    def skinfold_sum(self) -> Optional[float]:
        """Sum of all 7 skinfold measurements in mm."""
        sites = [
            self.skinfold_chest_mm,
            self.skinfold_abdomen_mm,
            self.skinfold_thigh_mm,
            self.skinfold_triceps_mm,
            self.skinfold_subscapular_mm,
            self.skinfold_suprailiac_mm,
            self.skinfold_midaxillary_mm,
        ]
        
        if all(s is not None for s in sites):
            return sum(float(s) for s in sites)
        return None
    
    # =========================================================================
    # METHODS
    # =========================================================================
    
    def calculate_body_density_jackson_pollock(self, age: int, sex: str) -> Optional[Decimal]:
        """
        Calculate body density using Jackson-Pollock 7-site formula.
        
        Males:
        BD = 1.112 - 0.00043499(sum) + 0.00000055(sum²) - 0.00028826(age)
        
        Females:
        BD = 1.097 - 0.00046971(sum) + 0.00000056(sum²) - 0.00012828(age)
        """
        sum_sf = self.skinfold_sum
        if sum_sf is None:
            return None
        
        if sex == 'male':
            bd = (1.112 
                  - 0.00043499 * sum_sf 
                  + 0.00000055 * (sum_sf ** 2) 
                  - 0.00028826 * age)
        else:  # female
            bd = (1.097 
                  - 0.00046971 * sum_sf 
                  + 0.00000056 * (sum_sf ** 2) 
                  - 0.00012828 * age)
        
        self.body_density = Decimal(str(round(bd, 5)))
        return self.body_density
    
    def calculate_body_fat_from_density(self) -> Optional[Decimal]:
        """
        Calculate body fat % from body density using Siri equation.
        
        Body Fat % = (495 / Body Density) - 450
        """
        if self.body_density is None:
            return None
        
        bd = float(self.body_density)
        bf_pct = (495 / bd) - 450
        
        return Decimal(str(round(bf_pct, 1)))
    
    def calculate_lean_mass_index(self, height_cm: Decimal) -> Optional[Decimal]:
        """
        Calculate Lean Mass Index (LMI).
        
        LMI = Lean Mass (kg) / Height (m)²
        """
        lean_mass = None
        
        if self.input_method == 'dexa' and self.dexa_lean_mass_kg:
            lean_mass = float(self.dexa_lean_mass_kg)
        elif self.input_method == 'bia' and self.bia_lean_mass_kg:
            lean_mass = float(self.bia_lean_mass_kg)
        
        if lean_mass and height_cm:
            height_m = float(height_cm) / 100
            lmi = lean_mass / (height_m ** 2)
            self.lean_mass_index = Decimal(str(round(lmi, 2)))
            return self.lean_mass_index
        
        return None
    
    def set_final_body_fat(self) -> None:
        """
        Set the final body_fat_pct based on input method.
        """
        if self.input_method == 'dexa' and self.dexa_body_fat_pct:
            self.body_fat_pct = self.dexa_body_fat_pct
        elif self.input_method == 'bia' and self.bia_body_fat_pct:
            self.body_fat_pct = self.bia_body_fat_pct
        elif self.input_method == 'manual':
            # Would need to calculate from skinfolds first
            bf = self.calculate_body_fat_from_density()
            if bf:
                self.body_fat_pct = bf
    
    def assess_sarcopenia_risk(self, sex: str) -> bool:
        """
        Assess sarcopenia risk based on muscle mass.
        
        ASMI cutoffs (EWGSOP2):
        - Males: <7.0 kg/m²
        - Females: <5.4 kg/m²
        
        LMI cutoffs:
        - Males: <14 kg/m²
        - Females: <11 kg/m²
        """
        # Check ASMI if available (more accurate)
        if self.dexa_asmi:
            asmi = float(self.dexa_asmi)
            if sex == 'male':
                self.sarcopenia_risk = asmi < 7.0
            else:
                self.sarcopenia_risk = asmi < 5.4
            return self.sarcopenia_risk
        
        # Fall back to LMI
        if self.lean_mass_index:
            lmi = float(self.lean_mass_index)
            if sex == 'male':
                self.sarcopenia_risk = lmi < 14
            else:
                self.sarcopenia_risk = lmi < 11
            return self.sarcopenia_risk
        
        return False
    
    def score_body_fat(self, age: int, sex: str) -> tuple[Decimal, str]:
        """
        Score body fat percentage based on age/sex-adjusted tables.
        
        Returns:
            Tuple of (score as percentage 0-100, category string)
        """
        if self.body_fat_pct is None:
            return Decimal('0'), 'Unknown'
        
        bf = float(self.body_fat_pct)
        
        # Age group determination
        if age < 50:
            age_group = '30-49'
        elif age < 70:
            age_group = '50-69'
        else:
            age_group = '70+'
        
        # Scoring tables per spec
        # Format: (upper_bound, score_pct, category)
        # Score is percentage (100 = Excellent, 25 = Very Poor)
        
        if sex == 'male':
            if age_group == '30-49':
                thresholds = [
                    (14, 100, 'Excellent'),
                    (17, 85, 'Good'),
                    (21, 70, 'Fair'),
                    (24, 50, 'Poor'),
                    (float('inf'), 25, 'Very Poor'),
                ]
            elif age_group == '50-69':
                thresholds = [
                    (16, 100, 'Excellent'),
                    (19, 85, 'Good'),
                    (23, 70, 'Fair'),
                    (26, 50, 'Poor'),
                    (float('inf'), 25, 'Very Poor'),
                ]
            else:  # 70+
                thresholds = [
                    (18, 100, 'Excellent'),
                    (21, 85, 'Good'),
                    (25, 70, 'Fair'),
                    (28, 50, 'Poor'),
                    (float('inf'), 25, 'Very Poor'),
                ]
        else:  # female
            if age_group == '30-49':
                thresholds = [
                    (20, 100, 'Excellent'),
                    (24, 85, 'Good'),
                    (29, 70, 'Fair'),
                    (32, 50, 'Poor'),
                    (float('inf'), 25, 'Very Poor'),
                ]
            elif age_group == '50-69':
                thresholds = [
                    (22, 100, 'Excellent'),
                    (26, 85, 'Good'),
                    (31, 70, 'Fair'),
                    (34, 50, 'Poor'),
                    (float('inf'), 25, 'Very Poor'),
                ]
            else:  # 70+
                thresholds = [
                    (24, 100, 'Excellent'),
                    (28, 85, 'Good'),
                    (33, 70, 'Fair'),
                    (36, 50, 'Poor'),
                    (float('inf'), 25, 'Very Poor'),
                ]
        
        for upper, score, category in thresholds:
            if bf < upper:
                self.body_fat_score = Decimal(str(score))
                self.body_fat_category = category
                return self.body_fat_score, category
        
        # Fallback
        self.body_fat_score = Decimal('25')
        self.body_fat_category = 'Very Poor'
        return self.body_fat_score, 'Very Poor'
    
    def score_lmi(self, sex: str) -> tuple[Decimal, str]:
        """
        Score Lean Mass Index.
        
        Returns:
            Tuple of (score as percentage 0-100, category string)
        """
        if self.lean_mass_index is None:
            return Decimal('0'), 'Unknown'
        
        lmi = float(self.lean_mass_index)
        
        if sex == 'male':
            thresholds = [
                (14, 25, 'Sarcopenia'),
                (16, 50, 'Low'),
                (18, 70, 'Fair'),
                (20, 85, 'Good'),
                (float('inf'), 100, 'Excellent'),
            ]
        else:  # female
            thresholds = [
                (11, 25, 'Sarcopenia'),
                (13, 50, 'Low'),
                (15, 70, 'Fair'),
                (17, 85, 'Good'),
                (float('inf'), 100, 'Excellent'),
            ]
        
        for upper, score, category in thresholds:
            if lmi < upper:
                self.lmi_score = Decimal(str(score))
                self.lmi_category = category
                return self.lmi_score, category
        
        # Above highest threshold = Excellent
        self.lmi_score = Decimal('100')
        self.lmi_category = 'Excellent'
        return self.lmi_score, 'Excellent'
    
    def score_visceral_fat(self) -> tuple[Decimal, str]:
        """
        Score visceral fat area.
        
        Returns:
            Tuple of (score as percentage 0-100, category string)
        """
        vfa = None
        
        # Try DEXA first
        if self.dexa_visceral_fat_area is not None:
            vfa = self.dexa_visceral_fat_area
            thresholds = [
                (100, 100, 'Low Risk'),
                (130, 85, 'Borderline'),
                (160, 70, 'Elevated'),
                (200, 50, 'High'),
                (float('inf'), 25, 'Very High'),
            ]
        # Fall back to BIA level
        elif self.bia_visceral_fat_level is not None:
            level = self.bia_visceral_fat_level
            thresholds = [
                (10, 100, 'Healthy'),
                (15, 70, 'Elevated'),
                (float('inf'), 40, 'High'),
            ]
            vfa = level
        
        if vfa is None:
            return Decimal('0'), 'Unknown'
        
        for upper, score, category in thresholds:
            if vfa < upper:
                self.visceral_fat_score = Decimal(str(score))
                return self.visceral_fat_score, category
        
        # Above highest
        self.visceral_fat_score = Decimal('25')
        return self.visceral_fat_score, 'Very High'
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'input_method': self.input_method,
            'body_fat_pct': float(self.body_fat_pct) if self.body_fat_pct else None,
            'body_fat_score': float(self.body_fat_score) if self.body_fat_score else None,
            'body_fat_category': self.body_fat_category,
            'lean_mass_index': float(self.lean_mass_index) if self.lean_mass_index else None,
            'lmi_score': float(self.lmi_score) if self.lmi_score else None,
            'lmi_category': self.lmi_category,
            'visceral_fat_score': float(self.visceral_fat_score) if self.visceral_fat_score else None,
            'sarcopenia_risk': self.sarcopenia_risk,
            'metabolic_syndrome_criteria_met': self.metabolic_syndrome_criteria_met,
        }
