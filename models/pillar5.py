"""
Pillar 5 Model - Disease Prevention & Clinical Biomarkers
==========================================================

9 test components with scoring and clinical alerts.
Maximum 20 points total.
Most comprehensive pillar with dynamic cancer screening.
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


class Pillar5Results(Base):
    """
    Pillar 5: Disease Prevention & Clinical Biomarkers
    
    9 Test Components (20 points total):
    1. Standard Lipid Panel (4 pts) - LDL, HDL, TG, Ratio
    2. Advanced Lipids (2 pts) - ApoB, Lp(a)
    3. Cardiac Imaging (3 pts) - CAC, TMT, Echo/CT
    4. Kidney Function (2 pts) - Creatinine → eGFR
    5. Cancer Screening (4 pts) - Dynamic compliance
    6. Organ Imaging (2 pts) - Abdomen, Chest
    7. Bone Health (1 pt) - DEXA T-score
    8. Sensory (1 pt) - Vision + Hearing
    9. Chronic Disease (1 pt) - Management status
    
    Green gradient theme: #16a085 to #27ae60
    """
    
    __tablename__ = 'pillar_5_results'
    
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
    # TEST 1: STANDARD LIPID PANEL (4 points)
    # =========================================================================
    
    lipids_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    
    # Exact values
    ldl_cholesterol: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL
    hdl_cholesterol: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL
    triglycerides: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL
    total_cholesterol: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL (auto-calculated)
    total_hdl_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)  # Auto-calculated
    
    # Category mode
    lipids_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Scoring
    ldl_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    hdl_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    triglycerides_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    ratio_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    lipids_total_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    lipids_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 2: ADVANCED LIPIDS (2 points)
    # =========================================================================
    
    apob: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL
    lp_a: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mg/dL
    apob_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    lp_a_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    advanced_lipids_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    # =========================================================================
    # TEST 3: CARDIAC IMAGING (3 points)
    # =========================================================================
    
    cac_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 1), nullable=True)  # Agatston score
    cac_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cac_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    tmt_performed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    tmt_result: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # negative/positive/abnormal/notPerformed
    tmt_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    echo_ct_performed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    echo_ct_result: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # normal/mild/moderate/severe/notPerformed
    echo_ct_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    cardiac_imaging_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    # =========================================================================
    # TEST 4: KIDNEY FUNCTION (2 points)
    # =========================================================================
    
    kidney_input_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'exact' or 'category'
    creatinine: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)  # mg/dL
    egfr: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 1), nullable=True)  # mL/min/1.73m² (auto-calculated)
    kidney_category_input: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    kidney_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    kidney_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 5: CANCER SCREENING (4 points) - Dynamic
    # =========================================================================
    
    # Screening completion (checkboxes)
    screening_colonoscopy: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    screening_mammogram: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    screening_pap_hpv: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    screening_ldct: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)  # Lung CT for smokers
    screening_psa: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    screening_skin: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # Calculated fields
    screening_recommended_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    screening_completed_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    screening_compliance_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    screening_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    # =========================================================================
    # TEST 6: ORGAN IMAGING (2 points)
    # =========================================================================
    
    abdomen_imaging: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # normal/abnormal/notPerformed
    abdomen_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    chest_imaging: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # normal/abnormal/notPerformed
    chest_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    organ_imaging_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    # =========================================================================
    # TEST 7: BONE HEALTH (1 point)
    # =========================================================================
    
    dexa_performed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    dexa_t_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)  # T-score
    bone_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    bone_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # =========================================================================
    # TEST 8: SENSORY HEALTH (1 point)
    # =========================================================================
    
    vision_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # excellent/good/fair/poor
    vision_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    hearing_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # excellent/good/fair/poor
    hearing_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    sensory_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TEST 9: CHRONIC DISEASE MANAGEMENT (1 point)
    # =========================================================================
    
    has_chronic_disease: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    chronic_disease_list: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # Comma-separated
    disease_management: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # excellent/good/fair/poor/none
    chronic_disease_points: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    
    # =========================================================================
    # TOTALS & CLINICAL FLAGS
    # =========================================================================
    
    pillar5_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    pillar5_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    pillar5_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    functional_age_modifier: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    
    clinical_alerts: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Clinical flags (9 total)
    high_ldl_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    low_hdl_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    high_triglycerides_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    high_cac_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    ckd_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    screening_overdue_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    osteoporosis_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    sensory_impairment_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    uncontrolled_disease_flag: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="pillar5_results",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Pillar5Results(id={self.id}, assessment_id={self.assessment_id}, "
            f"total={self.pillar5_total}/20, category={self.pillar5_category})>"
        )
    
    # =========================================================================
    # AUTO-CALCULATIONS
    # =========================================================================
    
    def calculate_total_cholesterol(self) -> None:
        """Calculate total cholesterol from LDL + HDL + (TG/5)."""
        if self.ldl_cholesterol and self.hdl_cholesterol and self.triglycerides:
            total = float(self.ldl_cholesterol) + float(self.hdl_cholesterol) + (float(self.triglycerides) / 5)
            self.total_cholesterol = Decimal(str(round(total, 1)))
    
    def calculate_total_hdl_ratio(self) -> None:
        """Calculate Total/HDL ratio."""
        if self.total_cholesterol and self.hdl_cholesterol and float(self.hdl_cholesterol) > 0:
            ratio = float(self.total_cholesterol) / float(self.hdl_cholesterol)
            self.total_hdl_ratio = Decimal(str(round(ratio, 2)))
    
    def calculate_egfr(self, age: int, sex: str, race: str = 'other') -> None:
        """
        Calculate eGFR using CKD-EPI 2021 equation (race-free).
        
        Args:
            age: Patient age in years
            sex: 'male' or 'female'
            race: Not used in 2021 equation (race-free)
        """
        if not self.creatinine:
            return
        
        cr = float(self.creatinine)
        
        # CKD-EPI 2021 equation (race-free)
        if sex == 'female':
            kappa = 0.7
            alpha = -0.241
            if cr <= kappa:
                egfr = 142 * ((cr / kappa) ** alpha) * (0.9938 ** age)
            else:
                egfr = 142 * ((cr / kappa) ** -1.200) * (0.9938 ** age)
        else:  # male
            kappa = 0.9
            alpha = -0.302
            if cr <= kappa:
                egfr = 142 * ((cr / kappa) ** alpha) * (0.9938 ** age)
            else:
                egfr = 142 * ((cr / kappa) ** -1.200) * (0.9938 ** age)
        
        self.egfr = Decimal(str(round(egfr, 1)))
    
    def calculate_screening_compliance(self) -> None:
        """Calculate cancer screening compliance percentage."""
        if self.screening_recommended_count and self.screening_recommended_count > 0:
            completed = self.screening_completed_count or 0
            compliance = (completed / self.screening_recommended_count) * 100
            self.screening_compliance_pct = Decimal(str(round(compliance, 2)))
    
    # =========================================================================
    # TOTAL SCORE CALCULATION
    # =========================================================================
    
    def calculate_pillar5_total(self) -> Decimal:
        """
        Calculate total Pillar 5 score (sum of all 9 test components).
        
        Max 20 points.
        """
        scores = [
            self.lipids_total_points,
            self.advanced_lipids_points,
            self.cardiac_imaging_points,
            self.kidney_points,
            self.screening_points,
            self.organ_imaging_points,
            self.bone_points,
            self.sensory_points,
            self.chronic_disease_points,
        ]
        
        valid_scores = [float(s) for s in scores if s is not None]
        total = sum(valid_scores)
        
        self.pillar5_total = Decimal(str(round(total, 1)))
        self.pillar5_pct = Decimal(str(round((total / 20) * 100, 2)))
        self.pillar5_category = self._categorize_total(total)
        
        return self.pillar5_total
    
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
        Calculate disease prevention impact on functional age.
        
        Score ranges:
        - 18-20 (90-100%): -2 years
        - 16-17.9 (80-89%): -1 year
        - 14-15.9 (70-79%): 0 years
        - 12-13.9 (60-69%): +1 year
        - 10-11.9 (50-59%): +2 years
        - <10 (<50%): +3 years
        """
        if self.pillar5_total is None:
            return Decimal('0')
        
        total = float(self.pillar5_total)
        
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
        
        # High LDL
        if self.ldl_cholesterol and float(self.ldl_cholesterol) >= 130:
            self.high_ldl_flag = True
            if float(self.ldl_cholesterol) >= 160:
                alerts.append({
                    'code': 'LDL_VERY_HIGH',
                    'level': 'high',
                    'message': 'Very high LDL cholesterol. Statin therapy recommended.',
                })
            else:
                alerts.append({
                    'code': 'LDL_HIGH',
                    'level': 'moderate',
                    'message': 'High LDL cholesterol. Lifestyle modifications and consider statin.',
                })
        
        # Low HDL
        if self.hdl_cholesterol:
            hdl = float(self.hdl_cholesterol)
            if hdl < 40:
                self.low_hdl_flag = True
                alerts.append({
                    'code': 'HDL_LOW',
                    'level': 'moderate',
                    'message': 'Low HDL cholesterol. Increase aerobic exercise and consider niacin.',
                })
        
        # High triglycerides
        if self.triglycerides and float(self.triglycerides) >= 150:
            self.high_triglycerides_flag = True
            if float(self.triglycerides) >= 500:
                alerts.append({
                    'code': 'TRIGLYCERIDES_SEVERE',
                    'level': 'urgent',
                    'message': 'URGENT: Very high triglycerides. Pancreatitis risk. Immediate treatment needed.',
                })
            else:
                alerts.append({
                    'code': 'TRIGLYCERIDES_HIGH',
                    'level': 'moderate',
                    'message': 'High triglycerides. Weight loss, exercise, and consider fibrate or omega-3.',
                })
        
        # High CAC
        if self.cac_score:
            cac = float(self.cac_score)
            if cac >= 100:
                self.high_cac_flag = True
                if cac >= 400:
                    alerts.append({
                        'code': 'CAC_EXTENSIVE',
                        'level': 'high',
                        'message': 'Extensive coronary calcification. High CV risk. Aggressive risk factor management.',
                    })
                else:
                    alerts.append({
                        'code': 'CAC_MODERATE',
                        'level': 'moderate',
                        'message': 'Moderate coronary calcification. Statin and aspirin recommended.',
                    })
        
        # Chronic kidney disease
        if self.egfr:
            egfr_val = float(self.egfr)
            if egfr_val < 60:
                self.ckd_flag = True
                if egfr_val < 30:
                    alerts.append({
                        'code': 'CKD_SEVERE',
                        'level': 'urgent',
                        'message': 'URGENT: Severe CKD (Stage 3B or worse). Nephrology referral needed.',
                    })
                else:
                    alerts.append({
                        'code': 'CKD_MODERATE',
                        'level': 'high',
                        'message': 'Moderate CKD. Monitor kidney function, adjust medications.',
                    })
        
        # Screening overdue
        if self.screening_compliance_pct and float(self.screening_compliance_pct) < 70:
            self.screening_overdue_flag = True
            alerts.append({
                'code': 'SCREENING_OVERDUE',
                'level': 'moderate',
                'message': 'Cancer screening overdue. Schedule recommended screenings.',
            })
        
        # Osteoporosis
        if self.dexa_t_score and float(self.dexa_t_score) <= -2.5:
            self.osteoporosis_flag = True
            alerts.append({
                'code': 'OSTEOPOROSIS',
                'level': 'high',
                'message': 'Osteoporosis detected. Bisphosphonate therapy and calcium/vitamin D supplementation recommended.',
            })
        
        # Sensory impairment
        if self.vision_status in ['poor'] or self.hearing_status in ['poor']:
            self.sensory_impairment_flag = True
            alerts.append({
                'code': 'SENSORY_IMPAIRMENT',
                'level': 'moderate',
                'message': 'Significant sensory impairment. Ophthalmology/audiology referral recommended.',
            })
        
        # Uncontrolled chronic disease
        if self.has_chronic_disease and self.disease_management in ['poor', 'none']:
            self.uncontrolled_disease_flag = True
            alerts.append({
                'code': 'UNCONTROLLED_DISEASE',
                'level': 'high',
                'message': 'Chronic disease poorly controlled. Review and optimize treatment plan.',
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
            # Lipids
            'lipids_input_mode': self.lipids_input_mode,
            'ldl_cholesterol': float(self.ldl_cholesterol) if self.ldl_cholesterol else None,
            'hdl_cholesterol': float(self.hdl_cholesterol) if self.hdl_cholesterol else None,
            'triglycerides': float(self.triglycerides) if self.triglycerides else None,
            'total_cholesterol': float(self.total_cholesterol) if self.total_cholesterol else None,
            'total_hdl_ratio': float(self.total_hdl_ratio) if self.total_hdl_ratio else None,
            'lipids_category_input': self.lipids_category_input,
            'ldl_points': float(self.ldl_points) if self.ldl_points else None,
            'hdl_points': float(self.hdl_points) if self.hdl_points else None,
            'triglycerides_points': float(self.triglycerides_points) if self.triglycerides_points else None,
            'ratio_points': float(self.ratio_points) if self.ratio_points else None,
            'lipids_total_points': float(self.lipids_total_points) if self.lipids_total_points else None,
            'lipids_category': self.lipids_category,
            # Advanced Lipids
            'apob': float(self.apob) if self.apob else None,
            'lp_a': float(self.lp_a) if self.lp_a else None,
            'apob_points': float(self.apob_points) if self.apob_points else None,
            'lp_a_points': float(self.lp_a_points) if self.lp_a_points else None,
            'advanced_lipids_points': float(self.advanced_lipids_points) if self.advanced_lipids_points else None,
            # Cardiac Imaging
            'cac_score': float(self.cac_score) if self.cac_score else None,
            'cac_category': self.cac_category,
            'cac_points': float(self.cac_points) if self.cac_points else None,
            'tmt_performed': self.tmt_performed,
            'tmt_result': self.tmt_result,
            'tmt_points': float(self.tmt_points) if self.tmt_points else None,
            'echo_ct_performed': self.echo_ct_performed,
            'echo_ct_result': self.echo_ct_result,
            'echo_ct_points': float(self.echo_ct_points) if self.echo_ct_points else None,
            'cardiac_imaging_points': float(self.cardiac_imaging_points) if self.cardiac_imaging_points else None,
            # Kidney
            'kidney_input_mode': self.kidney_input_mode,
            'creatinine': float(self.creatinine) if self.creatinine else None,
            'egfr': float(self.egfr) if self.egfr else None,
            'kidney_category_input': self.kidney_category_input,
            'kidney_points': float(self.kidney_points) if self.kidney_points else None,
            'kidney_category': self.kidney_category,
            # Cancer Screening
            'screening_colonoscopy': self.screening_colonoscopy,
            'screening_mammogram': self.screening_mammogram,
            'screening_pap_hpv': self.screening_pap_hpv,
            'screening_ldct': self.screening_ldct,
            'screening_psa': self.screening_psa,
            'screening_skin': self.screening_skin,
            'screening_recommended_count': self.screening_recommended_count,
            'screening_completed_count': self.screening_completed_count,
            'screening_compliance_pct': float(self.screening_compliance_pct) if self.screening_compliance_pct else None,
            'screening_points': float(self.screening_points) if self.screening_points else None,
            # Organ Imaging
            'abdomen_imaging': self.abdomen_imaging,
            'abdomen_points': float(self.abdomen_points) if self.abdomen_points else None,
            'chest_imaging': self.chest_imaging,
            'chest_points': float(self.chest_points) if self.chest_points else None,
            'organ_imaging_points': float(self.organ_imaging_points) if self.organ_imaging_points else None,
            # Bone
            'dexa_performed': self.dexa_performed,
            'dexa_t_score': float(self.dexa_t_score) if self.dexa_t_score else None,
            'bone_points': float(self.bone_points) if self.bone_points else None,
            'bone_category': self.bone_category,
            # Sensory
            'vision_status': self.vision_status,
            'vision_points': float(self.vision_points) if self.vision_points else None,
            'hearing_status': self.hearing_status,
            'hearing_points': float(self.hearing_points) if self.hearing_points else None,
            'sensory_points': float(self.sensory_points) if self.sensory_points else None,
            # Chronic Disease
            'has_chronic_disease': self.has_chronic_disease,
            'chronic_disease_list': self.chronic_disease_list,
            'disease_management': self.disease_management,
            'chronic_disease_points': float(self.chronic_disease_points) if self.chronic_disease_points else None,
            # Totals
            'pillar5_total': float(self.pillar5_total) if self.pillar5_total else None,
            'pillar5_pct': float(self.pillar5_pct) if self.pillar5_pct else None,
            'pillar5_category': self.pillar5_category,
            'functional_age_modifier': float(self.functional_age_modifier) if self.functional_age_modifier else None,
            # Alerts
            'clinical_alerts': self.clinical_alerts,
            'high_ldl_flag': self.high_ldl_flag,
            'low_hdl_flag': self.low_hdl_flag,
            'high_triglycerides_flag': self.high_triglycerides_flag,
            'high_cac_flag': self.high_cac_flag,
            'ckd_flag': self.ckd_flag,
            'screening_overdue_flag': self.screening_overdue_flag,
            'osteoporosis_flag': self.osteoporosis_flag,
            'sensory_impairment_flag': self.sensory_impairment_flag,
            'uncontrolled_disease_flag': self.uncontrolled_disease_flag,
        }
