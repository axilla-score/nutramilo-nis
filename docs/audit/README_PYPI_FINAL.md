# nutramilo-nis — PyPI long-description (final)

**Open-source algorithm for estimating the relative insulinogenic potential of meals from macronutrient composition.** Calibrated against the white-bread-referenced Food Insulin Index (FII) of Holt et al. 1997 and derivative literature.

> **Exploratory computational surrogate — not a medical device, not clinically validated, and not interchangeable with glucose-referenced insulinaemic-index measurements.**

## Install

```bash
pip install nutramilo-nis
```

## Use

```python
from nutramilo_nis import compute_nis
r = compute_nis(carbs_g=35, protein_g=30, fat_g=15, fiber_g=8)
print(r.nis_percent, r.tier)   # → 55.4 Medium
```

Full API docs and worked examples: <https://github.com/axilla-score/nutramilo-nis#api-reference>.

## Scientific status — v1.1.9

Exploratory methodology, evaluated against pooled literature FII observations. **No prospective clinical validation** on any patient cohort. All outputs must be interpreted as comparative estimates against the Holt-FII historical scale, not as physiological measurements.

### Evaluation (v4 Statistical Evidence Lock)

MAE / RMSE / Pearson r of NIS (0–100) against Holt-FII observations:

| Regime | n | MAE | RMSE | Pearson r |
|---|---:|---:|---:|---:|
| Full pooled literature cohort (fixed calibration) | 63 | 14.27 | 19.19 | 0.773 |
| Non-Holt subset (fixed calibration) | 25 | 10.20 | 13.46 | 0.826 |
| Non-Holt subset (leave-one-out refit calibration) | 25 | 11.72 | 14.50 | 0.799 |
| Algorithmically filtered non-overlap subset | 9 | 12.81 | 17.10 | 0.447 |

**Paired Wilcoxon** signed-rank (baseline vs full NIS on n = 25): **p = 0.003822** (two-sided).

**Important framing.** The non-Holt n = 25 subset is out-of-sample relative to the **regression** step but is **not** independent of the single-slope / single-intercept **calibration** step, which was fit on all 63 validation rows. The LOO-refit row quantifies the empirical optimism attributable to that calibration leakage (+1.52 MAE). The n = 9 "algorithmically filtered non-overlap" subset is defined by name, alias, macro-tuple, and publication-manifest non-overlap filters; experimental independence at the primary-source level has not been established.

## Training-data provenance

Regression coefficients `(net_carbs = +1.61, protein = +0.66, fat = +1.20, fiber = −1.14)` fit on `HoltBellBao_v1_frozen_2026.csv` (**n = 151 rows**, SHA-256 `b41eb157…a2aaec`). An earlier manifest line mentions "effective n = 147 after duplicate removal"; that row-exclusion rule is **unreconstructible** from the shipped artefacts and is flagged **UNRESOLVED** in the v4 Statistical Evidence Lock. The published 2-decimal-place coefficients are fully reproducible from the 151-row CSV.

## Reproducibility

* GitHub: <https://github.com/axilla-score/nutramilo-nis>
* Zenodo (DOI): <https://doi.org/10.5281/zenodo.20571802>
* Documentation: <https://nutramilo.com/science/nis>

```bash
pip install nutramilo-nis==1.1.9
python -m pytest tests -v   # 18/18 bundled tests
```

## Disclaimer

NIS is **not** a medical device under EU MDR 2017/745 or US 21 CFR 820. It is **not** intended for diagnosis, treatment, or dosing decisions and does not replace professional clinical judgement. Users with diabetes, hypoglycaemia, or on insulin therapy must consult a qualified clinician before acting on NIS outputs.

## Licence

Apache 2.0; see `NOTICE.txt` for the mandatory citation clause.

---

### Deployment note (for maintainer)

PyPI releases are immutable, so this description cannot replace the existing `1.1.9` long-description in place. Two options:

* **Option A (recommended once the GitHub README is merged):** publish a documentation-only release `v1.1.10` with identical source bytes, updated `README.md` (and hence PyPI long-description) and `pyproject.toml` `[project.urls].Issues` typo fix.
* **Option B:** keep PyPI at `1.1.9` unchanged. The PyPI project page already links to the GitHub Homepage, which users reach for the corrected documentation.

No publish action is taken by this audit.
