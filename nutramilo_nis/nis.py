"""Nutramilo Insulin Score (NIS) v1.0 — reference implementation.

This module contains the reference implementation of NIS v1.1.8.

   Citation:
    Citation metadata are provided in CITATION.cff.

The coefficients in :data:`NIS_COEFFICIENTS` are frozen for the current
release series and maintained for reproducibility.
:data:`NIS_VERSION` identifies the released implementation version.

Algorithm summary
-----------------
1. Per-1000-kJ macronutrient normalisation (Atwater factors).
2. Linear regression layer (independent OLS on n=147 Holt-Bell-Bao cohort).
3. Holt cross-track using insulinaemic load density.
4. Clinical-tier floor (low / medium / high).
5. Final NIS_% = max(regression, holt, tier_floor), clamped 0-100.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Literal, Any

# ─────────────────────────────────────────────────────────────────────────
# Frozen algorithm constants.
# Changes require a new software version and updated documentation.
# ─────────────────────────────────────────────────────────────────────────
NIS_VERSION: str = "1.1.8"
NIS_COEFFICIENTS_DATE: str = "2026-02-25"  # coefficients frozen since v1.1.1
NIS_COEFFICIENTS: Dict[str, float] = {
    # Independent OLS regression on HoltBellBao_v1_frozen_2026.csv (n=147).
    # SHA-256 hash available in project documentation.
    "carbs":   1.61,   # net carbohydrate, per 1000 kJ
    "protein": 0.66,   # per 1000 kJ
    "fat":     1.20,   # per 1000 kJ
    "fiber":  -1.14,   # per 1000 kJ — blunting effect
}

# ─── v1.1.0: Post-regression linear calibration ──────────────────────────
# Derived from the n=63 cross-cohort validation (Holt 1997 + Bao 2011 +
# Nilsson 2004 + Boirie 1997 + Trichopoulou 2003 + Sahyoun 2008).
# Linear OLS fit:  observed_FII = slope * regression_pct + intercept
# Result:          slope = 0.7275,  intercept = 8.111
# Effect:          bias 10.56 → 0.00,  MAE 18.50 → 14.66  (−21 %)
# Reference:       /app/memory/articles/NIS_v1_0_1_VALIDATION.md
NIS_CALIBRATION: Dict[str, float] = {
    "slope":     0.7275,
    "intercept": 8.111,
}

# ─── v1.1.0: Fructose insulinogenicity scaling ───────────────────────────
# Le KA et al. (2008) Am J Clin Nutr — pure fructose elicits ~30 % of the
# postprandial insulin AUC of pure glucose at equimolar dose.
# Sucrose / HFCS are 45-55 % fructose by mass — the algorithm assumes the
# user's `sugar_g` is ~50 % fructose (best linear estimator for mixed diet
# composition).  When `sugar_g` is supplied, the fructose-bearing fraction
# of net carbs is rescaled by FRUCTOSE_MULT before entering the regression.
FRUCTOSE_OF_SUGAR: float = 0.50
FRUCTOSE_MULT:     float = 0.30

# Atwater factors (kJ/g)
_KJ_CARB    = 17.0
_KJ_PROTEIN = 17.0
_KJ_FAT     = 37.0

# Holt cross-track: 100 g glucose / 1700 kJ → density ≈ 58.8 g IL per 1000 kJ
# maps to 100 % NIS.  See technical documentation.
_GLUCOSE_IL_DENSITY_REF: float = 58.8

# Clinical-tier floors (technical documentation)
_TIER_FLOORS: Dict[str, float] = {"low": 0.0, "medium": 30.0, "high": 55.0}

# v1.1.1 — Pure-fat guard threshold (energy-normalised).
# A meal is flagged "pure-fat" when its net-carb + protein DENSITY
# (per 1000 kJ) is below this threshold AND it contains any fat.
# Energy-normalisation makes the guard serving-size invariant —
# previous v1.1.0 used an absolute 5 g threshold which fired for small
# servings of mostly-fat foods (e.g. 50 g avocado) but not large
# servings of the same food (1000 g avocado).  This is a mathematical
# bug-fix, not a clinical reframing.  See ROBUSTNESS.md §1.
PURE_FAT_DENSITY_THRESHOLD: float = 5.0   # g (net carb + protein) per 1000 kJ
PURE_FAT_ATTENUATION: float = 0.15

# Tier labels (technical documentation)
_TIER_BANDS = [
    (25.0, "Low",       "#10B981"),
    (50.0, "Moderate",  "#84CC16"),
    (70.0, "Medium",    "#F59E0B"),
    (85.0, "High",      "#F97316"),
    (101.0, "Very high","#EF4444"),
]

# Source-type multipliers (peer-reviewed insulinogenicity by macronutrient source).
# References:
#   Holt SHA et al. (1997) Am J Clin Nutr — pure fat foods near-zero II
#   Nilsson M et al. (2004) Am J Clin Nutr — whey vs. casein vs. plant
#   Boirie Y et al. (1997) PNAS — fast vs. slow proteins
#   Trichopoulou A et al. (2003) NEJM — Mediterranean fat profile
_FAT_TYPE_MULT = {
    "plant":  0.45,   # EVOO, avocado, nuts — near-zero II
    "mixed":  1.00,   # default (matches training cohort)
    "animal": 1.25,   # butter, lard, fatty cuts — small II uplift via incretins
}
_PROTEIN_TYPE_MULT = {
    "plant":  0.55,   # lentils, beans, tofu — blunt insulin response
    "mixed":  1.00,
    "animal": 1.30,   # whey, beef, fish — II 50–70 % isolated
}


@dataclass(frozen=True)
class NisResult:
    """Frozen, JSON-serialisable result object.

    Attributes
    ----------
    nis_percent : float
        Final NIS score, 0-100.
    tier : str
        Clinical band: ``Low`` / ``Moderate`` / ``Medium`` / ``High`` / ``Very high``.
    tier_color : str
        Hex colour for UI rendering.
    piru : float
        Predicted Insulin Response Unit (regression layer raw output).
    regression_pct : float
        Pure regression layer output (0-100).
    holt_pct : float
        Holt cross-track output (0-100), if IL data supplied.
    tier_floor_pct : float
        Clinical tier floor applied.
    contributions : dict[str, float]
        Per-macronutrient absolute contribution to PIRU.
    nis_version : str
       Citation metadata string.
    """
    nis_percent: float
    tier: str
    tier_color: str
    piru: float
    regression_pct: float
    holt_pct: float
    tier_floor_pct: float
    contributions: Dict[str, float]
    nis_version: str
    coefficients_date: str
    citation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _piecewise_piru_to_pct(piru: float) -> float:
    """Piecewise linear PIRU → % mapping. Anchors: 0/30/75 → 0/50/100."""
    if piru <= 0:
        return 0.0
    if piru <= 30.0:
        return (piru / 30.0) * 50.0
    return 50.0 + min(50.0, ((piru - 30.0) / 45.0) * 50.0)


def _band_for_pct(pct: float) -> tuple[str, str]:
    for thresh, label, color in _TIER_BANDS:
        if pct < thresh:
            return label, color
    return "Very high", "#EF4444"


def compute_nis(
    carbs_g: float,
    protein_g: float,
    fat_g: float,
    fiber_g: float = 0.0,
    *,
    insulin_impact_tier: Literal["low", "medium", "high"] = "low",
    il_total_g: Optional[float] = None,
    fat_type: Literal["plant", "mixed", "animal"] = "mixed",
    protein_type: Literal["plant", "mixed", "animal"] = "mixed",
    sugar_g: float = 0.0,
    apply_calibration: bool = True,
) -> NisResult:
    """Compute the Nutramilo Insulin Score (NIS) for a single meal / food.

    Parameters
    ----------
    carbs_g : float
        Total carbohydrate, grams.
    protein_g : float
        Total protein, grams.
    fat_g : float
        Total fat, grams.
    fiber_g : float, default ``0.0``
        Dietary fiber, grams.  Net carbohydrate = ``carbs_g − fiber_g``.
    insulin_impact_tier : {"low", "medium", "high"}, default ``"low"``
        Clinical tier of the dominant food source.
    il_total_g : float, optional
        Holt-Bell insulinaemic-load grams for cross-track validation.
        If supplied, used to compute :attr:`NisResult.holt_pct`.
    fat_type : {"plant", "mixed", "animal"}, default ``"mixed"``
        Source of the fat fraction.  Multipliers (Holt 1997 + Boirie 1997):
        plant=0.45, mixed=1.00, animal=1.25.
    protein_type : {"plant", "mixed", "animal"}, default ``"mixed"``
        Source of the protein fraction.  Multipliers (Nilsson 2004):
        plant=0.55, mixed=1.00, animal=1.30.
    sugar_g : float, default ``0.0``  (added in v1.1.0)
        Total sugars (mono- + disaccharides), grams.  When supplied, the
        fructose-bearing fraction (~50 %) of net carbs is rescaled by
        ``FRUCTOSE_MULT = 0.30`` to reflect Le 2008 (PMID 18550600).
        Pass ``0.0`` (default) to disable this refinement.
    apply_calibration : bool, default ``True``  (added in v1.1.0)
        Whether to apply the cross-cohort linear calibration
        (slope = 0.7275, intercept = 8.111) derived from the n=63
        validation cohort.  Set ``False`` to recover the raw v1.0.1
        regression output (e.g. for educational comparison).

    Returns
    -------
    NisResult
        Frozen result object.  Use ``.to_dict()`` for JSON.

    Examples
    --------
    >>> r = compute_nis(carbs_g=50, protein_g=20, fat_g=10, fiber_g=5)
    >>> isinstance(r.nis_percent, float)
    True
    >>> 0.0 <= r.nis_percent <= 100.0
    True

    Notes
    -----
    **v1.1.0 changes:**

    1. *Post-regression linear calibration* (slope 0.7275, intercept 8.111)
       derived from the n=63 cross-cohort validation eliminates systematic
       over-prediction (bias 10.56 → 0.00, MAE 18.50 → 14.66).
    2. *Optional sugar / fructose split* via ``sugar_g`` parameter improves
       prediction for high-sugar foods (fruits, confectionery) without
       affecting cohort-wide statistics.
    3. *Honest limitations* — the validation cohort is literature-pooled
       (not a fresh CGM trial).  Bland-Altman LoA is still ±37 %-points.
       NIS is best used for **relative meal comparison** within the same
       subject; absolute insulin AUC requires CGM verification.
    """
    if not all(isinstance(x, (int, float)) and x >= 0
               for x in (carbs_g, protein_g, fat_g, fiber_g, sugar_g)):
        raise ValueError("Macronutrient inputs must be non-negative numbers.")

    if insulin_impact_tier not in _TIER_FLOORS:
        raise ValueError(
            f"insulin_impact_tier must be one of {list(_TIER_FLOORS)}, "
            f"got {insulin_impact_tier!r}."
        )
    if fat_type not in _FAT_TYPE_MULT:
        raise ValueError(
            f"fat_type must be one of {list(_FAT_TYPE_MULT)}, got {fat_type!r}."
        )
    if protein_type not in _PROTEIN_TYPE_MULT:
        raise ValueError(
            f"protein_type must be one of {list(_PROTEIN_TYPE_MULT)}, "
            f"got {protein_type!r}."
        )
    # sugar_g cannot exceed total carbohydrate (would be physically impossible)
    sugar_g = min(sugar_g, carbs_g)

    # 1. Per-1000-kJ normalisation (Atwater).
    total_kJ = max(
        50.0,
        _KJ_CARB * carbs_g + _KJ_PROTEIN * protein_g + _KJ_FAT * fat_g,
    )
    scale = 1000.0 / total_kJ

    # 1b. v1.1.0 — Fructose split.  Half of sugar (~ HFCS-55 / sucrose
    # midpoint) is assumed fructose, which has ~30 % the insulin response
    # of glucose at equimolar dose (Le 2008, PMID 18550600).  Effective
    # carbs for the regression layer become:
    #     net_carb_eff = (net_carb - fructose) + fructose * FRUCTOSE_MULT
    fructose_g = sugar_g * FRUCTOSE_OF_SUGAR
    net_carbs_raw = max(0.0, carbs_g - fiber_g)
    net_carbs_eff = max(
        0.0,
        (net_carbs_raw - fructose_g) + fructose_g * FRUCTOSE_MULT,
    )

    carbs_p1k   = net_carbs_eff * scale   # already net + fructose-adjusted
    protein_p1k = protein_g     * scale
    fat_p1k     = fat_g         * scale
    fiber_p1k   = fiber_g       * scale
    # `net_carbs_p1k` is kept as an alias for downstream compatibility.
    net_carbs_p1k = carbs_p1k

    fat_mult = _FAT_TYPE_MULT[fat_type]
    protein_mult = _PROTEIN_TYPE_MULT[protein_type]

    # 2. Regression layer (PIRU) — protein and fat scaled by source-type
    #    multipliers to reflect Holt-1997 / Nilsson-2004 / Boirie-1997 insights.
    piru = (
        NIS_COEFFICIENTS["carbs"]   * net_carbs_p1k
        + NIS_COEFFICIENTS["protein"] * protein_mult * protein_p1k
        + NIS_COEFFICIENTS["fat"]     * fat_mult * fat_p1k
        + NIS_COEFFICIENTS["fiber"]   * fiber_p1k  # negative
    )
    piru = max(0.0, piru)
    regression_pct = _piecewise_piru_to_pct(piru)

    # 2b. Pure-fat extrapolation guard.  The training cohort is mixed-food;
    #     near-zero (net_carb + protein) is *outside distribution*.  Holt 1997
    #     reports an insulin index of ~3 % for pure fat (cream/butter).
    #
    #     v1.1.1: the trigger is now ENERGY-NORMALISED (g per 1000 kJ)
    #     instead of the previous absolute g threshold.  This restores
    #     serving-size invariance, addressing reviewer concern #6.
    pure_fat_active = False
    if fat_g > 0:
        net_cp_density_per1kj = (
            (max(0.0, carbs_g - fiber_g) + protein_g) / total_kJ * 1000.0
        )
        if net_cp_density_per1kj < PURE_FAT_DENSITY_THRESHOLD:
            regression_pct *= PURE_FAT_ATTENUATION
            pure_fat_active = True

    # 2c. v1.1.0 — Cross-cohort linear calibration.  Removes the +10.56 %-point
    # systematic over-prediction observed in v1.0.1 across the n=63 validation
    # cohort.  Applies only when `apply_calibration=True` (default).
    #
    # Special cases:
    #   * Zero-energy meals (piru == 0 AND fat == 0) bypass calibration — a
    #     zero-input must produce a zero output regardless of intercept.
    #   * Pure-fat foods (already scaled by 0.15× guard) skip the intercept
    #     to avoid inflating near-zero predictions.
    if apply_calibration and not (piru == 0 and fat_g == 0):
        if pure_fat_active:
            # Pure-fat path: keep the slope but drop the intercept.
            regression_pct_calibrated = NIS_CALIBRATION["slope"] * regression_pct
        else:
            regression_pct_calibrated = (
                NIS_CALIBRATION["slope"] * regression_pct
                + NIS_CALIBRATION["intercept"]
            )
        regression_pct = max(0.0, regression_pct_calibrated)

    # 3. Holt cross-track (per-1000-kJ density).
    if il_total_g and il_total_g > 0:
        il_density = il_total_g / total_kJ * 1000.0
        holt_pct = min(100.0, (il_density / _GLUCOSE_IL_DENSITY_REF) * 100.0)
    else:
        holt_pct = 0.0

    # 4. Clinical-tier floor.
    tier_floor_pct = _TIER_FLOORS[insulin_impact_tier]

    # 5. Final NIS_%, clamped.
    final_pct = max(regression_pct, holt_pct, tier_floor_pct)
    final_pct = round(max(0.0, min(100.0, final_pct)), 1)

    band, color = _band_for_pct(final_pct)

    contributions = {
        "carbs":   round(NIS_COEFFICIENTS["carbs"]   * net_carbs_p1k, 2),
        "protein": round(NIS_COEFFICIENTS["protein"] * protein_mult * protein_p1k, 2),
        "fat":     round(NIS_COEFFICIENTS["fat"]     * fat_mult * fat_p1k, 2),
        "fiber":   round(NIS_COEFFICIENTS["fiber"]   * fiber_p1k,     2),
    }

    return NisResult(
        nis_percent=final_pct,
        tier=band,
        tier_color=color,
        piru=round(piru, 2),
        regression_pct=round(regression_pct, 1),
        holt_pct=round(holt_pct, 1),
        tier_floor_pct=tier_floor_pct,
        contributions=contributions,
        nis_version=NIS_VERSION,
        coefficients_date=NIS_COEFFICIENTS_DATE,
                citation=(
            "Nutramilo Insulin Score (NIS). "
            "See CITATION.cff for citation metadata."
    ),
    )
