"""Unit tests for nutramilo_nis.compute_nis — frozen v1.1.0 reference."""
import pytest
from nutramilo_nis import compute_nis, NIS_VERSION, NIS_COEFFICIENTS


def test_version_frozen():
    assert NIS_VERSION == "1.1.9"
    # Frozen coefficients — MUST NEVER change in v1.x (only modifiers added).
    assert NIS_COEFFICIENTS == {
        "carbs": 1.61, "protein": 0.66, "fat": 1.20, "fiber": -1.14,
    }


def test_zero_macros_returns_zero():
    r = compute_nis(0, 0, 0, 0)
    assert r.nis_percent == 0.0
    assert r.tier == "Low"


def test_clamps_at_100():
    """v1.1.0 calibration caps pure-glucose meals at ~81 %, not 100. White
    bread (Holt reference FII=100) corresponds to ~80-85 % calibrated NIS.
    Holt cross-track (il_total_g=100) can still push to 100."""
    r = compute_nis(carbs_g=300, protein_g=0, fat_g=0, fiber_g=0)
    # Bound: must be high (≥75) but not saturate (≤100).
    assert 75.0 <= r.nis_percent <= 100.0
    assert r.tier in ("High", "Very high")
    # Holt cross-track route reaches 100.
    r_holt = compute_nis(carbs_g=100, protein_g=0, fat_g=0, fiber_g=0, il_total_g=100)
    assert r_holt.nis_percent == 100.0


def test_fiber_reduces_nis():
    no_fiber = compute_nis(50, 10, 5, fiber_g=0).nis_percent
    high_fiber = compute_nis(50, 10, 5, fiber_g=15).nis_percent
    assert high_fiber < no_fiber


def test_plate_size_independence():
    """NIS is per-meal density — doubling all macros should yield same %."""
    small = compute_nis(40, 30, 10, fiber_g=5).nis_percent
    large = compute_nis(80, 60, 20, fiber_g=10).nis_percent
    assert abs(small - large) < 0.1


def test_tier_floor_applied():
    """High insulin impact tier floor lifts a low-regression meal."""
    r = compute_nis(2, 2, 2, fiber_g=0, insulin_impact_tier="high")
    assert r.nis_percent >= 55.0
    assert r.tier_floor_pct == 55.0


def test_holt_cross_track_pure_glucose():
    """100 g glucose ≈ 100 % NIS via Holt cross-track."""
    r = compute_nis(carbs_g=100, protein_g=0, fat_g=0, fiber_g=0, il_total_g=100)
    assert r.holt_pct >= 99.0


def test_invalid_tier_raises():
    with pytest.raises(ValueError):
        compute_nis(50, 20, 10, fiber_g=5, insulin_impact_tier="extreme")


def test_negative_macros_raises():
    with pytest.raises(ValueError):
        compute_nis(carbs_g=-5, protein_g=20, fat_g=10)


def test_result_serialisable():
    r = compute_nis(50, 20, 10, fiber_g=5)
    d = r.to_dict()
    assert "nis_percent" in d
    assert "citation" in d
    assert "CITATION.cff" in d["citation"]


def test_worked_example_balanced_meal():
    """Salmon + quinoa + broccoli (paper Sec. 3.2, Table 3)."""
    r = compute_nis(carbs_g=35, protein_g=30, fat_g=15, fiber_g=8)
    assert 50.0 <= r.nis_percent <= 75.0
    assert r.tier in {"Moderate", "Medium", "High"}


def test_worked_example_white_rice():
    """1 cup white rice ≈ High tier (paper Sec. 3.2, Table 3)."""
    r = compute_nis(carbs_g=45, protein_g=4, fat_g=0.5, fiber_g=1)
    assert r.nis_percent >= 50.0


def test_worked_example_avocado():
    """Avocado alone — fat dominant, fiber high → Low."""
    r = compute_nis(carbs_g=9, protein_g=2, fat_g=15, fiber_g=7)
    assert r.nis_percent <= 35.0
    assert r.tier in {"Low", "Moderate"}


# ─── v1.0.1 additions: source-type modifiers + pure-fat guard ───

def test_pure_fat_guard_50g():
    """50 g of pure fat (no carbs/protein) — Holt 1997: II ~ 3 %.
    With the v1.0.1 pure-fat guard the score must be at most "Moderate"."""
    r = compute_nis(carbs_g=0, protein_g=0, fat_g=50, fiber_g=0)
    assert r.nis_percent <= 25.0, f"pure-fat NIS too high: {r.nis_percent}"
    assert r.tier == "Low"


def test_pure_fat_guard_lifts_when_carbs_added():
    """Once carbs/protein cross the 5 g threshold, normal regression resumes."""
    r_pure = compute_nis(carbs_g=0, protein_g=0, fat_g=50, fiber_g=0)
    r_mixed = compute_nis(carbs_g=5, protein_g=5, fat_g=50, fiber_g=0)
    assert r_mixed.nis_percent > r_pure.nis_percent


def test_fat_type_modifier_changes_score():
    """Animal fat must produce a higher NIS than plant fat for the same plate."""
    plate = dict(carbs_g=30, protein_g=10, fat_g=25, fiber_g=4)
    r_plant  = compute_nis(**plate, fat_type="plant")
    r_mixed  = compute_nis(**plate, fat_type="mixed")
    r_animal = compute_nis(**plate, fat_type="animal")
    assert r_plant.nis_percent < r_mixed.nis_percent < r_animal.nis_percent


def test_protein_type_modifier_changes_score():
    """Animal (whey-like) protein must produce a higher NIS than plant protein."""
    plate = dict(carbs_g=20, protein_g=40, fat_g=10, fiber_g=3)
    r_plant  = compute_nis(**plate, protein_type="plant")
    r_animal = compute_nis(**plate, protein_type="animal")
    assert r_plant.nis_percent < r_animal.nis_percent


def test_invalid_source_type_raises():
    """Invalid fat_type / protein_type must raise ValueError."""
    import pytest
    with pytest.raises(ValueError, match="fat_type must be one of"):
        compute_nis(carbs_g=30, protein_g=10, fat_g=10, fat_type="vegan")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="protein_type must be one of"):
        compute_nis(carbs_g=30, protein_g=10, fat_g=10, protein_type="dairy")  # type: ignore[arg-type]
