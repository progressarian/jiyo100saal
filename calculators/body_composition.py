"""
Body Composition Calculators
============================

All formulas for body composition calculations per spec Part 3.
"""

import math
from decimal import Decimal
from typing import Optional, Tuple


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index.
    
    Formula: BMI = weight (kg) / height (m)²
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        
    Returns:
        BMI value (kg/m²)
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be positive")
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def calculate_lmi(lean_mass_kg: float, height_cm: float) -> float:
    """
    Calculate Lean Mass Index.
    
    Formula: LMI = lean mass (kg) / height (m)²
    
    Args:
        lean_mass_kg: Lean mass in kilograms
        height_cm: Height in centimeters
        
    Returns:
        LMI value (kg/m²)
    """
    if height_cm <= 0 or lean_mass_kg <= 0:
        raise ValueError("Height and lean mass must be positive")
    
    height_m = height_cm / 100
    lmi = lean_mass_kg / (height_m ** 2)
    return round(lmi, 2)


def calculate_asmi(appendicular_lean_mass_kg: float, height_cm: float) -> float:
    """
    Calculate Appendicular Skeletal Muscle Mass Index.
    
    Formula: ASMI = (arms lean mass + legs lean mass) / height (m)²
    
    Args:
        appendicular_lean_mass_kg: Combined lean mass of arms and legs (kg)
        height_cm: Height in centimeters
        
    Returns:
        ASMI value (kg/m²)
    """
    if height_cm <= 0 or appendicular_lean_mass_kg <= 0:
        raise ValueError("Height and lean mass must be positive")
    
    height_m = height_cm / 100
    asmi = appendicular_lean_mass_kg / (height_m ** 2)
    return round(asmi, 2)


def calculate_whr(waist_cm: float, hip_cm: float) -> float:
    """
    Calculate Waist-to-Hip Ratio.
    
    Formula: WHR = waist (cm) / hip (cm)
    
    Args:
        waist_cm: Waist circumference in centimeters
        hip_cm: Hip circumference in centimeters
        
    Returns:
        WHR value (ratio)
    """
    if waist_cm <= 0 or hip_cm <= 0:
        raise ValueError("Waist and hip must be positive")
    
    whr = waist_cm / hip_cm
    return round(whr, 2)


def calculate_body_density_jackson_pollock(
    sum_skinfolds_mm: float,
    age: int,
    sex: str
) -> float:
    """
    Calculate body density using Jackson-Pollock 7-site formula.
    
    Per spec 3.3.2:
    
    Males:
    BD = 1.112 - 0.00043499(sum) + 0.00000055(sum²) - 0.00028826(age)
    
    Females:
    BD = 1.097 - 0.00046971(sum) + 0.00000056(sum²) - 0.00012828(age)
    
    Args:
        sum_skinfolds_mm: Sum of 7 skinfold measurements in millimeters
        age: Age in years
        sex: 'male' or 'female'
        
    Returns:
        Body density (g/cm³)
    """
    if sum_skinfolds_mm <= 0:
        raise ValueError("Sum of skinfolds must be positive")
    if age <= 0:
        raise ValueError("Age must be positive")
    if sex not in ('male', 'female'):
        raise ValueError("Sex must be 'male' or 'female'")
    
    s = sum_skinfolds_mm
    s_squared = s ** 2
    
    if sex == 'male':
        bd = 1.112 - (0.00043499 * s) + (0.00000055 * s_squared) - (0.00028826 * age)
    else:  # female
        bd = 1.097 - (0.00046971 * s) + (0.00000056 * s_squared) - (0.00012828 * age)
    
    return round(bd, 5)


def calculate_body_fat_siri(body_density: float) -> float:
    """
    Calculate body fat percentage from body density using Siri equation.
    
    Formula: Body Fat % = (495 / Body Density) - 450
    
    Args:
        body_density: Body density in g/cm³
        
    Returns:
        Body fat percentage
    """
    if body_density <= 0:
        raise ValueError("Body density must be positive")
    
    body_fat_pct = (495 / body_density) - 450
    
    # Clamp to reasonable range
    body_fat_pct = max(3, min(60, body_fat_pct))
    
    return round(body_fat_pct, 1)


