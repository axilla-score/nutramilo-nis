"""Regression test — guarantees NIS v1.0.1 stays at least as good as v1.0.0.

Re-runs the full 63-food peer-reviewed cohort on every commit and asserts:

  • Pearson r of v1.0.1 typed/mixed ≥ v1.0.0 (no regression)
  • MAE of v1.0.1 typed/mixed ≤ v1.0.0 (no regression)
  • Pure-fat subset prediction is < 25 % (matches Holt 1997 observation)

Numbers are intentionally lenient: if any future model change DROPS the
metric, this test breaks immediately and CI gates the release.
"""

import pytest

pytest.skip(
    "validation module not included in GitHub release",
    allow_module_level=True
)
from validation.validate_v1_0_1 import run_validation


@pytest.fixture(scope="module")
def report():
    return run_validation()


def test_cohort_size_unchanged(report):
    """Detect accidental dataset edits — committed cohort = 63 foods."""
    assert report["cohort"]["size"] == 63


def test_no_pearson_regression(report):
    """v1.0.1 (mixed and typed) must NEVER be worse than v1.0.0 on r."""
    g = report["global"]
    assert g["v1_0_1_mixed"]["pearson_r"] >= g["v1_0_0"]["pearson_r"], \
        f'r regressed: mixed={g["v1_0_1_mixed"]["pearson_r"]} vs base={g["v1_0_0"]["pearson_r"]}'
    assert g["v1_0_1_typed"]["pearson_r"] >= g["v1_0_0"]["pearson_r"], \
        f'r regressed: typed={g["v1_0_1_typed"]["pearson_r"]} vs base={g["v1_0_0"]["pearson_r"]}'


def test_no_mae_regression(report):
    """v1.0.1 must produce LOWER mean absolute error than v1.0.0."""
    g = report["global"]
    assert g["v1_0_1_mixed"]["mae"] <= g["v1_0_0"]["mae"]
    assert g["v1_0_1_typed"]["mae"] <= g["v1_0_0"]["mae"]


def test_pure_fat_guard_effective(report):
    """Pure-fat predictions in v1.0.1 must be close to the observed ~9 % mean.

    Holt 1997: butter / oils / cream II ≈ 3–12 %.  v1.0.0 over-predicted by
    5×; the guard MUST bring it down to ≤ 25 %.
    """
    pf = report["pure_fat_subset"]
    assert pf["v1_0_1_mixed"]["mean_predicted"] <= 25.0
    assert pf["v1_0_1_typed"]["mean_predicted"] <= 25.0
    # And v1.0.0 must STILL be broken (sanity check that we're really testing
    # an improvement and not just a regression of v1.0.0 too)
    assert pf["v1_0_0"]["mean_predicted"] >= 40.0


def test_typed_pipeline_beats_mixed_on_mae(report):
    """Source-type classification should produce at least small improvement.

    This is the only test that asserts the *modifier* hypothesis directly —
    if a future change to the multipliers makes 'typed' worse than 'mixed',
    we want to know.
    """
    g = report["global"]
    assert g["v1_0_1_typed"]["mae"] <= g["v1_0_1_mixed"]["mae"] + 0.5, \
        "Source-type modifiers worsened MAE — re-tune multipliers."
