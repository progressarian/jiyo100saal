"""
Clinical Alerts Model
=====================

Audit trail for all triggered clinical alerts.
"""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, ForeignKey, CheckConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.assessment import Assessment


class ClinicalAlert(Base):
    """
    Clinical Alert Record
    
    Stores triggered alerts for audit and reporting purposes.
    Linked to an assessment.
    """
    
    __tablename__ = 'clinical_alerts'
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign key to assessment
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey('assessments.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    
    # Alert identification
    source_section: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # 'section0', 'section1', 'pillar1', etc.
    
    alert_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # 'SARCOPENIA', 'FALL_RISK_HIGH', 'HYPERTENSIVE_CRISIS', etc.
    
    alert_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # 'urgent', 'high', 'moderate'
    
    alert_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # What triggered this alert
    triggering_values: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="clinical_alerts",
    )
    
    # =========================================================================
    # CONSTRAINTS
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            "alert_level IN ('urgent', 'high', 'moderate')",
            name='check_alert_level_valid',
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"<ClinicalAlert(id={self.id}, code={self.alert_code}, "
            f"level={self.alert_level}, source={self.source_section})>"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'source_section': self.source_section,
            'alert_code': self.alert_code,
            'alert_level': self.alert_level,
            'alert_message': self.alert_message,
            'triggering_values': self.triggering_values,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# =========================================================================
# ALERT CODE DEFINITIONS (Reference)
# =========================================================================

ALERT_CODES = {
    # Section 0 alerts
    'HYPERTENSIVE_CRISIS': {
        'level': 'urgent',
        'section': 'section0',
        'description': 'Blood pressure >180/>120 mmHg',
    },
    'POLYPHARMACY': {
        'level': 'moderate',
        'section': 'section0',
        'description': '5+ medications (polypharmacy)',
    },
    'HIGH_POLYPHARMACY': {
        'level': 'high',
        'section': 'section0',
        'description': '10+ medications (high polypharmacy)',
    },
    'FRAGILITY_FRACTURE': {
        'level': 'high',
        'section': 'section0',
        'description': 'History of low-impact fracture',
    },
    'MULTIPLE_TBI': {
        'level': 'high',
        'section': 'section0',
        'description': 'Multiple traumatic brain injuries',
    },
    'EARLY_FAMILY_CVD': {
        'level': 'moderate',
        'section': 'section0',
        'description': 'Family history of early cardiovascular disease',
    },
    
    # Section 1 alerts
    'SARCOPENIA_BODY_COMP': {
        'level': 'high',
        'section': 'section1',
        'description': 'Low muscle mass (sarcopenia criteria)',
    },
    'HIGH_VISCERAL_FAT': {
        'level': 'moderate',
        'section': 'section1',
        'description': 'Visceral fat area >160 cm²',
    },
    'METABOLIC_SYNDROME': {
        'level': 'high',
        'section': 'section1',
        'description': '3+ metabolic syndrome criteria met',
    },
    
    # Pillar 1 alerts
    'SARCOPENIA': {
        'level': 'high',
        'section': 'pillar1',
        'description': 'Low grip strength (<27 kg male, <16 kg female)',
    },
    'FALL_RISK_VERY_HIGH': {
        'level': 'urgent',
        'section': 'pillar1',
        'description': 'Very high fall risk (multiple indicators)',
    },
    'FALL_RISK_HIGH': {
        'level': 'high',
        'section': 'pillar1',
        'description': 'High fall risk',
    },
    'SEVERE_FUNCTIONAL_LIMITATION': {
        'level': 'high',
        'section': 'pillar1',
        'description': 'Very low chair stand count',
    },
    'VERY_LOW_VO2': {
        'level': 'high',
        'section': 'pillar1',
        'description': 'VO2 max <20 mL/kg/min (high mortality risk)',
    },
    'VERY_LOW_GAIT_SPEED': {
        'level': 'urgent',
        'section': 'pillar1',
        'description': 'Gait speed <0.6 m/s (severe mobility limitation)',
    },
    'VERY_LOW_6MWT': {
        'level': 'high',
        'section': 'pillar1',
        'description': '6-minute walk <300m (poor prognosis)',
    },
}
