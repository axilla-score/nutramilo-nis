# nutramilo-nis

[![Python ≥ 3.9](https://img.shields.io/badge/python-≥3.9-green.svg)](https://python.org)
<!-- DOI badge will be added after publication -->
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI downloads](https://img.shields.io/pypi/dm/nutramilo-nis.svg)](https://pypi.org/project/nutramilo-nis/)
[![Status: exploratory-methodology](https://img.shields.io/badge/status-exploratory--methodology-yellow.svg)](#)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-purple.svg)](https://github.com/astral-sh/ruff)

> **Reference implementation of the Nutramilo Insulin Score (NIS)** —
> an open-source algorithm designed to estimate the relative insulinogenic
> potential of a meal from its nutritional composition.
> NIS is intended for research, educational use, software development,
and exploratory nutritional analysis. It should not be interpreted as a
clinically validated predictor of postprandial insulin response.
> ⚠️ Scientific status. NIS v1.1.8 represents an exploratory methodology.
The algorithm is intended for comparative analysis of meals and hypothesis
generation rather than diagnostic or therapeutic decision-making.

---

## ✨ Why NIS?

| Property | Holt Food Insulin Index (FII) | **NIS v1.1.8** |
|---|---|---|
| In-vivo insulin AUC measurement required | ✅ Yes | ❌ No — **composition only** |
| Suitable for mobile apps & CGM-less use | ❌ No | ✅ Yes |
| Frozen, versioned coefficients | ❌ No | ✅ Yes (Apache 2.0, since v1.0) |
| Open dataset (SHA-256-verified) | ❌ No | ✅ Yes (Zenodo on release) |
| Out-of-sample evaluation reported | Partial | ✅ Yes (n = 25 hold-out) |
| Externally validated on fresh CGM cohort | n/a | ❌ **Not yet** — see technical documentation |

## Scientific Status

NIS has been evaluated during development using internal validation
procedures and independent test subsets.

The methodology is intended to provide a transparent, reproducible, and
open framework for estimating relative meal insulinogenicity from
nutritional composition.

Users should interpret outputs as comparative estimates rather than direct
physiological measurements.

Future independent validation studies may further clarify the strengths,
limitations, and potential applications of the methodology.


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
print(result.citation)
# → "See CITATION.cff for citation metadata."
```

JSON-serialisable for APIs:

```python
import json
print(json.dumps(result.to_dict(), indent=2))
```

## 🧪 Worked examples

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

## 📐 Algorithm (5-step pipeline, v1.1.8)

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
> overlap, see see project documentation).  All inferential claims in v1.1.8 are
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
| `insulin_impact_tier` | `Literal["low","medium","high"]` | `"low"` | Clinical floor band |
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
| `citation` | `str` | Citation metadata string |

Use `.to_dict()` → JSON-serialisable.

## Reproducibility

| Artifact                | Availability                            |
| ----------------------- | --------------------------------------- |
| Source code             | Included in this repository             |
| Unit tests              | Included in the package                 |
| Coefficient definitions | Publicly documented in source code      |
| Example calculations    | Included in README and tests            |
| Version history         | Available through Git tags and releases |

All calculations are fully reproducible from the published source code and released package versions.

## ™ Trademark Notice

NIS, Nutramilo Insulin Score™, and Nutramilo™ may be used to identify
the project and associated materials.

The Apache 2.0 license applies to the software source code.

Commercial use of names, logos, and branding elements may be subject to
separate intellectual property rights where applicable.

## ⚖️ Disclaimer & regulatory framing

NIS is intended for **educational and research** purposes.
It is **not** a medical device, does **not** diagnose any disease, and should
**not** replace professional clinical judgement.


## 🏗️ Roadmap (semver-frozen)

- **v1.x** — patch fixes only; coefficients **never** change.
- **v2.0.x** — prospective CGM trial re-regression.


| GDPR | No personal data processed by the library itself |

## 🤝 NIS vs DIL — different questions, different units

NIS and DIL are **complementary, not interchangeable**:

| | **NIS** (per-meal) | **DIL** (per-meal & daily) |
|---|---|---|
| Question | *"How insulinogenic is THIS meal compared to pure glucose?"* | *"How many grams of carb-equivalent insulin load did I eat today?"* |
| Output | 0–100 % (intensity score) | grams of carb-equivalent (load) |
| Use-case | Compare two meals; rank foods on a phone; coach single-meal swaps | Daily budget tracking; weekly trend monitoring; clinical dosing-adjacent reasoning |
| Formula | 5-step pipeline with source-aware multipliers, pure-fat guard, cross-cohort calibration | `0.69 × protein + max(carbs − fiber, 0)` per food, summed across the day |
| Validation | exploratory out-of-sample evaluation reported in project documentation | OLS-stable across Ridge/LASSO; food-level coefficient frozen at 0.69 since 2026-02-10 |
| In this SDK | `compute_nis(...)` | not bundled — see `nutramilo-health` package or `services/dil_formula.py` in the Nutramilo platform |

If you need both layers (per-meal NIS for ranking + daily DIL for budget),
combine `compute_nis` here with the open `compute_dil` formula:
`DIL_g = max(0, 0.69·protein + max(0, carbs − fiber))`.

## 📜 Licence

[Apache 2.0](LICENSE) — see NOTICE for the mandatory citation clause.

## 💬 Contact

| For | Email |
|---|---|
| Research collaboration | research@nutramilo.bg |
| Trademark / commercial licensing | legal@nutramilo.bg |
| Bug reports & feature requests | https://github.com/axilla-score/nutramilo-nis/issues |
| General product info | https://nutramilo.com/science |
