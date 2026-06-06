"""Nutramilo Insulin Score (NIS) — open, macronutrient-derived postprandial insulin response algorithm.

Public API:
    >>> from nutramilo_nis import compute_nis
    >>> result = compute_nis(carbs_g=50, protein_g=20, fat_g=10, fiber_g=5)
    >>> result["nis_percent"]
    37.4

Citation (required by NOTICE file):
    Inkov, I. (2026). "Nutramilo Insulin Score (NIS): An Open,
    Macronutrient-Derived Algorithm for Predicting Postprandial
    Insulinaemic Response..." Int J Med Rev Case Rep. DOI: 

Trademarks: NIS™, Nutramilo Insulin Score™, Nutramilo™ — International Sci Ink Press Ltd EOOD, EUIPO.
"""
from .nis import (
    NIS_VERSION,
    NIS_COEFFICIENTS,
    NIS_COEFFICIENTS_DATE,
    NIS_CALIBRATION,
    PURE_FAT_DENSITY_THRESHOLD,
    PURE_FAT_ATTENUATION,
    FRUCTOSE_OF_SUGAR,
    FRUCTOSE_MULT,
    compute_nis,
    NisResult,
)
from .classify import classify

__version__ = "1.1.6"
__all__ = [
    "compute_nis",
    "classify",
    "NIS_VERSION",
    "NIS_COEFFICIENTS",
    "NIS_COEFFICIENTS_DATE",
    "NIS_CALIBRATION",
    "PURE_FAT_DENSITY_THRESHOLD",
    "PURE_FAT_ATTENUATION",
    "FRUCTOSE_OF_SUGAR",
    "FRUCTOSE_MULT",
    "NisResult",
    "__version__",
]