def calculate_body_fat_navy(
    height_cm: float,
    waist_cm: float,
    neck_cm: float,
    sex: str,
    hip_cm: Optional[float] = None
) -> float:
    """
    Calculate body fat percentage using U.S. Navy method (circumferences).
    
    Per spec 3.3.3:
    
    Males:
    BF% = 86.010 × log₁₀(waist - neck) - 70.041 × log₁₀(height) + 36.76
    
    Females:
    BF% = 163.205 × log₁₀(waist + hip - neck) - 97.684 × log₁₀(height) - 78.387
    
    Note: Formula uses cm for all measurements (spec says inches but we use cm)
    
    Args:
        height_cm: Height in centimeters
        waist_cm: Waist circumference in centimeters
        neck_cm: Neck circumference in centimeters
        sex: 'male' or 'female'
        hip_cm: Hip circumference (required for females)
        
    Returns:
        Body fat percentage
    """
    if sex not in ('male', 'female'):
        raise ValueError("Sex must be 'male' or 'female'")
    
    if height_cm <= 0 or waist_cm <= 0 or neck_cm <= 0:
        raise ValueError("All measurements must be positive")
    
    if sex == 'female' and (hip_cm is None or hip_cm <= 0):
        raise ValueError("Hip circumference required for females")
    
    # Convert to inches for the Navy formula
    height_in = height_cm / 2.54
    waist_in = waist_cm / 2.54
    neck_in = neck_cm / 2.54
    
    if sex == 'male':
        if waist_in <= neck_in:
            raise ValueError("Waist must be greater than neck circumference")
        body_fat_pct = (
            86.010 * math.log10(waist_in - neck_in)
            - 70.041 * math.log10(height_in)
            + 36.76
        )
    else:  # female
        hip_in = hip_cm / 2.54
        circumference_sum = waist_in + hip_in - neck_in
        if circumference_sum <= 0:
            raise ValueError("Invalid circumference combination")
        body_fat_pct = (
            163.205 * math.log10(circumference_sum)
            - 97.684 * math.log10(height_in)
            - 78.387
        )
    
    # Clamp to reasonable range
    body_fat_pct = max(3, min(60, body_fat_pct))
    
    return round(body_fat_pct, 1)


def calculate_skinfold_sum(
    chest_mm: Optional[float],
    abdomen_mm: Optional[float],
    thigh_mm: Optional[float],
    triceps_mm: Optional[float],
    subscapular_mm: Optional[float],
    suprailiac_mm: Optional[float],
    midaxillary_mm: Optional[float]
) -> Optional[float]:
    """
    Calculate sum of 7 skinfold measurements.
    
    Args:
        All 7 skinfold sites in millimeters
        
    Returns:
        Sum of skinfolds, or None if any are missing
    """
    sites = [
        chest_mm, abdomen_mm, thigh_mm, triceps_mm,
        subscapular_mm, suprailiac_mm, midaxillary_mm
    ]
    
    if any(s is None for s in sites):
        return None
    
    return sum(sites)


def calculate_lean_mass_from_fat(
    total_weight_kg: float,
    body_fat_pct: float
) -> float:
    """
    Calculate lean mass from total weight and body fat percentage.
    
    Formula: Lean Mass = Weight × (1 - Body Fat % / 100)
    
    Args:
        total_weight_kg: Total body weight in kg
        body_fat_pct: Body fat percentage
        
    Returns:
        Lean mass in kg
    """
    if total_weight_kg <= 0:
        raise ValueError("Weight must be positive")
    if not (0 <= body_fat_pct <= 100):
        raise ValueError("Body fat must be 0-100%")
    
    lean_mass = total_weight_kg * (1 - body_fat_pct / 100)
    return round(lean_mass, 1)


def calculate_fat_mass_from_pct(
    total_weight_kg: float,
    body_fat_pct: float
) -> float:
    """
    Calculate fat mass from total weight and body fat percentage.
    
    Formula: Fat Mass = Weight × (Body Fat % / 100)
    
    Args:
        total_weight_kg: Total body weight in kg
        body_fat_pct: Body fat percentage
        
    Returns:
        Fat mass in kg
    """
    if total_weight_kg <= 0:
        raise ValueError("Weight must be positive")
    if not (0 <= body_fat_pct <= 100):
        raise ValueError("Body fat must be 0-100%")
    
    fat_mass = total_weight_kg * (body_fat_pct / 100)
    return round(fat_mass, 1)


def detect_o2_desaturation(pre_o2_sat: int, post_o2_sat: int) -> bool:
    """
    Detect significant O2 desaturation (>4% drop).
    
    Args:
        pre_o2_sat: Pre-test O2 saturation (%)
        post_o2_sat: Post-test O2 saturation (%)
        
    Returns:
        True if desaturation >4%
    """
    if pre_o2_sat <= 0 or post_o2_sat <= 0:
        return False
    
    drop = pre_o2_sat - post_o2_sat
    return drop > 4
