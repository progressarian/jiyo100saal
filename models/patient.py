"""
Patient Model
=============

Core patient demographics and metadata.
"""

from datetime import date, datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Date, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from models.base import Base

if TYPE_CHECKING:
    from models.assessment import Assessment


class Patient(Base):
    """
    Patient demographic information.
    
    A patient can have multiple assessments over time.
    Age is calculated dynamically from date_of_birth.
    """
    
    __tablename__ = 'patients'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Demographics
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(10), nullable=False)  # 'male' or 'female'
    
    # Contact (optional)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # External reference (hospital MRN, etc.)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    assessments: Mapped[List["Assessment"]] = relationship(
        "Assessment",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="Assessment.assessment_date.desc()",
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("sex IN ('male', 'female')", name='check_sex_valid'),
    )
    
    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, name='{self.full_name}', dob={self.date_of_birth}, sex={self.sex})>"
    
    # =========================================================================
    # CALCULATED PROPERTIES
    # =========================================================================
    
    @property
    def full_name(self) -> str:
        """Full name (first + last)."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def current_age(self) -> int:
        """
        Current age in years (as of today).
        
        Returns:
            Age in complete years
        """
        return self._calculate_age(date.today())
    
    def age_at_date(self, target_date: date) -> int:
        """
        Age in years at a specific date.
        
        Args:
            target_date: Date to calculate age at
            
        Returns:
            Age in complete years at target_date
        """
        return self._calculate_age(target_date)
    
    def _calculate_age(self, as_of_date: date) -> int:
        """
        Calculate age in complete years.
        
        Handles birthday edge case correctly.
        """
        age = as_of_date.year - self.date_of_birth.year
        
        # Subtract 1 if birthday hasn't occurred yet this year
        if (as_of_date.month, as_of_date.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        
        return age
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    @validates('sex')
    def validate_sex(self, key: str, value: str) -> str:
        """Validate sex is 'male' or 'female'."""
        if value not in ('male', 'female'):
            raise ValueError(f"Sex must be 'male' or 'female', got '{value}'")
        return value
    
    @validates('date_of_birth')
    def validate_date_of_birth(self, key: str, value: date) -> date:
        """
        Validate date of birth is reasonable.
        
        - Must be in the past
        - Patient age must be reasonable (not > 130)
        """
        if value is None:
            raise ValueError("Date of birth is required")
        
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        
        # Calculate age with the new value
        today = date.today()
        age = today.year - value.year
        if (today.month, today.day) < (value.month, value.day):
            age -= 1
        
        # Note: We allow any age for patient creation, but assessments
        # will validate 30-120 range at assessment time
        if age > 130:
            raise ValueError(f"Invalid date of birth (age would be {age})")
        
        return value
    
    @validates('email')
    def validate_email(self, key: str, value: Optional[str]) -> Optional[str]:
        """Basic email format validation."""
        if value is None:
            return None
        
        if '@' not in value or '.' not in value:
            raise ValueError(f"Invalid email format: {value}")
        
        return value.lower().strip()
    
    # =========================================================================
    # METHODS
    # =========================================================================
    
    def get_latest_assessment(self) -> Optional["Assessment"]:
        """Get the most recent assessment for this patient."""
        if self.assessments:
            return self.assessments[0]  # Already ordered by date desc
        return None
    
    def get_assessments_count(self) -> int:
        """Get total number of assessments."""
        return len(self.assessments)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat(),
            'sex': self.sex,
            'current_age': self.current_age,
            'phone': self.phone,
            'email': self.email,
            'external_id': self.external_id,
            'assessments_count': self.get_assessments_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
