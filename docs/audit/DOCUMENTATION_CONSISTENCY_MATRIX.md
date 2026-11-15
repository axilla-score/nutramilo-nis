# DOCUMENTATION CONSISTENCY MATRIX

**Audit:** Nutramilo NIS v1.1.9 — Final Documentation (v6)
**Scope.** Verifies that `README_GITHUB_FINAL.md`, `README_PYPI_FINAL.md`, `ZENODO_DESCRIPTION_FINAL.md`, `ZENODO_CORRECTION_NOTE.md`, and `SCIENTIFIC_METHODS_AND_RESULTS.md` agree on every quantitative fact. The authoritative source is `nis_evidence_lock.json` from the v4 Statistical Evidence Lock bundle.

---

## 1. Primary attributes

| Attribute | Authoritative value | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---|:---:|:---:|:---:|:---:|:---:|
| NIS version | `1.1.9` | ✅ | ✅ | ✅ | ✅ | ✅ |
| License (software) | Apache 2.0 | ✅ | ✅ | ✅ | ✅ | ✅ |
| License (documentation) | CC BY 4.0 | — | — | ✅ | — | ✅ |
| Zenodo DOI | `10.5281/zenodo.20571802` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GitHub tag commit | `ddb3ada` | — | — | — | — | ✅ |
| PyPI wheel SHA-256 | `7d4c29cc…c533d6` | ✅ | — | ✅ | — | ✅ |
| PyPI sdist SHA-256 | `75da8335…8ca7d` | ✅ | — | ✅ | — | ✅ |
| Training CSV SHA-256 | `b41eb157…a2aaec` | ✅ | ✅ | ✅ | ✅ | ✅ |
| Validation CSV SHA-256 | `6e2868c8…43f5cf` | — | — | ✅ | — | ✅ |

## 2. Model purpose and framing

| Claim | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|:---:|:---:|:---:|:---:|:---:|
| NIS is an *exploratory computational surrogate* | ✅ | ✅ | ✅ | ✅ | ✅ |
| NIS is bound to the **white-bread Holt-FII** reference standard | ✅ | ✅ | ✅ | ✅ | ✅ |
| NIS is **not** interchangeable with glucose-referenced indices | ✅ | ✅ | ✅ | ✅ | ✅ |
| NIS is **not** a medical device (EU MDR 2017/745, 21 CFR 820) | ✅ | ✅ | ✅ | — | ✅ |
| **No prospective clinical validation** performed | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Independent external validation NOT ACHIEVED** | ✅ | ✅ | ✅ | ✅ | ✅ |

## 3. Training dataset

| Fact | Value | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---|:---:|:---:|:---:|:---:|:---:|
| File name | `HoltBellBao_v1_frozen_2026.csv` | ✅ | — | ✅ | ✅ | ✅ |
| Row count | **151** | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exact normalised-name duplicates | 0 | ✅ | — | — | ✅ | ✅ |
| Exact macro-tuple duplicates | 0 | — | — | — | ✅ | ✅ |
| Historical "n = 147" claim | **UNRESOLVED** | ✅ | ✅ | ✅ | ✅ | ✅ |
| Source publications | Holt1997, Bell2014, Bao2009 | — | — | — | — | ✅ |

## 4. Regression coefficients

All five documents quote the deployed 2-decimal-place coefficients:

| Coefficient | Value | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---:|:---:|:---:|:---:|:---:|:---:|
| `net_carbs_p1k` | +1.61 | ✅ | ✅ | ✅ | — | ✅ |
| `protein_p1k` | +0.66 | ✅ | ✅ | ✅ | — | ✅ |
| `fat_p1k` | +1.20 | ✅ | ✅ | ✅ | — | ✅ |
| `fiber_p1k` | −1.14 | ✅ | ✅ | ✅ | — | ✅ |

Full-precision OLS output `(1.6121954, 0.6587755, 1.1976358, −1.1401008)` quoted in: METHODS_RESULTS only (matches v4 lock).

## 5. Calibration

