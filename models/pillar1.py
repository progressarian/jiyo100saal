"""
Pillar 1 Model - Movement & Strength
=====================================

All 8 physical performance tests with scoring and clinical alerts.
Maximum 20 points total (22 with balance bonus).
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


class Pillar1Results(Base):
    """
    Pillar 1: Movement & Strength Assessment
    
    8 Tests (20 points total + 0.5 bonus):
    1. 30-Second Chair Stand (3 pts)
    2. Grip Strength (3 pts)
    3. 4-Meter Gait Speed (2 pts)
    4. Balance Assessment (2.5 pts + 0.5 bonus)
    5. Timed Up and Go (2 pts)
    6. VO2 Max (4 pts)
    7. Sit-and-Reach Flexibility (2 pts)
    8. 6-Minute Walk Test (3 pts)
    """
    
    __tablename__ = 'pillar_1_results'
    
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
    # TEST 1: 30-SECOND CHAIR STAND (3 points max)
    # =========================================================================
    
    chair_stand_reps: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # Count in 30 seconds
    
    chair_stand_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )  # 0.5-3.0 pts
    
    chair_stand_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # =========================================================================
    # TEST 2: GRIP STRENGTH (3 points max)
    # =========================================================================
    
    grip_dominant_hand: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )  # 'left' or 'right'
    
    # Left hand trials
    grip_left_1: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    grip_left_2: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    grip_left_3: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    grip_left_best: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    
    # Right hand trials
    grip_right_1: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    grip_right_2: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    grip_right_3: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    grip_right_best: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    
    # Dominant hand best (used for scoring)
    grip_dominant_best: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    grip_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    grip_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    grip_asymmetry_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )  # Flag if >10%
    
    # =========================================================================
    # TEST 3: 4-METER GAIT SPEED (2 points max)
    # =========================================================================
    
    gait_trial_1_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    gait_trial_2_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    gait_faster_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )  # Calculated
    
    gait_speed_ms: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )  # Calculated m/s
    
    gait_walking_aid: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    
    gait_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    gait_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # =========================================================================
    # TEST 4: BALANCE (2.5 points + 0.5 bonus = 3.0 max)
    # =========================================================================
    
    # Romberg (pass/fail clinical indicator - no points)
    romberg_eyes_open: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    romberg_eyes_closed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Eyes closed timed (0.5 pts max)
    eyes_closed_time_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )  # Max 30 sec
    
    eyes_closed_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        nullable=True,
    )  # 0.1-0.5 pts
    
    # Single-leg stance - LEFT
    single_leg_left_1: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    single_leg_left_2: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    single_leg_left_3: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    single_leg_left_best: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    
    # Single-leg stance - RIGHT
    single_leg_right_1: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    single_leg_right_2: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    single_leg_right_3: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    single_leg_right_best: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    
    # BETTER leg best time (used for scoring)
    single_leg_better_best: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    single_leg_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )  # 0.1-1.5 pts
    
    single_leg_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # Tandem stand (0.5 pts bonus - OPTIONAL)
    tandem_stand_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    tandem_stand_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        nullable=True,
    )  # 0-0.5 pts
    
    # Balance totals
    balance_total_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )  # 0-2.5 (or 3.0 with bonus)
    
    balance_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # =========================================================================
    # TEST 5: TIMED UP AND GO (2 points max)
    # =========================================================================
    
    tug_trial_1_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    tug_trial_2_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    tug_faster_sec: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    tug_walking_aid: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    
    # Qualitative modifiers
    tug_unsteady_gait: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    tug_unsteady_turn: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    tug_used_arms: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    tug_plopped_down: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    tug_base_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    tug_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    tug_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # =========================================================================
    # TEST 6: VO2 MAX (4 points max)
    # =========================================================================
    
    vo2_method: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'direct', 'submaximal', 'non_exercise'
    
    vo2_direct_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    vo2_bruce_time_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    vo2_resting_hr: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vo2_pa_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-7
    
    vo2_max: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )  # Final value used
    
    vo2_max_hr_achieved: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vo2_max_hr_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vo2_test_stopped_reason: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    vo2_percentile: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    vo2_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    vo2_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    vo2_mets: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
    )
    
    # =========================================================================
    # TEST 7: SIT-AND-REACH FLEXIBILITY (2 points max)
    # =========================================================================
    
    flexibility_method: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )  # 'standard' or 'chair'
    
    flexibility_trial_1_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    flexibility_trial_2_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    flexibility_trial_3_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    flexibility_best_cm: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    
    flexibility_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    flexibility_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # =========================================================================
    # TEST 8: 6-MINUTE WALK TEST (3 points max)
    # =========================================================================
    
    walk_6min_laps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_partial_m: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
    )
    walk_6min_total_m: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_walking_aid: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    walk_6min_stops: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # HR and O2 monitoring
    walk_6min_hr_pre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_hr_post: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_o2_sat_pre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_o2_sat_post: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_o2_desat: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Expected and % predicted
    walk_6min_expected_m: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walk_6min_pct_predicted: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    
    walk_6min_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
    )
    
    walk_6min_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    # =========================================================================
    # TOTALS & CLINICAL ALERTS
    # =========================================================================
    
    pillar1_total: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
    )  # Sum of all tests (0-20, up to 20.5 with bonus)
    
    pillar1_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )  # Percentage
    
    pillar1_category: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    
    functional_age_impact: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )  # +/- years
    
    # Clinical alerts stored as JSON array
    clinical_alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Individual alert flags
    sarcopenia_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fall_risk_flag: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # 'low', 'moderate', 'high', 'very_high'
    severe_limitation_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    low_vo2_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="pillar1_results",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Pillar1Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"total={self.pillar1_total}/20, category={self.pillar1_category})>"
        )
    
    # =========================================================================
    # CALCULATED BEST VALUES
    # =========================================================================
    
    def calculate_grip_best(self) -> None:
        """Calculate best grip for each hand and dominant hand."""
        # Left hand best
        left_trials = [self.grip_left_1, self.grip_left_2, self.grip_left_3]
        left_valid = [float(t) for t in left_trials if t is not None]
        if left_valid:
            self.grip_left_best = Decimal(str(max(left_valid)))
        
        # Right hand best
        right_trials = [self.grip_right_1, self.grip_right_2, self.grip_right_3]
        right_valid = [float(t) for t in right_trials if t is not None]
        if right_valid:
            self.grip_right_best = Decimal(str(max(right_valid)))
        
        # Dominant hand best
        if self.grip_dominant_hand == 'left' and self.grip_left_best:
            self.grip_dominant_best = self.grip_left_best
        elif self.grip_dominant_hand == 'right' and self.grip_right_best:
            self.grip_dominant_best = self.grip_right_best
        elif self.grip_left_best and self.grip_right_best:
            # If dominant not specified, use higher
            self.grip_dominant_best = max(self.grip_left_best, self.grip_right_best)
        
        # Calculate asymmetry
        if self.grip_left_best and self.grip_right_best:
            left = float(self.grip_left_best)
            right = float(self.grip_right_best)
            diff = abs(left - right)
            avg = (left + right) / 2
            if avg > 0:
                self.grip_asymmetry_pct = Decimal(str(round((diff / avg) * 100, 1)))
    
    def calculate_gait_speed(self) -> None:
        """Calculate gait speed from trial times."""
        times = [self.gait_trial_1_sec, self.gait_trial_2_sec]
        valid_times = [float(t) for t in times if t is not None]
        
        if valid_times:
            faster = min(valid_times)
            self.gait_faster_sec = Decimal(str(faster))
            # Speed = 4 meters / time
            speed = 4.0 / faster
            self.gait_speed_ms = Decimal(str(round(speed, 2)))
    
    def calculate_single_leg_best(self) -> None:
        """Calculate best single-leg stance time for each leg and better leg."""
        # Left leg best
        left_trials = [self.single_leg_left_1, self.single_leg_left_2, self.single_leg_left_3]
        left_valid = [float(t) for t in left_trials if t is not None]
        if left_valid:
            self.single_leg_left_best = Decimal(str(max(left_valid)))
        
        # Right leg best
        right_trials = [self.single_leg_right_1, self.single_leg_right_2, self.single_leg_right_3]
        right_valid = [float(t) for t in right_trials if t is not None]
        if right_valid:
            self.single_leg_right_best = Decimal(str(max(right_valid)))
        
        # BETTER leg (use for scoring per spec)
        if self.single_leg_left_best and self.single_leg_right_best:
            self.single_leg_better_best = max(self.single_leg_left_best, self.single_leg_right_best)
        elif self.single_leg_left_best:
            self.single_leg_better_best = self.single_leg_left_best
        elif self.single_leg_right_best:
            self.single_leg_better_best = self.single_leg_right_best
    
    def calculate_tug_faster(self) -> None:
        """Calculate faster TUG time."""
        times = [self.tug_trial_1_sec, self.tug_trial_2_sec]
        valid_times = [float(t) for t in times if t is not None]
        
        if valid_times:
            self.tug_faster_sec = Decimal(str(min(valid_times)))
    
    def calculate_flexibility_best(self) -> None:
        """Calculate best flexibility measurement."""
        trials = [self.flexibility_trial_1_cm, self.flexibility_trial_2_cm, self.flexibility_trial_3_cm]
        valid = [float(t) for t in trials if t is not None]
        
        if valid:
            self.flexibility_best_cm = Decimal(str(max(valid)))
    
    def calculate_6min_walk_distance(self, course_length_m: int = 30) -> None:
        """Calculate total 6-minute walk distance."""
        if self.walk_6min_laps is not None:
            total = self.walk_6min_laps * course_length_m
            if self.walk_6min_partial_m:
                total += float(self.walk_6min_partial_m)
            self.walk_6min_total_m = int(total)
    
    def calculate_vo2_mets(self) -> None:
        """Calculate METs from VO2 max (1 MET = 3.5 mL/kg/min)."""
        if self.vo2_max:
            mets = float(self.vo2_max) / 3.5
            self.vo2_mets = Decimal(str(round(mets, 1)))
    
    # =========================================================================
    # TOTAL SCORE CALCULATION
    # =========================================================================
    
    def calculate_pillar1_total(self) -> Decimal:
        """
        Calculate total Pillar 1 score (sum of all 8 tests).
        
        Max 20 points (or 20.5 with tandem bonus).
        """
        scores = [
            self.chair_stand_score,
            self.grip_score,
            self.gait_score,
            self.balance_total_score,
            self.tug_score,
            self.vo2_score,
            self.flexibility_score,
            self.walk_6min_score,
        ]
        
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        
        self.pillar1_total = Decimal(str(round(total, 2)))
        self.pillar1_pct = Decimal(str(round((total / 20) * 100, 2)))
        self.pillar1_category = self._categorize_total(total)
        
        return self.pillar1_total
    
    def _categorize_total(self, total: float) -> str:
        """Categorize total score."""
        pct = (total / 20) * 100
        
        if pct >= 92.5:
            return 'Excellent'
        elif pct >= 82.5:
            return 'Very Good'
        elif pct >= 72.5:
            return 'Good'
        elif pct >= 60:
            return 'Fair'
        elif pct >= 45:
            return 'Below Average'
        elif pct >= 30:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def calculate_functional_age_impact(self) -> int:
        """
        Calculate functional age impact based on Pillar 1 score.
        
        Per spec:
        - 92.5-100%: -3 to -5 years
        - 82.5-92%: -1 to -2 years
        - 72.5-82%: 0 years
        - 60-72%: +1 to +2 years
        - 45-60%: +3 to +4 years
        - 30-45%: +5 to +7 years
        - <30%: +8 to +10 years
        """
        if self.pillar1_pct is None:
            return 0
        
        pct = float(self.pillar1_pct)
        
        if pct >= 92.5:
            impact = -4  # Average of -3 to -5
        elif pct >= 82.5:
            impact = -2  # Average of -1 to -2
        elif pct >= 72.5:
            impact = 0
        elif pct >= 60:
            impact = 2  # Average of +1 to +2
        elif pct >= 45:
            impact = 4  # Average of +3 to +4
        elif pct >= 30:
            impact = 6  # Average of +5 to +7
        else:
            impact = 9  # Average of +8 to +10
        
        self.functional_age_impact = impact
        return impact
    
    # =========================================================================
    # CLINICAL ALERT DETECTION
    # =========================================================================
    
    def detect_clinical_alerts(self, age: int, sex: str) -> List[dict]:
        """
        Detect all clinical alerts based on test results.
        
        Returns list of alert dictionaries.
        """
        alerts = []
        
        # Sarcopenia check
        if self.grip_dominant_best:
            grip = float(self.grip_dominant_best)
            if (sex == 'male' and grip < 27) or (sex == 'female' and grip < 16):
                self.sarcopenia_flag = True
                alerts.append({
                    'code': 'SARCOPENIA',
                    'level': 'high',
                    'message': f'Low grip strength ({grip} kg) indicates possible sarcopenia',
                    'threshold': 27 if sex == 'male' else 16,
                    'value': grip,
                })
        
        # Fall risk assessment
        fall_risk_factors = 0
        
        if self.gait_speed_ms and float(self.gait_speed_ms) < 0.8:
            fall_risk_factors += 1
        
        if self.single_leg_better_best and age >= 65:
            if float(self.single_leg_better_best) < 5:
                fall_risk_factors += 1
        
        if self.tug_faster_sec and float(self.tug_faster_sec) > 20:
            fall_risk_factors += 1
        
        if fall_risk_factors >= 3:
            self.fall_risk_flag = 'very_high'
            alerts.append({
                'code': 'FALL_RISK_VERY_HIGH',
                'level': 'urgent',
                'message': 'Very high fall risk (gait <0.8, balance <5s, TUG >20s)',
                'factors': fall_risk_factors,
            })
        elif fall_risk_factors >= 2:
            self.fall_risk_flag = 'high'
            alerts.append({
                'code': 'FALL_RISK_HIGH',
                'level': 'high',
                'message': 'High fall risk identified',
                'factors': fall_risk_factors,
            })
        elif fall_risk_factors >= 1:
            self.fall_risk_flag = 'moderate'
        else:
            self.fall_risk_flag = 'low'
        
        # Severe functional limitation
        if self.chair_stand_reps is not None:
            reps = self.chair_stand_reps
            if (age < 70 and reps < 8) or (age >= 70 and reps < 5):
                self.severe_limitation_flag = True
                alerts.append({
                    'code': 'SEVERE_FUNCTIONAL_LIMITATION',
                    'level': 'high',
                    'message': f'Very low chair stand count ({reps} reps) indicates severe functional limitation',
                    'value': reps,
                })
        
        # Very low VO2 max
        if self.vo2_max and float(self.vo2_max) < 20:
            self.low_vo2_flag = True
            alerts.append({
                'code': 'VERY_LOW_VO2',
                'level': 'high',
                'message': f'Very low VO2 max ({self.vo2_max} mL/kg/min) indicates high mortality risk',
                'value': float(self.vo2_max),
            })
        
        # Very poor gait speed
        if self.gait_speed_ms and age >= 65:
            speed = float(self.gait_speed_ms)
            if speed < 0.6:
                alerts.append({
                    'code': 'VERY_LOW_GAIT_SPEED',
                    'level': 'urgent',
                    'message': f'Very slow gait speed ({speed} m/s) indicates severe mobility limitation',
                    'value': speed,
                })
        
        # 6MWT very low
        if self.walk_6min_total_m and age >= 65:
            distance = self.walk_6min_total_m
            if distance < 300:
                alerts.append({
                    'code': 'VERY_LOW_6MWT',
                    'level': 'high',
                    'message': f'Very low 6-minute walk distance ({distance}m) indicates poor prognosis',
                    'value': distance,
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
            # Test 1
            'chair_stand_reps': self.chair_stand_reps,
            'chair_stand_score': float(self.chair_stand_score) if self.chair_stand_score else None,
            'chair_stand_category': self.chair_stand_category,
            # Test 2
            'grip_dominant_best': float(self.grip_dominant_best) if self.grip_dominant_best else None,
            'grip_score': float(self.grip_score) if self.grip_score else None,
            'grip_category': self.grip_category,
            'grip_asymmetry_pct': float(self.grip_asymmetry_pct) if self.grip_asymmetry_pct else None,
            # Test 3
            'gait_speed_ms': float(self.gait_speed_ms) if self.gait_speed_ms else None,
            'gait_score': float(self.gait_score) if self.gait_score else None,
            'gait_category': self.gait_category,
            # Test 4
            'single_leg_better_best': float(self.single_leg_better_best) if self.single_leg_better_best else None,
            'balance_total_score': float(self.balance_total_score) if self.balance_total_score else None,
            'balance_category': self.balance_category,
            # Test 5
            'tug_faster_sec': float(self.tug_faster_sec) if self.tug_faster_sec else None,
            'tug_score': float(self.tug_score) if self.tug_score else None,
            'tug_category': self.tug_category,
            # Test 6
            'vo2_max': float(self.vo2_max) if self.vo2_max else None,
            'vo2_score': float(self.vo2_score) if self.vo2_score else None,
            'vo2_category': self.vo2_category,
            'vo2_mets': float(self.vo2_mets) if self.vo2_mets else None,
            # Test 7
            'flexibility_best_cm': float(self.flexibility_best_cm) if self.flexibility_best_cm else None,
            'flexibility_score': float(self.flexibility_score) if self.flexibility_score else None,
            'flexibility_category': self.flexibility_category,
            # Test 8
            'walk_6min_total_m': self.walk_6min_total_m,
            'walk_6min_score': float(self.walk_6min_score) if self.walk_6min_score else None,
            'walk_6min_category': self.walk_6min_category,
            # Totals
            'pillar1_total': float(self.pillar1_total) if self.pillar1_total else None,
            'pillar1_pct': float(self.pillar1_pct) if self.pillar1_pct else None,
            'pillar1_category': self.pillar1_category,
            'functional_age_impact': self.functional_age_impact,
            # Alerts
            'sarcopenia_flag': self.sarcopenia_flag,
            'fall_risk_flag': self.fall_risk_flag,
            'severe_limitation_flag': self.severe_limitation_flag,
            'low_vo2_flag': self.low_vo2_flag,
            'clinical_alerts': self.clinical_alerts,
        }
