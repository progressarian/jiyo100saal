"""
Pillar 2 Model - Cognitive Function
====================================

11 cognitive test components with scoring and clinical alerts.
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


class Pillar2Results(Base):
    """
    Pillar 2: Cognitive Function Assessment
    
    11 Test Components (20 points total):
    1. Immediate Word Recall (2 pts)
    2. Delayed Word Recall (2 pts)
    3. Digit Span Forward (1 pt)
    4. Digit Span Backward (1 pt)
    5. Trail Making A (3 pts)
    6. Trail Making B (3 pts)
    7. DSST - Digital Symbol Substitution (3 pts)
    8. Clock Drawing (2 pts)
    9. Verbal Fluency - Animals (2 pts)
    10. PHQ-2 Depression Screen (1 pt)
    11. GAD-2 Anxiety Screen (1 pt)
    
    Note: All scoring functions enforce maximum caps to prevent scores exceeding limits.
    """
    
    __tablename__ = 'pillar_2_results'
    
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
    # TEST 1: IMMEDIATE WORD RECALL (2 points max)
    # =========================================================================
    
    # Word list: Face, Velvet, Church, Daisy, Red, Salt, Button, Cabin, Pole, Ticket
    memory_immediate_word1: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Face
    memory_immediate_word2: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Velvet
    memory_immediate_word3: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Church
    memory_immediate_word4: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Daisy
    memory_immediate_word5: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Red
    memory_immediate_word6: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Salt
    memory_immediate_word7: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Button
    memory_immediate_word8: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Cabin
    memory_immediate_word9: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Pole
    memory_immediate_word10: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Ticket
    
    memory_immediate_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_immediate_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    memory_immediate_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # =========================================================================
    # TEST 2: DELAYED WORD RECALL (2 points max)
    # =========================================================================
    
    memory_delayed_word1: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word2: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word3: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word4: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word5: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word6: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word7: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word8: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word9: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_delayed_word10: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    memory_delayed_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    memory_delayed_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    memory_delayed_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    memory_retention_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    memory_retention_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # True if <50%
    
    # =========================================================================
    # TEST 3 & 4: DIGIT SPAN (2 points max: Forward 1pt, Backward 1pt)
    # =========================================================================
    
    digit_span_forward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    digit_span_forward_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    digit_span_forward_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    digit_span_backward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    digit_span_backward_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    digit_span_backward_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    digit_span_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    digit_span_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)  # Combined
    digit_span_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # =========================================================================
    # TEST 5 & 6: TRAIL MAKING TESTS (6 points max: A=3pts, B=3pts)
    # =========================================================================
    
    trails_a_time: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    trails_a_errors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trails_a_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    trails_a_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    trails_b_time: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)
    trails_b_errors: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trails_b_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    trails_b_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    trails_ba_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    trails_total_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 7: DSST - DIGITAL SYMBOL SUBSTITUTION (3 points max)
    # =========================================================================
    
    dsst_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dsst_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    dsst_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    dsst_percentile: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # =========================================================================
    # TEST 8: CLOCK DRAWING TEST (2 points max)
    # =========================================================================
    
    clock_circle_intact: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    clock_numbers_present: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    clock_numbers_sequence: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    clock_numbers_position: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    clock_hands_present: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    clock_hands_correct_time: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    clock_hands_proportion: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    clock_score_raw: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-7 components
    clock_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    clock_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    clock_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # =========================================================================
    # TEST 9: VERBAL FLUENCY - ANIMALS (2 points max)
    # =========================================================================
    
    verbal_fluency_animals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verbal_fluency_repetitions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verbal_fluency_intrusions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verbal_fluency_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    verbal_fluency_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # =========================================================================
    # TEST 10: PHQ-2 DEPRESSION SCREEN (1 point max)
    # =========================================================================
    
    phq2_interest: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-3
    phq2_depressed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-3
    phq2_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-6
    phq2_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    phq2_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phq2_followup_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # ≥3
    phq2_urgent_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # ≥5
    
    # =========================================================================
    # TEST 11: GAD-2 ANXIETY SCREEN (1 point max)
    # =========================================================================
    
    gad2_nervous: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-3
    gad2_worry: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-3
    gad2_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-6
    gad2_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    gad2_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gad2_followup_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # ≥3
    gad2_urgent_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # ≥5
    
    # =========================================================================
    # TOTALS & CLINICAL ALERTS
    # =========================================================================
    
    pillar2_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    pillar2_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    pillar2_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    functional_age_modifier: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    
    clinical_alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Individual alert flags
    cognitive_concern_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    executive_dysfunction_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    memory_deficit_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    language_concern_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    depression_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    anxiety_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="pillar2_results",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Pillar2Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"total={self.pillar2_total}/20, category={self.pillar2_category})>"
        )
    
    # =========================================================================
    # CALCULATED VALUES
    # =========================================================================
    
    def calculate_immediate_memory_count(self) -> int:
        """Count words recalled immediately."""
        words = [
            self.memory_immediate_word1, self.memory_immediate_word2,
            self.memory_immediate_word3, self.memory_immediate_word4,
            self.memory_immediate_word5, self.memory_immediate_word6,
            self.memory_immediate_word7, self.memory_immediate_word8,
            self.memory_immediate_word9, self.memory_immediate_word10,
        ]
        count = sum(1 for w in words if w is True)
        self.memory_immediate_count = count
        return count
    
    def calculate_delayed_memory_count(self) -> int:
        """Count words recalled after delay."""
        words = [
            self.memory_delayed_word1, self.memory_delayed_word2,
            self.memory_delayed_word3, self.memory_delayed_word4,
            self.memory_delayed_word5, self.memory_delayed_word6,
            self.memory_delayed_word7, self.memory_delayed_word8,
            self.memory_delayed_word9, self.memory_delayed_word10,
        ]
        count = sum(1 for w in words if w is True)
        self.memory_delayed_count = count
        return count
    
    def calculate_retention_rate(self) -> Optional[float]:
        """Calculate delayed/immediate retention rate."""
        if self.memory_immediate_count and self.memory_immediate_count > 0:
            delayed = self.memory_delayed_count or 0
            rate = (delayed / self.memory_immediate_count) * 100
            self.memory_retention_pct = Decimal(str(round(rate, 1)))
            self.memory_retention_flag = rate < 50
            return rate
        return None
    
    def calculate_trails_ratio(self) -> None:
        """Calculate B/A ratio for executive control assessment."""
        if self.trails_a_time and self.trails_b_time:
            a_time = float(self.trails_a_time)
            b_time = float(self.trails_b_time)
            if a_time > 0:
                ratio = b_time / a_time
                self.trails_ba_ratio = Decimal(str(round(ratio, 2)))
    
    def calculate_digit_span_total(self) -> None:
        """Calculate total digit span (forward + backward)."""
        forward = self.digit_span_forward or 0
        backward = self.digit_span_backward or 0
        self.digit_span_total = forward + backward
    
    def calculate_trails_total(self) -> None:
        """Calculate total trails points (A + B), capped at 6.0."""
        a_pts = float(self.trails_a_points) if self.trails_a_points else 0
        b_pts = float(self.trails_b_points) if self.trails_b_points else 0
        total = a_pts + b_pts
        # Cap at maximum 6.0 points for combined trails
        capped_total = min(total, 6.0)
        self.trails_total_points = Decimal(str(round(capped_total, 2)))
    
    def calculate_clock_raw_score(self) -> int:
        """Calculate clock drawing raw score from components."""
        components = [
            self.clock_circle_intact,
            self.clock_numbers_present,
            self.clock_numbers_sequence,
            self.clock_numbers_position,
            self.clock_hands_present,
            self.clock_hands_correct_time,
            self.clock_hands_proportion,
        ]
        score = sum(1 for c in components if c is True)
        self.clock_score_raw = score
        return score
    
    def calculate_phq2_total(self) -> int:
        """Calculate PHQ-2 total."""
        total = (self.phq2_interest or 0) + (self.phq2_depressed or 0)
        self.phq2_total = total
        self.phq2_followup_flag = total >= 3
        self.phq2_urgent_flag = total >= 5
        return total
    
    def calculate_gad2_total(self) -> int:
        """Calculate GAD-2 total."""
        total = (self.gad2_nervous or 0) + (self.gad2_worry or 0)
        self.gad2_total = total
        self.gad2_followup_flag = total >= 3
        self.gad2_urgent_flag = total >= 5
        return total
    
    # =========================================================================
    # TOTAL SCORE CALCULATION
    # =========================================================================
    
    def calculate_pillar2_total(self) -> Decimal:
        """
        Calculate total Pillar 2 score (sum of all 11 test components).
        
        Max 18 points (with Trails A/B capped at 1.5 each).
        """
        scores = [
            self.memory_immediate_points,
            self.memory_delayed_points,
            self.digit_span_forward_points,
            self.digit_span_backward_points,
            self.trails_a_points,
            self.trails_b_points,
            self.dsst_points,
            self.clock_points,
            self.verbal_fluency_points,
            self.phq2_points,
            self.gad2_points,
        ]
        
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        
        # Cap total at maximum possible (18.0 points)
        total = min(total, 18.0)
        
        self.pillar2_total = Decimal(str(round(total, 2)))
        self.pillar2_pct = Decimal(str(round((total / 18) * 100, 2)))
        self.pillar2_category = self._categorize_total(total)
        
        # Also calculate combined scores
        if self.digit_span_forward_points and self.digit_span_backward_points:
            self.digit_span_points = self.digit_span_forward_points + self.digit_span_backward_points
        
        return self.pillar2_total
    
    def _categorize_total(self, total: float) -> str:
        """Categorize total score (out of 18)."""
        pct = (total / 18) * 100
        
        if pct >= 90:
            return 'Excellent'
        elif pct >= 75:
            return 'Good'
        elif pct >= 55:
            return 'Fair'
        elif pct >= 40:
            return 'Below Average'
        else:
            return 'Poor'
    
    def calculate_functional_age_modifier(self) -> Decimal:
        """
        Calculate cognitive impact on functional age.
        
        Based on score out of 20:
        - ≥18/20 (90%+): -2 years (Excellent)
        - 16-18 (80-89%): -1 year (Good)
        - 14-16 (70-79%): 0 years (Average)
        - 12-14 (60-69%): +1 year (Below Average)
        - 10-12 (50-59%): +2 years (Poor)
        - <10 (<50%): +3 years (Very Poor)
        """
        if self.pillar2_pct is None:
            return Decimal('0')
        
        pct = float(self.pillar2_pct)
        
        if pct >= 90:  # ≥18/20
            modifier = -2.0
        elif pct >= 80:  # 16-18
            modifier = -1.0
        elif pct >= 70:  # 14-16
            modifier = 0.0
        elif pct >= 60:  # 12-14
            modifier = 1.0
        elif pct >= 50:  # 10-12
            modifier = 2.0
        else:  # <10
            modifier = 3.0
        
        self.functional_age_modifier = Decimal(str(modifier))
        return self.functional_age_modifier
    
    # =========================================================================
    # CLINICAL ALERT DETECTION
    # =========================================================================
    
    def detect_clinical_alerts(self, age: int, sex: str) -> List[dict]:
        """Detect all clinical alerts based on test results."""
        alerts = []
        
        # Memory retention concern
        if self.memory_retention_flag:
            self.memory_deficit_flag = True
            alerts.append({
                'code': 'LOW_MEMORY_RETENTION',
                'level': 'high',
                'message': f'Low memory retention ({self.memory_retention_pct}%) - Hippocampal function concern',
                'value': float(self.memory_retention_pct) if self.memory_retention_pct else 0,
            })
        
        # DSST very low
        if self.dsst_score is not None:
            score = self.dsst_score
            threshold = 45 if age < 50 else (35 if age < 70 else 25)
            if score < threshold:
                self.cognitive_concern_flag = True
                alerts.append({
                    'code': 'LOW_DSST',
                    'level': 'moderate',
                    'message': f'Low processing speed (DSST: {score}) - Consider cognitive evaluation',
                    'value': score,
                })
        
        # B/A ratio
        if self.trails_ba_ratio is not None:
            ratio = float(self.trails_ba_ratio)
            if ratio > 3.5:
                self.executive_dysfunction_flag = True
                alerts.append({
                    'code': 'HIGH_BA_RATIO',
                    'level': 'high',
                    'message': f'High B/A ratio ({ratio:.1f}) - Executive dysfunction indicated',
                    'value': ratio,
                })
        
        # Digit span
        if self.digit_span_total is not None and self.digit_span_total < 10:
            self.memory_deficit_flag = True
            alerts.append({
                'code': 'LOW_DIGIT_SPAN',
                'level': 'moderate',
                'message': f'Low digit span ({self.digit_span_total}) - Working memory deficit',
                'value': self.digit_span_total,
            })
        
        # Clock drawing severe issues
        if self.clock_score_raw is not None and self.clock_score_raw <= 3:
            self.cognitive_concern_flag = True
            alerts.append({
                'code': 'CLOCK_DRAWING_CONCERN',
                'level': 'high',
                'message': f'Significant clock drawing errors ({self.clock_score_raw}/7) - Visuospatial/executive concern',
                'value': self.clock_score_raw,
            })
        
        # Verbal fluency
        if self.verbal_fluency_animals is not None and self.verbal_fluency_animals < 12:
            self.language_concern_flag = True
            alerts.append({
                'code': 'LOW_VERBAL_FLUENCY',
                'level': 'moderate',
                'message': f'Low verbal fluency ({self.verbal_fluency_animals} animals)',
                'value': self.verbal_fluency_animals,
            })
        
        # PHQ-2 Depression
        if self.phq2_urgent_flag:
            self.depression_flag = True
            alerts.append({
                'code': 'PHQ2_URGENT',
                'level': 'urgent',
                'message': f'URGENT: PHQ-2 score {self.phq2_total}/6 - Immediate mental health referral needed',
                'value': self.phq2_total,
            })
        elif self.phq2_followup_flag:
            self.depression_flag = True
            alerts.append({
                'code': 'PHQ2_ELEVATED',
                'level': 'high',
                'message': f'PHQ-2 score {self.phq2_total}/6 - Full PHQ-9 evaluation recommended',
                'value': self.phq2_total,
            })
        
        # GAD-2 Anxiety
        if self.gad2_urgent_flag:
            self.anxiety_flag = True
            alerts.append({
                'code': 'GAD2_URGENT',
                'level': 'urgent',
                'message': f'URGENT: GAD-2 score {self.gad2_total}/6 - Immediate mental health referral needed',
                'value': self.gad2_total,
            })
        elif self.gad2_followup_flag:
            self.anxiety_flag = True
            alerts.append({
                'code': 'GAD2_ELEVATED',
                'level': 'high',
                'message': f'GAD-2 score {self.gad2_total}/6 - Full GAD-7 evaluation recommended',
                'value': self.gad2_total,
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
            # Memory
            'memory_immediate_count': self.memory_immediate_count,
            'memory_immediate_points': float(self.memory_immediate_points) if self.memory_immediate_points else None,
            'memory_delayed_count': self.memory_delayed_count,
            'memory_delayed_points': float(self.memory_delayed_points) if self.memory_delayed_points else None,
            'memory_retention_pct': float(self.memory_retention_pct) if self.memory_retention_pct else None,
            # Digit Span
            'digit_span_forward': self.digit_span_forward,
            'digit_span_forward_points': float(self.digit_span_forward_points) if self.digit_span_forward_points else None,
            'digit_span_backward': self.digit_span_backward,
            'digit_span_backward_points': float(self.digit_span_backward_points) if self.digit_span_backward_points else None,
            'digit_span_total': self.digit_span_total,
            'digit_span_points': float(self.digit_span_points) if self.digit_span_points else None,
            # Trails
            'trails_a_time': float(self.trails_a_time) if self.trails_a_time else None,
            'trails_a_points': float(self.trails_a_points) if self.trails_a_points else None,
            'trails_b_time': float(self.trails_b_time) if self.trails_b_time else None,
            'trails_b_points': float(self.trails_b_points) if self.trails_b_points else None,
            'trails_ba_ratio': float(self.trails_ba_ratio) if self.trails_ba_ratio else None,
            # DSST
            'dsst_score': self.dsst_score,
            'dsst_points': float(self.dsst_points) if self.dsst_points else None,
            # Clock
            'clock_score_raw': self.clock_score_raw,
            'clock_points': float(self.clock_points) if self.clock_points else None,
            # Verbal Fluency
            'verbal_fluency_animals': self.verbal_fluency_animals,
            'verbal_fluency_points': float(self.verbal_fluency_points) if self.verbal_fluency_points else None,
            # Mental Health
            'phq2_total': self.phq2_total,
            'phq2_points': float(self.phq2_points) if self.phq2_points else None,
            'gad2_total': self.gad2_total,
            'gad2_points': float(self.gad2_points) if self.gad2_points else None,
            # Totals
            'pillar2_total': float(self.pillar2_total) if self.pillar2_total else None,
            'pillar2_pct': float(self.pillar2_pct) if self.pillar2_pct else None,
            'pillar2_category': self.pillar2_category,
            'functional_age_modifier': float(self.functional_age_modifier) if self.functional_age_modifier else None,
            # Alerts
            'clinical_alerts': self.clinical_alerts,
        }
