"""
Assessment Model
================

Core assessment record linking patient to all test results.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Date, Text, Integer, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from models.base import Base

if TYPE_CHECKING:
    from models.patient import Patient
    from models.section0 import Section0Results
    from models.section1 import Section1Results
    from models.pillar1 import Pillar1Results
    from models.pillar2 import Pillar2Results
    from models.pillar3 import Pillar3Results
    from models.pillar4 import Pillar4Results
    from models.pillar5 import Pillar5Results
    from models.alerts import ClinicalAlert


class Assessment(Base):
    """
    A single functional aging assessment session.
    
    Links a patient to all their test results (Section 0, Section 1, Pillar 1, etc.)
    Stores calculated totals and functional age.
    """
    
    __tablename__ = 'assessments'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key to patient
    patient_id: Mapped[int] = mapped_column(
        ForeignKey('patients.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    
    # Assessment metadata
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    assessment_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='comprehensive',
    )  # 'comprehensive' or 'practical'
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='draft',
    )  # 'draft', 'in_progress', 'completed'
    
    clinician_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # =========================================================================
    # CALCULATED TOTALS (populated after sections complete)
    # =========================================================================
    
    # Pillar 1 total (0-20 points, sum of 8 tests)
    pillar1_total_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )
    
    # Final functional age (biological age estimate)
    functional_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Delta from chronological age (positive = older, negative = younger)
    functional_age_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="assessments",
    )
    
    section0_results: Mapped[Optional["Section0Results"]] = relationship(
        "Section0Results",
        back_populates="assessment",
        uselist=False,  # 1:1 relationship
        cascade="all, delete-orphan",
    )
    
    section1_results: Mapped[Optional["Section1Results"]] = relationship(
        "Section1Results",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    pillar1_results: Mapped[Optional["Pillar1Results"]] = relationship(
        "Pillar1Results",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    pillar2_results: Mapped[Optional["Pillar2Results"]] = relationship(
        "Pillar2Results",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    pillar3_results: Mapped[Optional["Pillar3Results"]] = relationship(
        "Pillar3Results",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    pillar4_results: Mapped[Optional["Pillar4Results"]] = relationship(
        "Pillar4Results",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    pillar5_results: Mapped[Optional["Pillar5Results"]] = relationship(
        "Pillar5Results",
        back_populates="assessment",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    clinical_alerts: Mapped[list["ClinicalAlert"]] = relationship(
        "ClinicalAlert",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="ClinicalAlert.created_at",
    )
    
    # =========================================================================
    # CONSTRAINTS
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            "assessment_type IN ('comprehensive', 'practical')",
            name='check_assessment_type_valid',
        ),
        CheckConstraint(
            "status IN ('draft', 'in_progress', 'completed')",
            name='check_status_valid',
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Assessment(id={self.id}, patient_id={self.patient_id}, "
            f"date={self.assessment_date}, type={self.assessment_type}, "
            f"status={self.status})>"
        )
    
    # =========================================================================
    # CALCULATED PROPERTIES
    # =========================================================================
    
    @property
    def age_at_assessment(self) -> int:
        """
        Patient's age at the time of assessment.
        
        This is the authoritative age used for all scoring calculations.
        """
        if self.patient and self.assessment_date:
            return self.patient.age_at_date(self.assessment_date)
        return 0
    
    @property
    def sex(self) -> str:
        """Patient's sex (shortcut for scoring functions)."""
        if self.patient:
            return self.patient.sex
        return ''
    
    @property
    def is_complete(self) -> bool:
        """Check if all required sections are complete."""
        if self.assessment_type == 'comprehensive':
            return all([
                self.section0_results is not None,
                self.section1_results is not None,
                self.pillar1_results is not None,
                self.pillar2_results is not None,
            ])
        else:  # practical
            # Practical may have fewer requirements
            return all([
                self.section0_results is not None,
                self.pillar1_results is not None,
            ])
    
    @property
    def completion_percentage(self) -> float:
        """Calculate how much of the assessment is complete."""
        sections = [
            self.section0_results is not None,
            self.section1_results is not None,
            self.pillar1_results is not None,
            self.pillar2_results is not None,
        ]
        return (sum(sections) / len(sections)) * 100
    
    @property
    def pillar1_percentage(self) -> Optional[float]:
        """Pillar 1 score as percentage (0-100)."""
        if self.pillar1_total_score is not None:
            return float(self.pillar1_total_score / 20 * 100)
        return None
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    @validates('assessment_type')
    def validate_assessment_type(self, key: str, value: str) -> str:
        """Validate assessment type."""
        valid_types = ('comprehensive', 'practical')
        if value not in valid_types:
            raise ValueError(f"assessment_type must be one of {valid_types}, got '{value}'")
        return value
    
    @validates('status')
    def validate_status(self, key: str, value: str) -> str:
        """Validate status."""
        valid_statuses = ('draft', 'in_progress', 'completed')
        if value not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}, got '{value}'")
        return value
    
    @validates('assessment_date')
    def validate_assessment_date(self, key: str, value: date) -> date:
        """Validate assessment date is not in the future."""
        if value > date.today():
            raise ValueError("Assessment date cannot be in the future")
        return value
    
    # =========================================================================
    # METHODS
    # =========================================================================
    
    def validate_age_eligibility(self) -> bool:
        """
        Check if patient age is within eligible range (30-120).
        
        Returns:
            True if eligible, raises ValueError if not
        """
        age = self.age_at_assessment
        if not (30 <= age <= 120):
            raise ValueError(
                f"Patient age must be between 30-120 years for assessment. "
                f"Patient is {age} years old."
            )
        return True
    
    def get_age_group(self) -> str:
        """
        Get age group for scoring table lookup.
        
        Returns:
            Age group string (e.g., '30-49', '50-64', '65-79', '80+')
        """
        age = self.age_at_assessment
        
        if age < 50:
            return '30-49'
        elif age < 65:
            return '50-64'
        elif age < 80:
            return '65-79'
        else:
            return '80+'
    
    def calculate_functional_age(self) -> Optional[int]:
        """
        Calculate functional age based on all assessment results.
        
        This is a preliminary calculation - full algorithm will be
        implemented when all pillars are complete.
        
        Returns:
            Estimated functional/biological age
        """
        chronological_age = self.age_at_assessment
        
        # Start with chronological age
        delta = 0
        
        # Apply Section 0 modifiers (family history, lifestyle)
        if self.section0_results:
            delta += self.section0_results.functional_age_modifier or 0
        
        # Apply Pillar 1 impact (Movement & Strength)
        if self.pillar1_results:
            delta += self.pillar1_results.functional_age_impact or 0
        
        # Apply Pillar 2 impact (Cognitive Function)
        if self.pillar2_results:
            modifier = self.pillar2_results.functional_age_modifier
            if modifier:
                delta += float(modifier)
        
        functional_age = chronological_age + int(delta)
        
        # Store calculated values
        self.functional_age = functional_age
        self.functional_age_delta = int(delta)
        
        return functional_age
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'assessment_date': self.assessment_date.isoformat(),
            'assessment_type': self.assessment_type,
            'status': self.status,
            'clinician_name': self.clinician_name,
            'age_at_assessment': self.age_at_assessment,
            'sex': self.sex,
            'age_group': self.get_age_group(),
            'pillar1_total_score': float(self.pillar1_total_score) if self.pillar1_total_score else None,
            'pillar1_percentage': self.pillar1_percentage,
            'functional_age': self.functional_age,
            'functional_age_delta': self.functional_age_delta,
            'is_complete': self.is_complete,
            'completion_percentage': self.completion_percentage,
            'has_section0': self.section0_results is not None,
            'has_section1': self.section1_results is not None,
            'has_pillar1': self.pillar1_results is not None,
            'has_pillar2': self.pillar2_results is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
