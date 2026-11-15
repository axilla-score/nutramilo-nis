# nutramilo-nis

[![PyPI version](https://img.shields.io/pypi/v/nutramilo-nis.svg)](https://pypi.org/project/nutramilo-nis/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20571802.svg)](https://doi.org/10.5281/zenodo.20571802)
[![Python ≥ 3.9](https://img.shields.io/badge/python-≥3.9-green.svg)](https://python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI downloads](https://img.shields.io/pypi/dm/nutramilo-nis.svg)](https://pypi.org/project/nutramilo-nis/)
[![Status: exploratory-methodology](https://img.shields.io/badge/status-exploratory--methodology-yellow.svg)](#scientific-status)

> **Reference implementation of the Nutramilo Insulin Score (NIS)** — an open-source algorithm that estimates, from a meal's macronutrient composition, how it would rank on the white-bread-referenced Food Insulin Index (FII) of Holt et al. (1997) and derivative literature.
>
> NIS is an **exploratory computational surrogate**. It is **not** a medical device, has **not** been clinically validated, and does **not** predict an individual's insulin secretion or glycaemic response.

---

## Scientific status

NIS v1.1.9 is an exploratory, open methodology evaluated against pooled literature FII observations. It has **not** undergone prospective clinical validation on any patient cohort. All outputs must be interpreted as comparative estimates against the Holt-FII historical scale, not as physiological measurements. See the [v4 Statistical Evidence Lock](https://doi.org/10.5281/zenodo.20571802) for the full statistical dossier.

## Intended use

* Comparative ranking of meals by macronutrient composition for research, education, and software development.
* Hypothesis generation for subsequent experimental work.
* Reproducibility benchmarking of alternative insulin-response surrogates.

**Not intended for:** diagnosis, treatment, dosing decisions, individual-level clinical prediction, or any clinical decision-making.

## Reference standard

NIS is calibrated against the **white-bread-referenced Food Insulin Index (FII)** of Holt et al. (1997), extended by Bell (2014 PhD thesis), Bao (2009, 2011), Nilsson (2004), Boirie (1997), Trichopoulou (2003), and Sahyoun (2008). Pure glucose has a Holt-FII of ≈ 100; white bread is the reference anchor at 100. **NIS values are not interchangeable with glucose-referenced insulinaemic-index measurements** reported in other literature.

---

## Install

```bash
pip install nutramilo-nis
```

Optional extras: `"[validation]"` (numpy / pandas / scipy), `"[dev]"` (pytest, ruff, coverage).

## Quick start

```python
from nutramilo_nis import compute_nis

result = compute_nis(
    carbs_g=35, protein_g=30, fat_g=15, fiber_g=8,
    fat_type="mixed", protein_type="mixed",     # defaults — matches worked examples
)

print(result.nis_percent)   # → 55.4
print(result.tier)          # → "Medium"
print(result.contributions) # → {"carbs": 26.19, "protein": 11.93, "fat": 10.84, "fiber": -5.49}
```

JSON-serialisable via `.to_dict()`.

## Worked examples

Default `mixed` source-type, calibration on (slope = 0.7275, intercept = 8.111).

| Plate | C / P / F / Fb (g) | NIS % | Tier |
|---|---|---|---|
| White bread, lean cheese, butter | 50 / 12 / 8 / 1 | **77.3** | High |
| Salmon + quinoa + broccoli | 35 / 30 / 15 / 8 | **55.4** | Medium |
| Plain Greek yogurt + walnuts | 8 / 18 / 14 / 2 | **50.6** | Medium |
| Black bean & spinach bowl | 30 / 14 / 6 / 13 | **44.3** | Moderate |
| Avocado-omelette + side salad | 6 / 18 / 22 / 5 | **42.0** | Moderate |

---

## Mathematical methodology (five-step pipeline, v1.1.9)

1. **Per-1000 kJ normalisation.** Compute total energy with Atwater factors `E = 17·C + 17·P + 37·F` (kJ per g). Scale all macro quantities by `1000 / max(50, E)` g per 1000 kJ.
2. **Linear regression layer.** Ordinary least-squares with no intercept. Coefficients (per 1000 kJ):

   | Feature | Coefficient |
   |---|---:|
   | net-carbs (carbs − fibre, clipped ≥ 0) | **+1.61** |
   | protein | **+0.66** |
   | fat | **+1.20** |
   | fibre | **−1.14** |

   Protein and fat are multiplied by **source-type modifiers** before regression contribution:

   | Source type | `_PROTEIN_TYPE_MULT` | `_FAT_TYPE_MULT` |
   |---|---:|---:|
   | plant | 0.55 | 0.45 |
   | mixed (default) | 1.00 | 1.00 |
   | animal | 1.30 | 1.25 |

   When `sugar_g` > 0, approximately 50 % of sugar is treated as fructose and multiplied by `FRUCTOSE_MULT = 0.30` (Stanhope 2009 / Le 2008).
3. **Pure-fat extrapolation guard.** When `(net-carb + protein) / 1000 kJ < 5` g, the regression output is scaled by `0.15×` (serving-invariant since v1.1.1).
4. **Cross-cohort linear calibration.** `obs ≈ 0.7275 × raw + 8.111`, fit on **all 63** cross-cohort validation rows. Opt-out via `apply_calibration=False`.
5. **Optional Holt cross-track + clinical-tier floor.** `Final NIS = max(regression_cal, holt, tier_floor)`, clamped `[0, 100]`.

## Input variables

| Argument | Type | Default | Description |
|---|---|---|---|
| `carbs_g` | `float` | — | Total carbohydrate grams |
| `protein_g` | `float` | — | Protein grams |
| `fat_g` | `float` | — | Total fat grams |
| `fiber_g` | `float` | `0.0` | Dietary fibre grams |
| `insulin_impact_tier` | `"low" / "medium" / "high"` | `"low"` | Clinical floor band |
| `il_total_g` | `float \| None` | `None` | Pre-computed Insulin Load grams; enables Holt cross-track |
| `fat_type` | `"plant" / "mixed" / "animal"` | `"mixed"` | Fat-source multiplier |
| `protein_type` | `"plant" / "mixed" / "animal"` | `"mixed"` | Protein-source multiplier |
| `sugar_g` | `float` | `0.0` | Total sugars (if specified, ≈ 50 % treated as fructose) |
| `apply_calibration` | `bool` | `True` | Apply cross-cohort linear calibration |

## Output interpretation (`NisResult`)

| Field | Meaning |
|---|---|
| `nis_percent` | 0–100 score on the white-bread-referenced Holt-FII scale |
| `tier` | `Low` / `Moderate` / `Medium` / `High` / `Very high` |
| `tier_color` | Hex colour for UI |
| `piru` | Predicted Insulin Response Unit (regression layer raw) |
| `regression_pct`, `holt_pct`, `tier_floor_pct` | Component values before taking the max |
| `contributions` | Per-macro absolute contribution to `piru` |
| `nis_version` | `"1.1.9"` |
| `coefficients_date` | ISO date the coefficients were regressed |
| `citation` | Citation metadata string (see `CITATION.cff`) |

Use `result.to_dict()` for JSON serialisation.

## Training-data provenance

**Training CSV:** `HoltBellBao_v1_frozen_2026.csv`
**Rows:** **151** (zero exact normalised-name duplicates, zero exact macro-tuple duplicates)
**SHA-256:** `b41eb157661b2d8ad0f1e2bd0447f7cb61dfc460bb27bff754a59f3f50a2aaec`

OLS regression on all 151 rows reproduces the deployed coefficients (1.61 / 0.66 / 1.20 / −1.14) to two decimal places; full-precision OLS output is `(1.6121954, 0.6587755, 1.1976358, −1.1401008)`. An earlier manifest line referred to an *"effective n = 147 after duplicate removal"*; that row-exclusion rule **cannot be reconstructed** from the frozen artefacts and is therefore marked **UNRESOLVED**. The 2-decimal-place agreement establishes reproducibility to the published precision only — it does not prove methodological equivalence with any historical 147-row procedure.

## Calibration methodology

The single-slope / single-intercept post-hoc calibration `obs ≈ 0.7275 × raw + 8.111` was **fit on all 63** cross-cohort validation rows. Therefore the calibration-fit set entirely contains the n = 25 subset and the n = 9 non-overlap subset used for evaluation. Users who need a calibration-leakage-free estimate can run the package with `apply_calibration=False` and apply their own calibration externally.

## Evaluation results

MAE / RMSE / Pearson r of NIS (0–100) against Holt-FII observations. Bootstrap CIs: `SEED = 20260227, N = 2000`.

| Regime | Protocol | n | MAE | RMSE | Bias | Pearson r | 95 % MAE CI |
|---|---|---:|---:|---:|---:|---:|---|
| Full pooled literature cohort | fixed production calibration | **63** | **14.27** | 19.19 | −0.42 | **0.773** | [11.39, 17.51] |
| Non-Holt subset (citation ≠ Holt 1997) | fixed production calibration | **25** | **10.20** | 13.46 | +2.82 | **0.826** | [7.06, 13.70] |
| Non-Holt subset | leave-one-out refit calibration | **25** | **11.72** | 14.50 | +2.00 | **0.799** | — |
| Algorithmically filtered non-overlap subset | fixed production calibration | **9** | **12.81** | 17.10 | +1.83 | **0.447** | [5.74, 20.28] |

**Paired Wilcoxon signed-rank** (baseline vs full NIS on non-Holt n = 25): W = 55.5, z = −2.89, **p = 0.003822** (two-sided, continuity-corrected).

**Important framing.** The non-Holt n = 25 subset is out-of-sample relative to the OLS regression step but is **not** independent of the single-slope / single-intercept calibration step, which was fit on all 63 validation rows. The LOO-refit row quantifies the empirical optimism attributable to that calibration leakage (+1.52 MAE). The 9-row "algorithmically filtered non-overlap" subset is defined by normalised-name, alias, macro-tuple, and publication-manifest non-overlap criteria; **experimental independence at the primary-source level is not fully established**.

## Reproducibility

```bash
python -m venv .venv && . .venv/bin/activate
pip install --no-cache-dir nutramilo-nis==1.1.9 numpy pandas scikit-learn pytest

# 18/18 bundled test-suite
python -m pytest tests -v

# Full v4 reproducibility pack (if downloaded):
python verify_nis.py        # from nutramilo_nis_public_release_verification.zip
```

Package artefact hashes:

| File | SHA-256 |
|---|---|
| `nutramilo_nis-1.1.9-py3-none-any.whl` | `7d4c29cc533c3fd43447666500b76fee851f536bf91577ea54777e2125c533d6` |
| `nutramilo_nis-1.1.9.tar.gz` | `75da8335938d7876430c873c8be0973197ff06a3bce199ceef31beb77878ca7d` |

## Scientific limitations

1. **No independent external validation.** No cohort collected outside the training publications is included in this release. The non-Holt subset overlaps the calibration-fit set by 25/63 = 39.68 %.
2. **Training-cohort size is unresolved at full methodological precision.** The frozen CSV contains 151 rows; the "effective n = 147" manifest claim is unreconstructible from the shipped artefacts.
3. **The n = 9 non-overlap subset is algorithmic, not experimentally verified** at the primary-source level. Reported as a lower-bound estimate under stricter non-overlap criteria; Pearson r = 0.447 has a wide bootstrap CI reflecting the small sample.
4. **NIS is bound to the Holt-FII reference standard.** It is not interchangeable with glucose-referenced indices and does not correspond to continuous-glucose-monitoring (CGM) response measures.
5. **Pure-fat and pure-protein meals** are explicitly down-weighted by the pure-fat guard (step 3). This is a conservative regularisation, not an empirical finding from large pure-fat cohorts.

## Citation and DOI

Please cite both the Zenodo record and this repository:

* Zenodo DOI: [`10.5281/zenodo.20571802`](https://doi.org/10.5281/zenodo.20571802)
* GitHub: <https://github.com/axilla-score/nutramilo-nis>
* Full citation metadata: see `CITATION.cff`.

## Disclaimer

NIS is an **exploratory computational surrogate** for the white-bread-referenced Food Insulin Index of Holt et al. 1997 and derivative literature. It estimates, from macronutrient composition alone, how a meal would rank on that historical index — **not** the user's individual postprandial insulin AUC, glycaemic response, or any clinical outcome.

NIS has **not** undergone prospective clinical validation on any patient cohort. It is intended for research, education, software development, and comparative hypothesis generation. It is **not** a medical device under EU MDR 2017/745 or US 21 CFR 820, is **not** intended for diagnosis, treatment, or dosing decisions, and does **not** replace professional clinical judgement.

Users with diabetes, hypoglycaemia, or on insulin therapy must consult a qualified clinician before acting on NIS outputs.

## Roadmap

* **v1.x** — patch fixes only; coefficients **never** change.
* **v2.0.x** — prospective CGM / independent-cohort re-regression (required for "externally validated" status).

## Licence

[Apache 2.0](LICENSE) — see `NOTICE.txt` for the mandatory citation clause.
