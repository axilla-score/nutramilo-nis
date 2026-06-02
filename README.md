# nutramilo-nis

[![PyPI version](https://img.shields.io/pypi/v/nutramilo-nis.svg)](https://pypi.org/project/nutramilo-nis/)
[![Python ≥ 3.9](https://img.shields.io/badge/python-≥3.9-green.svg)](https://python.org)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![DOI](https://img.shields.io/badge/DOI-10.XXXX%2Fijmrcr.2026.NIS-orange.svg)](https://doi.org/10.XXXX/ijmrcr.2026.NIS)
[![PyPI downloads](https://img.shields.io/pypi/dm/nutramilo-nis.svg)](https://pypi.org/project/nutramilo-nis/)
[![Status: exploratory-methodology](https://img.shields.io/badge/status-exploratory--methodology-yellow.svg)](#)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-purple.svg)](https://github.com/astral-sh/ruff)

> **Reference implementation of the Nutramilo Insulin Score (NIS™)** —
> an open, **exploratory** macronutrient-derived insulinogenic surrogate
> computable from any meal composition.  Trained on the Holt–Bell–Bao
> Food Insulin Index cohort (n = 147) and evaluated on a strictly
> out-of-sample subset (n = 25).
>
> ⚠️ **Positioning.** NIS v1.1.5 is an **exploratory methodology study**,
> not an externally validated predictive model.  A prospective CGM trial
> is the planned confirmatory step (see manuscript §4.2 + Part II).

---

## ✨ Why NIS?

| Property | Holt Food Insulin Index (FII) | **NIS v1.1.5** |
|---|---|---|
| In-vivo insulin AUC measurement required | ✅ Yes | ❌ No — **composition only** |
| Suitable for mobile apps & CGM-less use | ❌ No | ✅ Yes |
| Frozen, versioned coefficients | ❌ No | ✅ Yes (Apache 2.0, since v1.0) |
| Mandatory citation in derivatives | ❌ No | ✅ Yes (NOTICE clause) |
| Open dataset (SHA-256-verified) | ❌ No | ✅ Yes (Zenodo on release) |
| Out-of-sample evaluation reported | Partial | ✅ Yes (n = 25 hold-out) |
| Externally validated on fresh CGM cohort | n/a | ❌ **Not yet** — see Part II |

**Headline metrics (v1.1.5 on n = 25 strictly out-of-sample subset):**

| Pipeline | OOS MAE | 95 % bootstrap CI | Pearson r |
|---|---|---|---|
| v1.0.0 baseline | 17.49 | [14.22, 21.12] | 0.778 |
| **v1.1.5 full** | **10.20** | **[7.06, 13.70]** | **0.826** |

Paired Wilcoxon (n = 25 OOS): **W = 55.5, z = −2.879, p = 0.00399**.
Bootstrap 95 % CIs do not overlap.  Bland–Altman LoA on the OOS subset
is **±37.6 %-points** — wide enough that NIS is **best used for
relative meal comparison within the same subject**, not for absolute
insulin AUC prediction.

## 📦 Install

```bash
pip install nutramilo-nis
```

Optional extras:

```bash
pip install "nutramilo-nis[validation]"   # numpy / pandas / scipy for re-running the regression notebook
pip install "nutramilo-nis[dev]"          # pytest, ruff, coverage
```

## 🚀 Quick start — 30 seconds

```python
from nutramilo_nis import compute_nis

# A balanced lunch: salmon + quinoa + broccoli
result = compute_nis(
    carbs_g=35,
    protein_g=30,
    fat_g=15,
    fiber_g=8,
)

print(result.nis_percent)   # → 55.4
print(result.tier)          # → "Medium"
print(result.tier_color)    # → "#F59E0B"
print(result.contributions) # → {"carbs": 26.19, "protein": 11.93, "fat": 10.84, "fiber": -5.49}
print(result.citation)      # → "Inkov I, et al. (2026). NIS … IJMRCR …"
```

JSON-serialisable for APIs:

```python
import json
print(json.dumps(result.to_dict(), indent=2))
```

## 🧪 Worked examples (from the paper)

> Computed with default `mixed` source-type and calibration **on**
> (slope = 0.7275, intercept = 8.111).  See `tests/test_nis_v1_1_*.py`
> for the full pinned numerical regression suite.

| Plate | C / P / F / Fb (g) | NIS % | Tier |
|---|---|---|---|
| White bread, lean cheese, butter | 50 / 12 / 8 / 1 | **77.3** | High |
| Salmon + quinoa + broccoli | 35 / 30 / 15 / 8 | **55.4** | Medium |
| Plain Greek yogurt + walnuts | 8 / 18 / 14 / 2 | **50.6** | Medium |
| Black bean & spinach bowl | 30 / 14 / 6 / 13 | **44.3** | Moderate |
| Avocado-omelette + side salad | 6 / 18 / 22 / 5 | **42.0** | Moderate |

## 📐 Algorithm (5-step pipeline, v1.1.5)

1. **Per-1000-kJ normalisation** using Atwater factors (17·C + 17·P + 37·F kJ/g).
2. **Linear regression layer** — independent OLS on the frozen
   `HoltBellBao_v1_frozen_2026.csv` cohort (n = 147 foods).
   Coefficients exposed as `NIS_COEFFICIENTS`:
   `carbs = +1.61 · protein = +0.66 · fat = +1.20 · fiber = −1.14` (per 1000 kJ).
   Protein and fat scaled by **source-type multipliers** (plant/mixed/animal:
   protein 0.55/1.00/1.30, fat 0.45/1.00/1.25).
3. **Pure-fat extrapolation guard** — when `(net-carb + protein) / 1000 kJ < 5 g`
   the regression output is scaled by `0.15×` (energy-normalised, serving-
   invariant since v1.1.1).
4. **Cross-cohort linear calibration** — `obs ≈ 0.7275 × pct + 8.111`
   (fit on the n = 63 cross-cohort validation set; opt-out via
   `apply_calibration=False`).
5. **Optional Holt cross-track + clinical-tier floor**, then
   **`Final NIS = max(regression_cal, holt, floor)`**, clamped [0, 100].

> **Note on validation framing.**  The n = 147 training cohort and the
> n = 63 cross-cohort calibration set share Holt 1997 foods (derivational
> overlap, see manuscript §4.3 L1).  All inferential claims in v1.1.5 are
> therefore restricted to the **n = 25 strictly out-of-sample subset**
> (Bao 2011, Nilsson 2004, Boirie 1997, Trichopoulou 2003, Sahyoun 2008).

## 📘 API reference

### `compute_nis(carbs_g, protein_g, fat_g, fiber_g=0.0, *, insulin_impact_tier="low", il_total_g=None, fat_type="mixed", protein_type="mixed", sugar_g=0.0, apply_calibration=True) → NisResult`

| Argument | Type | Default | Description |
|---|---|---|---|
| `carbs_g` | `float` | — | Total carbohydrate grams (net carb = `carbs_g − fiber_g`) |
| `protein_g` | `float` | — | Protein grams |
| `fat_g` | `float` | — | Total fat grams |
| `fiber_g` | `float` | `0.0` | Dietary fibre grams (blunts response) |
| `insulin_impact_tier` | `Literal["low","medium","high"]` | `"low"` | Clinical floor band (paper §2.4) |
| `il_total_g` | `Optional[float]` | `None` | Pre-computed Insulin Load grams — activates the Holt cross-track |
| `fat_type` | `Literal["plant","mixed","animal"]` | `"mixed"` | Fat-source multiplier — plant 0.45, mixed 1.00, animal 1.25 (Holt 1997 / Trichopoulou 2003) |
| `protein_type` | `Literal["plant","mixed","animal"]` | `"mixed"` | Protein-source multiplier — plant 0.55, mixed 1.00, animal 1.30 (Nilsson 2004 / Boirie 1997) |
| `sugar_g` | `float` | `0.0` | Total sugars; when supplied, ~50 % is treated as fructose (×0.30 insulinogenicity per Le 2008) |
| `apply_calibration` | `bool` | `True` | Apply cross-cohort linear calibration (slope 0.7275, intercept 8.111). Set `False` to recover raw v1.0.1 regression output |

### `NisResult` (frozen `dataclass`)

| Field | Type | Description |
|---|---|---|
| `nis_percent` | `float` | Final NIS, 0–100 |
| `tier` | `str` | `"Low"` / `"Moderate"` / `"Medium"` / `"High"` / `"Very high"` |
| `tier_color` | `str` | Hex colour for UI (Tailwind-compatible) |
| `piru` | `float` | Predicted Insulin Response Unit (regression layer raw) |
| `regression_pct` | `float` | Pure regression output (0–100) |
| `holt_pct` | `float` | Holt cross-track output (0–100) |
| `tier_floor_pct` | `float` | Clinical-tier floor applied |
| `contributions` | `dict[str, float]` | Per-macro absolute contribution to PIRU |
| `nis_version` | `str` | Frozen version (e.g. `"1.0.0"`) |
| `coefficients_date` | `str` | Date coefficients were regressed (ISO) |
| `citation` | `str` | Required academic citation |

Use `.to_dict()` → JSON-serialisable.

## 🔬 Reproducibility

| Artifact | Location |
|---|---|
| Frozen training dataset | Zenodo DOI [10.5281/zenodo.XXXXXX](https://zenodo.org/) |
| Regression notebook | [`notebooks/independent_regression_v2.ipynb`](https://github.com/nutramilo/nutramilo-nis) |
| SHA-256 of v1.0 dataset | `b41eb157661b2d8ad0…` (paper § 2.2) |
| Unit tests | `pytest -q` — 23 tests, all should pass |
| Figures (PNG + TIFF 300dpi) | Paper supplement, Figs 1–6 |

## 📖 Paper

> **Inkov, I., et al.** (2026). "Nutramilo Insulin Score (NIS): An Open,
> Macronutrient-Derived Algorithm for Predicting Postprandial Insulinaemic
> Response — Development and Validation Against the Holt Food Insulin Index."
> *International Journal of Medical Reviews and Case Reports*, in press.
> DOI: [10.XXXX/ijmrcr.2026.NIS](https://doi.org/10.XXXX/ijmrcr.2026.NIS)

**Pre-print:** [medRxiv 2026.02.XXXXXX](https://medrxiv.org/)

If you use NIS in research, **please cite the paper** (Apache 2.0 + NOTICE).

## ™ Trademark notice

`NIS™`, `Nutramilo Insulin Score™`, and `Nutramilo™` are trademarks of
**International Sci Ink Press Ltd EOOD** (EIK 205414288, Sofia, Bulgaria),
filed at the EUIPO.

The Apache 2.0 licence covers the **code** — *not* the trademarks. For
commercial use of the marks in branding/marketing, contact
[legal@nutramilo.bg](mailto:legal@nutramilo.bg).

## ⚖️ Disclaimer & regulatory framing

NIS is intended for **educational and research** purposes.
It is **not** a medical device, does **not** diagnose any disease, and should
**not** replace professional clinical judgement.

| Framework | Classification |
|---|---|
| EU MDR 2017/745 | **Not a medical device** |
| EU AI Act 2024/1689 | **Limited risk** (Art. 50 — transparency only) |

## 🏗️ Roadmap (semver-frozen)

- **v1.x** — patch fixes only; coefficients **never** change.
- **v2.0.x** — prospective CGM trial re-regression (manuscript Part II,
  pre-registered at OSF before data collection).


| GDPR | No personal data processed by the library itself |

## 🤝 NIS vs DIL — different questions, different units

NIS and DIL are **complementary, not interchangeable**:

| | **NIS** (per-meal) | **DIL** (per-meal & daily) |
|---|---|---|
| Question | *"How insulinogenic is THIS meal compared to pure glucose?"* | *"How many grams of carb-equivalent insulin load did I eat today?"* |
| Output | 0–100 % (intensity score) | grams of carb-equivalent (load) |
| Use-case | Compare two meals; rank foods on a phone; coach single-meal swaps | Daily budget tracking; weekly trend monitoring; clinical dosing-adjacent reasoning |
| Formula | 5-step pipeline with source-aware multipliers, pure-fat guard, cross-cohort calibration | `0.69 × protein + max(carbs − fiber, 0)` per food, summed across the day |
| Validation | n = 25 OOS Pearson r = 0.83, MAE = 10.2 | OLS-stable across Ridge/LASSO; food-level coefficient frozen at 0.69 since 2026-02-10 |
| In this SDK | `compute_nis(...)` | not bundled — see `nutramilo-health` package or `services/dil_formula.py` in the Nutramilo platform |

If you need both layers (per-meal NIS for ranking + daily DIL for budget),
combine `compute_nis` here with the open `compute_dil` formula:
`DIL_g = max(0, 0.69·protein + max(0, carbs − fiber))`.

## 📜 Licence

[Apache 2.0](LICENSE) — see [`NOTICE`](NOTICE) for the mandatory citation clause.

## 💬 Contact

| For | Email |
|---|---|
| Research collaboration | research@nutramilo.bg |
| Trademark / commercial licensing | legal@nutramilo.bg |
| Bug reports & feature requests | [github.com/nutramilo/nutramilo-nis/issues](https://github.com/nutramilo/nutramilo-nis/issues) |
| General product info | https://nutramilo.com/science |
