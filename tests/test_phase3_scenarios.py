"""
Phase 3 Validation Test Script
==============================

Tests Section 1 (Body Composition) implementation with calculation validation.

Validates:
- Jackson-Pollock skinfold formula
- Navy method circumference formula
- LMI calculation
- Body fat scoring (age/sex-adjusted)
- Sarcopenia risk detection
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculators.body_composition import (
    calculate_bmi,
    calculate_lmi,
    calculate_whr,
    calculate_body_density_jackson_pollock,
    calculate_body_fat_siri,
    calculate_body_fat_navy,
    calculate_skinfold_sum,
    calculate_lean_mass_from_fat,
)
from scoring.section1 import (
    score_body_fat_pct,
    score_lmi,
    score_visceral_fat,
    assess_sarcopenia_risk,
)


def test_bmi_calculations():
    """Test BMI calculation."""
    print("\n" + "="*60)
    print("TEST: BMI CALCULATIONS")
    print("="*60)
    
    # Test cases from spec
    test_cases = [
        (75, 175, 24.5, "Normal male"),
        (78, 162, 29.7, "68F Sedentary"),
        (72, 180, 22.2, "42M Athletic"),
    ]
    
    all_passed = True
    for weight, height, expected, desc in test_cases:
        result = calculate_bmi(weight, height)
        passed = abs(result - expected) < 0.1
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {desc} - BMI = {result} (expected: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_lmi_calculations():
    """Test Lean Mass Index calculation."""
    print("\n" + "="*60)
    print("TEST: LMI CALCULATIONS")
    print("="*60)
    
    # LMI = lean_mass / height_m²
    test_cases = [
        (55, 175, 17.96, "55M with 55kg lean mass"),  # 55 / 1.75² = 17.96
        (45, 162, 17.15, "68F with 45kg lean mass"),  # 45 / 1.62² = 17.15
        (60, 180, 18.52, "42M athletic with 60kg lean"),  # 60 / 1.80² = 18.52
    ]
    
    all_passed = True
    for lean_mass, height, expected, desc in test_cases:
        result = calculate_lmi(lean_mass, height)
        passed = abs(result - expected) < 0.1
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {desc} - LMI = {result} (expected: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_jackson_pollock_formula():
    """Test Jackson-Pollock 7-site skinfold formula."""
    print("\n" + "="*60)
    print("TEST: JACKSON-POLLOCK SKINFOLD FORMULA")
    print("="*60)
    
    # From spec example in 3.3.2
    # Male, age 45, skinfold sum = 120 mm
    # Body Density = 1.112 - 0.00043499(120) + 0.00000055(120²) - 0.00028826(45)
    #              = 1.112 - 0.0522 + 0.00792 - 0.01297
    #              = 1.05475
    
    sum_sf = 120
    age = 45
    sex = 'male'
    
    expected_bd = 1.05475
    result_bd = calculate_body_density_jackson_pollock(sum_sf, age, sex)
    
    passed_bd = abs(result_bd - expected_bd) < 0.001
    status_bd = "✅ PASS" if passed_bd else "❌ FAIL"
    print(f"{status_bd}: Body Density = {result_bd} (expected: ~{expected_bd})")
    
    # Body Fat % = (495 / BD) - 450 = (495 / 1.05475) - 450 = 19.4%
    expected_bf = 19.4
    result_bf = calculate_body_fat_siri(result_bd)
    
    passed_bf = abs(result_bf - expected_bf) < 0.5
    status_bf = "✅ PASS" if passed_bf else "❌ FAIL"
    print(f"{status_bf}: Body Fat % = {result_bf} (expected: ~{expected_bf})")
    
    # Test female formula
    result_bd_f = calculate_body_density_jackson_pollock(100, 50, 'female')
    result_bf_f = calculate_body_fat_siri(result_bd_f)
    print(f"  Female (sum=100, age=50): BD={result_bd_f}, BF={result_bf_f}%")
    
    return passed_bd and passed_bf


def test_navy_method():
    """Test Navy method circumference formula."""
    print("\n" + "="*60)
    print("TEST: NAVY METHOD (CIRCUMFERENCES)")
    print("="*60)
    
    # Test male case
    # Height: 175 cm, Waist: 90 cm, Neck: 38 cm
    result_male = calculate_body_fat_navy(175, 90, 38, 'male')
    print(f"Male (H:175, W:90, N:38): Body Fat = {result_male}%")
    
    # Expected roughly 20-25% for these measurements
    passed_male = 15 < result_male < 30
    status_male = "✅ PASS" if passed_male else "❌ FAIL"
    print(f"{status_male}: Male result in reasonable range (15-30%)")
    
    # Test female case
    # Height: 162 cm, Waist: 85 cm, Hip: 100 cm, Neck: 33 cm
    result_female = calculate_body_fat_navy(162, 85, 33, 'female', 100)
    print(f"Female (H:162, W:85, H:100, N:33): Body Fat = {result_female}%")
    
    # Expected roughly 25-35% for these measurements
    passed_female = 20 < result_female < 40
    status_female = "✅ PASS" if passed_female else "❌ FAIL"
    print(f"{status_female}: Female result in reasonable range (20-40%)")
    
    return passed_male and passed_female


def test_body_fat_scoring():
    """Test age/sex-adjusted body fat scoring."""
    print("\n" + "="*60)
    print("TEST: BODY FAT SCORING (Age/Sex-Adjusted)")
    print("="*60)
    
    test_cases = [
        # (body_fat%, age, sex, expected_category)
        (15, 55, 'male', 'Excellent'),  # Male 50-69: <16% = Excellent
        (25, 55, 'male', 'Poor'),       # Male 50-69: 24-26% = Poor
        (22, 55, 'female', 'Good'),     # Female 50-69: 22-27% = Good (boundary)
        (30, 68, 'female', 'Fair'),     # Female 50-69: 27-31% = Fair
        (12, 42, 'male', 'Excellent'),  # Male 30-49: <14% = Excellent
    ]
    
    all_passed = True
    for bf, age, sex, expected_cat in test_cases:
        score, category = score_body_fat_pct(bf, age, sex)
        passed = category == expected_cat
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {sex} age {age}, BF {bf}% → {category} (expected: {expected_cat})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_lmi_scoring():
    """Test LMI scoring."""
    print("\n" + "="*60)
    print("TEST: LMI SCORING")
    print("="*60)
    
    test_cases = [
        # (lmi, sex, expected_category)
        (21, 'male', 'Excellent'),     # Male ≥20 = Excellent
        (18.5, 'male', 'Good'),        # Male 18-20 = Good
        (17, 'male', 'Fair'),          # Male 16-18 = Fair
        (13, 'male', 'Sarcopenia'),    # Male <14 = Sarcopenia
        (18, 'female', 'Excellent'),   # Female ≥17 = Excellent
        (14, 'female', 'Fair'),        # Female 13-15 = Fair
        (10, 'female', 'Sarcopenia'),  # Female <11 = Sarcopenia
    ]
    
    all_passed = True
    for lmi, sex, expected_cat in test_cases:
        score, category = score_lmi(lmi, sex)
        passed = category == expected_cat
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {sex}, LMI {lmi} → {category} (expected: {expected_cat})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_sarcopenia_detection():
    """Test sarcopenia risk detection."""
    print("\n" + "="*60)
    print("TEST: SARCOPENIA RISK DETECTION")
    print("="*60)
    
    test_cases = [
        # (sex, lmi, asmi, expected_at_risk)
        ('male', 18.0, None, False),   # LMI 18 > 14 = no risk
        ('male', 13.5, None, True),    # LMI 13.5 < 14 = at risk
        ('female', 12.0, None, False), # LMI 12 > 11 = no risk
        ('female', 10.5, None, True),  # LMI 10.5 < 11 = at risk
        ('male', None, 7.5, False),    # ASMI 7.5 > 7.0 = no risk
        ('male', None, 6.5, True),     # ASMI 6.5 < 7.0 = at risk
        ('female', None, 5.0, True),   # ASMI 5.0 < 5.4 = at risk
    ]
    
    all_passed = True
    for sex, lmi, asmi, expected in test_cases:
        at_risk, reason = assess_sarcopenia_risk(sex, lmi=lmi, asmi=asmi)
        passed = at_risk == expected
        status = "✅ PASS" if passed else "❌ FAIL"
        param = f"LMI={lmi}" if lmi else f"ASMI={asmi}"
        print(f"{status}: {sex}, {param} → at_risk={at_risk} (expected: {expected})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_visceral_fat_scoring():
    """Test visceral fat scoring."""
    print("\n" + "="*60)
    print("TEST: VISCERAL FAT SCORING")
    print("="*60)
    
    test_cases = [
        # (vfa_cm2, bia_level, expected_score, expected_cat)
        (80, None, 100, 'Low Risk'),
        (120, None, 85, 'Borderline'),
        (150, None, 70, 'Elevated'),
        (180, None, 50, 'High'),
        (250, None, 25, 'Very High'),
        (None, 8, 100, 'Healthy'),
        (None, 12, 70, 'Elevated'),
        (None, 20, 40, 'High'),
    ]
    
    all_passed = True
    for vfa, bia, expected_score, expected_cat in test_cases:
        score, category = score_visceral_fat(vfa, bia)
        passed = score == expected_score
        status = "✅ PASS" if passed else "❌ FAIL"
        param = f"VFA={vfa}" if vfa else f"BIA={bia}"
        print(f"{status}: {param} → score={score}, cat={category} (expected: {expected_score}, {expected_cat})")
        if not passed:
            all_passed = False
    
    return all_passed


def test_scenario_calculations():
    """Test complete calculation flow for test scenarios."""
    print("\n" + "="*60)
    print("TEST: COMPLETE SCENARIO CALCULATIONS")
    print("="*60)
    
    # Scenario 1: 55M High-Functioning with DEXA
    print("\n--- Scenario 1: 55M High-Functioning (DEXA) ---")
    bf_55m = 18.0  # Body fat %
    lean_mass_55m = 61.5  # kg (75 * 0.82)
    height_55m = 175  # cm
    
    lmi_55m = calculate_lmi(lean_mass_55m, height_55m)
    bf_score, bf_cat = score_body_fat_pct(bf_55m, 55, 'male')
    lmi_score, lmi_cat = score_lmi(lmi_55m, 'male')
    sarco_risk, _ = assess_sarcopenia_risk('male', lmi=lmi_55m)
    
    print(f"  Body Fat: {bf_55m}% → {bf_cat} (score: {bf_score})")
    print(f"  LMI: {lmi_55m} kg/m² → {lmi_cat} (score: {lmi_score})")
    print(f"  Sarcopenia Risk: {sarco_risk}")
    
    # Scenario 2: 68F Sedentary with manual skinfolds
    print("\n--- Scenario 2: 68F Sedentary (Skinfolds) ---")
    # Simulated skinfolds totaling 140 mm
    sum_sf_68f = 140
    bd_68f = calculate_body_density_jackson_pollock(sum_sf_68f, 68, 'female')
    bf_68f = calculate_body_fat_siri(bd_68f)
    lean_68f = calculate_lean_mass_from_fat(78, bf_68f)
    lmi_68f = calculate_lmi(lean_68f, 162)
    
    bf_score_68f, bf_cat_68f = score_body_fat_pct(bf_68f, 68, 'female')
    lmi_score_68f, lmi_cat_68f = score_lmi(lmi_68f, 'female')
    sarco_risk_68f, _ = assess_sarcopenia_risk('female', lmi=lmi_68f)
    
    print(f"  Skinfold Sum: {sum_sf_68f} mm")
    print(f"  Body Density: {bd_68f}")
    print(f"  Body Fat: {bf_68f}% → {bf_cat_68f} (score: {bf_score_68f})")
    print(f"  Lean Mass: {lean_68f} kg")
    print(f"  LMI: {lmi_68f} kg/m² → {lmi_cat_68f} (score: {lmi_score_68f})")
    print(f"  Sarcopenia Risk: {sarco_risk_68f}")
    
    # Scenario 3: 42M Athletic with BIA
    print("\n--- Scenario 3: 42M Athletic (BIA) ---")
    bf_42m = 12.0  # Athletic low body fat
    lean_mass_42m = 63.4  # kg (72 * 0.88)
    height_42m = 180  # cm
    
    lmi_42m = calculate_lmi(lean_mass_42m, height_42m)
    bf_score_42m, bf_cat_42m = score_body_fat_pct(bf_42m, 42, 'male')
    lmi_score_42m, lmi_cat_42m = score_lmi(lmi_42m, 'male')
    sarco_risk_42m, _ = assess_sarcopenia_risk('male', lmi=lmi_42m)
    
    print(f"  Body Fat: {bf_42m}% → {bf_cat_42m} (score: {bf_score_42m})")
    print(f"  LMI: {lmi_42m} kg/m² → {lmi_cat_42m} (score: {lmi_score_42m})")
    print(f"  Sarcopenia Risk: {sarco_risk_42m}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "#"*70)
    print("#" + " "*20 + "PHASE 3 VALIDATION TEST" + " "*20 + "#")
    print("#" + " "*15 + "Section 1: Body Composition" + " "*15 + "#")
    print("#"*70)
    
    results = []
    
    results.append(("BMI Calculations", test_bmi_calculations()))
    results.append(("LMI Calculations", test_lmi_calculations()))
    results.append(("Jackson-Pollock Formula", test_jackson_pollock_formula()))
    results.append(("Navy Method", test_navy_method()))
    results.append(("Body Fat Scoring", test_body_fat_scoring()))
    results.append(("LMI Scoring", test_lmi_scoring()))
    results.append(("Sarcopenia Detection", test_sarcopenia_detection()))
    results.append(("Visceral Fat Scoring", test_visceral_fat_scoring()))
    results.append(("Scenario Calculations", test_scenario_calculations()))
    
    # Summary
    print("\n" + "="*70)
    print("PHASE 3 VALIDATION SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL PHASE 3 VALIDATION CHECKS PASSED!")
    else:
        print("⚠️  SOME CHECKS FAILED. Review the results above.")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())
