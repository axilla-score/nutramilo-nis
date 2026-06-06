"""Nutramilo Insulin Score (NIS) — an open-source algorithm designed to estimate the relative insulinogenic potential of a meal from its nutritional composition. NIS is intended for research, educational use, software development, and exploratory nutritional analysis. It should not be interpreted as a clinically validated predictor of postprandial insulin response. ⚠️ Scientific status. NIS v1.1.7 represents an exploratory methodology. The algorithm is intended for comparative analysis of meals and hypothesis generation rather than diagnostic or therapeutic decision-making.


Public API:
    >>> from nutramilo_nis import compute_nis
    >>> result = compute_nis(carbs_g=50, protein_g=20, fat_g=10, fiber_g=5)
    >>> result["nis_percent"]
    37.4

Citation:
    If you use this software, please cite the software repository
    and accompanying documentation.  


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

__version__ = "1.1.7"
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