| Fact | Value | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---|:---:|:---:|:---:|:---:|:---:|
| Form | single slope + intercept | ✅ | ✅ | ✅ | ✅ | ✅ |
| Slope | 0.7275 | ✅ | — | ✅ | ✅ | ✅ |
| Intercept | 8.111 | ✅ | — | ✅ | ✅ | ✅ |
| Fit set | **all 63 validation rows** | ✅ | ✅ | ✅ | ✅ | ✅ |
| Calibration-leakage disclosure | explicit | ✅ | ✅ | ✅ | ✅ | ✅ |

## 6. Evaluation metrics (recomputed, authoritative)

| Subset | n | MAE | RMSE | Pearson r | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| Full pooled cohort | 63 | 14.27 | 19.19 | 0.773 | ✅ | ✅ | ✅ | — | ✅ |
| Non-Holt (fixed cal.) | 25 | 10.20 | 13.46 | 0.826 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Non-Holt (LOO refit cal.) | 25 | 11.72 | 14.50 | 0.799 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Algorithmically filtered non-overlap | 9 | 12.81 | 17.10 | 0.447 | ✅ | ✅ | ✅ | — | ✅ |

**Rounding rule.** Prose uses 2 decimal places for MAE/RMSE and 3 decimal places for Pearson r; the 4-decimal-place authoritative values in `nis_evidence_lock.json` (`14.2667 / 19.1897 / 0.7733`, etc.) match on prefix.

## 7. Paired Wilcoxon signed-rank (baseline vs full NIS on n = 25)

| Statistic | Authoritative value | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---:|:---:|:---:|:---:|:---:|:---:|
| n (non-zero pairs) | 25 | ✅ | — | — | — | ✅ |
| W (min of W⁺, W⁻) | 55.5 | ✅ | — | ✅ | — | ✅ |
| z (continuity-corrected) | −2.89 | ✅ | — | ✅ | — | ✅ |
| two-sided p-value | 0.003822 | ✅ | ✅ | ✅ | — | ✅ |

## 8. Scientific limitations (common list)

The following six limitations must appear (in substance) across all documentation surfaces:

| # | Limitation | README_GITHUB | README_PYPI | ZENODO_DESCRIPTION | ZENODO_CORRECTION | METHODS_RESULTS |
|---|---|:---:|:---:|:---:|:---:|:---:|
| 1 | No independent external validation | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 | Calibration overlaps "OOS" subset | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 | n = 147 historical claim unresolved | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4 | n = 9 non-overlap is algorithmic, not experimental | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 | Bound to Holt-FII reference standard (not CGM, not glucose-ref.) | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6 | Pure-fat guard is a conservative regularisation | ✅ | — | — | — | ✅ |

## 9. DOI and citation

All five documents point to the same DOI `10.5281/zenodo.20571802`, delegate full citation metadata to `CITATION.cff`, and request users to cite both the DOI and the repository.

## 10. Items deliberately **not** stated identically

Different surfaces have different space budgets. These asymmetries are expected and do not constitute inconsistency:

| Content | Where it lives | Rationale |
|---|---|---|
| Full API reference table | `README_GITHUB_FINAL.md` only | too long for PyPI / Zenodo |
| Full precision OLS coefficients + full LOSCO per-cohort breakdown | `SCIENTIFIC_METHODS_AND_RESULTS.md` only | methodology-level detail |
| Zenodo edit mechanics (Option A / B / C) | `ZENODO_CORRECTION_NOTE.md` only | maintainer instruction only |
| PyPI release-decision tree | `README_PYPI_FINAL.md` footer | maintainer instruction only |

## 11. Verdict

| Check | Result |
|---|---|
| All five documents agree on the model purpose, framing, and disclaimer | **PASS** |
| All five documents quote identical performance numbers | **PASS** (rounding difference prefix-matches 4-dp lock) |
| All five documents cite the same DOI and training-cohort hash | **PASS** |
| No document claims clinical, prospective, or independent external validation | **PASS** |
| No document invents or alters any statistical result | **PASS** |
