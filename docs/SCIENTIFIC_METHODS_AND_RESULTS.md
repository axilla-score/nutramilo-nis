# Nutramilo Insulin Score: Model Development, Calibration, and Internal Evaluation

**A pre-manuscript technical report (v1.1.9)**

**Authors.** Inkov, I. et al. (co-authors per `CITATION.cff`).
**Affiliation.** International Sci Ink Press Ltd EOOD, Sofia, Bulgaria.
**Correspondence.** <inkov@nutramilo.bg>.
**Date.** 2026-02.
**Software version documented.** Nutramilo-NIS v1.1.9 (Zenodo DOI [`10.5281/zenodo.20571802`](https://doi.org/10.5281/zenodo.20571802); GitHub tag `nis-v1.1.9`; PyPI release 1.1.9).

> **Disclaimer.** This document is a methodological, pre-manuscript record intended as the foundation for a future peer-reviewed article. It does **not** claim clinical validation, prospective validation, or independent external validation. All performance figures below are **internal evaluation** results and must be read with the framing stated in §7 (Limitations).

---

## Abstract

The Nutramilo Insulin Score (NIS) v1.1.9 is an open, reproducible computational surrogate that estimates, from macronutrient composition alone, how a meal would rank on the white-bread-referenced Food Insulin Index (FII) of Holt et al. (1997) and its subsequent extensions. The model is a five-step pipeline: per-1000 kJ normalisation, a four-feature ordinary least-squares regression layer with source-type modifiers, a pure-fat extrapolation guard, a single-slope / single-intercept post-hoc linear calibration, and an optional Holt cross-track combined with a clinical-tier floor. Regression coefficients were fit on a frozen 151-row literature cohort; the deployed two-decimal-place coefficients `(net_carbs = +1.61, protein = +0.66, fat = +1.20, fiber = −1.14)` are reproducible from the archived CSV. The post-hoc calibration `obs ≈ 0.7275 × raw + 8.111` was fit on all 63 cross-cohort validation rows. Internal evaluation across three subsets yielded MAE values of 14.27 (n = 63), 10.20 (n = 25, non-Holt), and 12.81 (n = 9, algorithmically filtered non-overlap). Leave-one-out refit of the calibration on the non-Holt subset raised MAE from 10.20 to 11.72, quantifying the empirical optimism attributable to calibration leakage. A paired Wilcoxon signed-rank test confirmed statistically significant improvement over a pure-macro baseline on the non-Holt subset (p = 0.003822). Independent external validation remains an explicit roadmap item; no cohort outside the training publications is included in this release.

**Keywords.** Food Insulin Index, Holt-FII, insulin response, macronutrient-derived score, OLS, internal validation, reproducibility.

---

## 1. Scientific rationale

Postprandial insulin response varies systematically across foods for reasons that extend beyond carbohydrate content alone. Protein and fat each contribute to the insulin area-under-curve in a food-type-dependent manner, and dietary fibre attenuates the response. The Holt Food Insulin Index (Holt et al., 1997) remains the most widely referenced open scale that captures these effects across a diverse food set, extended by Bell (2014), Bao (2009, 2011), Nilsson (2004), Boirie (1997), Trichopoulou (2003), and Sahyoun (2008). However, the Holt-FII requires in-vivo insulin AUC measurement per food and is therefore impractical for app-level meal-by-meal computation.

The Nutramilo Insulin Score (NIS) is a composition-only surrogate for the Holt-FII scale. It targets three design properties absent in prior open implementations:

1. **Frozen, versioned coefficients** (reproducible across releases).
2. **Source-type awareness** (plant / mixed / animal multipliers for protein and fat).
3. **Open, SHA-256-verified training and calibration data** (archived on Zenodo).

NIS is intended for comparative meal ranking in research, educational, and software-development contexts. It is explicitly **not** intended as a clinical biomarker.

---

## 2. Model development

### 2.1 Pipeline overview

The NIS pipeline computes a 0–100 score in five stages:

1. **Per-1000 kJ normalisation** of macronutrient quantities using Atwater factors (17 kJ/g for carbohydrate and protein; 37 kJ/g for fat).
2. **Linear regression layer.** Ordinary least-squares without intercept; four features (net-carbs, protein, fat, fibre per 1000 kJ) with source-type modifiers applied to protein and fat.
3. **Pure-fat extrapolation guard** (0.15× down-weighting when net-carb + protein density falls below 5 g per 1000 kJ).
4. **Cross-cohort linear calibration** (single slope + intercept).
5. **Tier floor and clamp** (`max(regression_cal, holt, floor)`, clamped `[0, 100]`).

### 2.2 Source-type modifiers

Applied to the protein and fat per-1000 kJ terms before the regression contribution:

| Source type | `_PROTEIN_TYPE_MULT` | `_FAT_TYPE_MULT` |
|---|---:|---:|
| plant | 0.55 | 0.45 |
| mixed (default) | 1.00 | 1.00 |
| animal | 1.30 | 1.25 |

Rationale: plant-source protein and fat exhibit smaller insulinaemic effects than animal-source matter in the Holt-FII cohort and its extensions.

### 2.3 Fructose handling

When total sugars (`sugar_g`) are supplied, approximately 50 % of sugar is treated as fructose, with fructose multiplied by `FRUCTOSE_MULT = 0.30` (Le, 2008; Stanhope, 2009).

### 2.4 Pure-fat guard

When `(net-carb + protein) / 1000 kJ < 5 g`, the regression output is scaled by 0.15×. This conservative regularisation reflects the absence of large pure-fat insulin-AUC cohorts in the training data and prevents the model from extrapolating to very-low-carb, very-low-protein compositions.

---

## 3. Mathematical framework

Let `C, P, F, Fb` be grams of carbohydrate, protein, fat, and fibre respectively; `T` be the fat type ∈ {plant, mixed, animal}; `Q` be the protein type ∈ {plant, mixed, animal}; and `S` be sugar grams. Define

```
E     = max(50, 17·C + 17·P + 37·F)      [kJ]
scale = 1000 / E                          [1000·kJ⁻¹]
C'    = max(0, C − Fb) · scale            [g per 1000 kJ]
P'    = P · scale · μ_P(Q)
F'    = F · scale · μ_F(T)
Fb'   = Fb · scale
```

with `μ_P` and `μ_F` the source-type modifiers tabulated in §2.2.

**Regression layer (step 2):**

```
PIRU = max(0, 1.61·C' + 0.66·P' + 1.20·F' − 1.14·Fb')
pct  = PIRU/30 · 50                             if PIRU ≤ 30
     = 50 + min(50, (PIRU − 30)/45 · 50)        otherwise
```

**Pure-fat guard (step 3):** if `(max(0, C − Fb) + P)·scale < 5`, then `pct ← 0.15 · pct`.

**Calibration (step 4):** `pct_cal ← clip(0, 100, 0.7275·pct + 8.111)` — except for pure-fat meals, where the intercept is skipped.

**Final combination (step 5):** `NIS = clip(0, 100, max(pct_cal, holt_cross, tier_floor))`.

The implementation is the function `compute_nis` in `nutramilo_nis.nis`; it is bit-identical across the PyPI wheel, the PyPI sdist, and the GitHub tag `nis-v1.1.9` (SHA-256 of `nis.py`: `fa36213c…ef6e744`).

---

## 4. Data sources

### 4.1 Training cohort

| Property | Value |
|---|---|
| File | `HoltBellBao_v1_frozen_2026.csv` |
| Rows | **151** |
| SHA-256 | `b41eb157661b2d8ad0f1e2bd0447f7cb61dfc460bb27bff754a59f3f50a2aaec` |
| Source publications | Holt (1997), Bell (2014 PhD thesis), Bao (2009) |
| Observation unit | Holt-FII per food (white-bread-referenced, incremental AUC 2 h) |

Exhaustive audit of the frozen CSV identified **zero exact normalised-name duplicates** and **zero exact macro-tuple duplicates**. An earlier manifest annotation referring to *"effective n = 147 after duplicate removal"* is unreconstructible from the shipped artefacts and is flagged **`HISTORICAL_METHOD_UNRESOLVED`** in the v4 Statistical Evidence Lock. The published 2-decimal-place coefficients reproduce from OLS on all 151 rows; the full-precision OLS output is `(1.6121954, 0.6587755, 1.1976358, −1.1401008)`, which is a sufficient — but **not** necessary — condition for historical methodological equivalence. Readers should therefore read all training-cohort claims with the 2-decimal-place / unresolved-at-full-precision caveat.

### 4.2 Cross-cohort calibration + evaluation set

| Property | Value |
|---|---|
| File | `foods_v1_0_1_validation.csv` |
| Rows | 63 |
| SHA-256 | `6e2868c8a37e0b60c9a69249682528b540c3da4f6ecabb7e2a5a67d73443f5cf` |
| Source publications (n per citation) | Holt1997 (38), Bao2011 (14), Nilsson2004 (4), Trichopoulou2003 (3), Boirie1997 (2), Sahyoun2008 (2) |

---

## 5. Calibration

The single-slope / single-intercept calibration `pct_cal = 0.7275 · pct + 8.111` was fit on the **entire 63-row** cross-cohort validation set by ordinary least squares between the raw regression output `pct` and the Holt-referenced FII observation. The calibration therefore **pools** training-derivative foods (Holt 1997, n = 38) with non-training publications (n = 25). Consequently, any evaluation that re-uses rows from the calibration-fit set necessarily overlaps the data used to derive the calibration.

To quantify the empirical optimism caused by this calibration leakage, we also report **leave-one-out refit** of the calibration on the n = 25 subset (§6.2).

---

## 6. Statistical evaluation

All evaluation statistics were recomputed from the installed public PyPI package (`nutramilo-nis 1.1.9`, wheel SHA-256 `7d4c29cc…`) on the frozen validation CSV. Bootstrap 95 % confidence intervals use `SEED = 20260227, N = 2000`. All numbers are read verbatim from `nis_evidence_lock.json`.

### 6.1 Three internal regimes (fixed production calibration)

| Regime | Protocol | n | MAE | RMSE | Bias | Pearson r | 95 % MAE CI |
|---|---|---:|---:|---:|---:|---:|---|
| Full pooled literature cohort | all rows, production pipeline | **63** | 14.27 | 19.19 | −0.42 | 0.773 | [11.39, 17.51] |
| Non-Holt subset | `citation ≠ Holt1997` | **25** | 10.20 | 13.46 | +2.82 | 0.826 | [7.06, 13.70] |
| Algorithmically filtered non-overlap subset | non-Holt + no training name / alias / macro-tuple / publication-manifest overlap | **9** | 12.81 | 17.10 | +1.83 | 0.447 | [5.74, 20.28] |

### 6.2 Leave-one-out calibration refit (internal cross-validation)

With the four regression coefficients held fixed at their production values, the single calibration slope and intercept were refit on the remaining 62 rows for each held-out observation. Metrics restricted to the n = 25 non-Holt subset:

| Metric | Fixed calibration | LOO-refit calibration | Δ (LOO − fixed) |
|---|---:|---:|---:|
| MAE | 10.20 | **11.72** | +1.52 |
| RMSE | 13.46 | 14.50 | +1.04 |
| Pearson r | 0.826 | 0.799 | −0.027 |

LOO slope mean ± sd: 0.7266 ± 0.0073; LOO intercept mean ± sd: 8.1427 ± 0.4213. The ≈ 1.5-point MAE gap is the **empirical optimism** attributable to the calibration-leakage pathway while keeping the four regression coefficients fixed.

### 6.3 Paired Wilcoxon signed-rank test

Comparison of absolute prediction errors between the pure-macro baseline (default `mixed` source types, no calibration) and the full NIS pipeline on the non-Holt n = 25 subset:

| Statistic | Value |
|---|---:|
| n (non-zero pairs) | 25 |
| W (min of W⁺, W⁻) | 55.5 |
| W⁺ / W⁻ | 269.5 / 55.5 |
| z (continuity-corrected) | −2.89 |
| two-sided p-value | **0.003822** |

The improvement of the full NIS over the macro baseline is statistically significant on this slice.

### 6.4 Leave-one-source-cohort-out (LOSCO)

A cross-cohort protocol where each source publication was held out in turn, the calibration refit on the remaining cohorts, and metrics reported on the held-out cohort only. Results per cohort are available in the v4 Statistical Evidence Lock (`phase_3_metrics.leave_one_source_cohort_out`). **LOSCO is not external validation**; it tests the calibration step only, not the four fixed regression coefficients.

### 6.5 Sensitivity analyses

Five sensitivity sweeps (fructose multiplier, pure-fat attenuation, calibration slope, animal-fat multiplier, animal-protein multiplier) were executed with an isolated prediction path that accepts per-call parameter overrides. The production SDK source was **not modified**. Every sweep includes an executable applied-assertion check; the master script aborts if an override fails to propagate. All five sweeps passed. Numerical details are in the v4 Statistical Evidence Lock.

---

## 7. Limitations

1. **No independent external validation.** No cohort collected outside the training publications is included. Every row of the n = 25 "out-of-sample" subset is drawn from a publication that is either a direct extension of the training cohort (Bao 2011 ← Bao 2009) or a publication-level overlap with the training manifest. Independent external validation requires a prospectively collected cohort outside this literature and is explicitly a v2.0.x roadmap item.
2. **Calibration leakage.** The post-hoc linear calibration was fit on all 63 validation rows. Both the n = 25 and the n = 9 subsets overlap this calibration-fit set (39.68 % and 14.29 % respectively). LOO-refit of the calibration raises MAE on n = 25 from 10.20 to 11.72.
3. **Training-cohort size.** The frozen CSV contains 151 rows with zero exact duplicates; the MANIFEST's "effective n = 147" claim is unreconstructible. 2-decimal-place coefficient reproducibility is **necessary but not sufficient** evidence of complete methodological equivalence with any historical 147-row procedure.
4. **Small n = 9 subset.** The algorithmically filtered non-overlap subset has Pearson r = 0.447 with a 95 % MAE CI spanning [5.74, 20.28] — wide, reflecting the small sample. Experimental independence at the primary-source level has not been established.
5. **Reference-standard binding.** NIS is bound to the white-bread Holt-FII scale and is **not** interchangeable with glucose-referenced insulinaemic-index measurements or CGM-derived response measures.
6. **Pure-fat and pure-protein meals.** The pure-fat guard (0.15×) is a conservative regularisation, not an empirical finding from large pure-fat cohorts. Model behaviour on such compositions should be interpreted cautiously.
7. **Class imbalance on the training cohort.** Food types are not uniformly distributed; the cohort is literature-driven and reflects historical insulin-AUC publication choices.

---

## 8. Reproducibility

All code and data are open under Apache 2.0 (software) and CC BY 4.0 (documentation). The analysis is bit-reproducible from the installed public package:

```bash
python -m venv .venv && . .venv/bin/activate
pip install --no-cache-dir nutramilo-nis==1.1.9 numpy pandas scikit-learn pytest

# Phase 6 portable verifier (from nutramilo_nis_public_release_verification.zip)
python verify_nis.py                  # exits 0 on PyPI 1.1.9
python -m pytest test_consistency.py  # 5/5 pass
```

Determinism: `SEED = 20260227, N_BOOTSTRAP = 2000`. LOO, LOSCO, and OLS are closed-form and seed-independent.

Artefact hashes:

| Artefact | SHA-256 |
|---|---|
| PyPI wheel `nutramilo_nis-1.1.9-py3-none-any.whl` | `7d4c29cc533c3fd43447666500b76fee851f536bf91577ea54777e2125c533d6` |
| PyPI sdist `nutramilo_nis-1.1.9.tar.gz` | `75da8335938d7876430c873c8be0973197ff06a3bce199ceef31beb77878ca7d` |
| GitHub tag `nis-v1.1.9` commit | `ddb3ada8d0fca7a8125009a698518339cbbbeb93` |
| Training CSV | `b41eb157661b2d8ad0f1e2bd0447f7cb61dfc460bb27bff754a59f3f50a2aaec` |
| Validation CSV | `6e2868c8a37e0b60c9a69249682528b540c3da4f6ecabb7e2a5a67d73443f5cf` |

---

## 9. Future independent validation requirements

A credible claim of "externally validated" NIS requires:

1. **A cohort collected prospectively**, with new participants and new in-vivo insulin AUC measurements, **outside** the six training publications.
2. **Pre-registration** of the evaluation protocol (subsets, metrics, significance tests, stopping rules).
3. **Blinding**: the external cohort must be analysed with the NIS model as deployed, without any further coefficient or calibration fitting. If re-calibration is required, it must be reported as a separate, pre-registered step.
4. **Statistical pre-specification** of success criteria (e.g. target MAE within specified CI, or non-inferiority against a stated baseline).
5. **Public release** of the external-cohort data (or a release schedule that preserves scientific independence).
6. **A new major release** (`v2.0.x`) accompanying the external-validation publication. The frozen v1.1.x coefficients will not be modified.

Only after these steps will the "externally validated" status change from NOT ACHIEVED to CONFIRMED.

---

## 10. Conflict-of-interest and funding statement

The authors declare financial interest in Nutramilo-branded consumer products derived from this methodology. The current work was supported internally by International Sci Ink Press Ltd EOOD. No external funder influenced the evaluation protocol or the content of this technical report.

---

## 11. Data and code availability

| Item | Location |
|---|---|
| Source code | <https://github.com/axilla-score/nutramilo-nis> |
| PyPI distribution | <https://pypi.org/project/nutramilo-nis/> |
| Zenodo DOI | <https://doi.org/10.5281/zenodo.20571802> |
| v4 Statistical Evidence Lock bundle | `nutramilo_nis_statistical_evidence_lock.zip` (companion deposit recommended) |
| v5 Public Release Verification bundle | `nutramilo_nis_public_release_verification.zip` (companion deposit recommended) |

---

## 12. Citation

Please cite the Zenodo DOI and this technical report:

> Inkov, I. et al. (2026). Nutramilo Insulin Score (NIS) v1.1.9 — open, macronutrient-derived algorithm for estimating the relative insulinogenic potential of meals. Zenodo. <https://doi.org/10.5281/zenodo.20571802>.

Full citation metadata: `CITATION.cff` in the GitHub repository.

---

## 13. References (bibliography)

1. Holt S. H. A., Brand-Miller J. C., Petocz P. (1997). *An insulin index of foods: the insulin demand generated by 1000-kJ portions of common foods.* American Journal of Clinical Nutrition 66(5):1264–1276.
2. Bell K. J., Smart C. E., Steil G. M., Brand-Miller J. C., King B., Wolpert H. A. (2014). *PhD thesis on dietary protein and fat insulin demand in type 1 diabetes* (University of Sydney).
3. Bao J., de Jong V., Atkinson F., Petocz P., Brand-Miller J. C. (2009). *Food insulin index: physiologic basis for predicting insulin demand evoked by composite meals.* American Journal of Clinical Nutrition 90(4):986–992.
4. Bao J. (2011). *The Food Insulin Index: Physiological Basis and Clinical Applications* (PhD thesis, University of Sydney).
5. Nilsson M., Stenberg M., Frid A. H., Holst J. J., Björck I. M. E. (2004). *Glycemia and insulinemia in healthy subjects after lactose-equivalent meals of milk and other food proteins: the role of plasma amino acids and incretins.* American Journal of Clinical Nutrition 80(5):1246–1253.
6. Boirie Y., Dangin M., Gachon P., Vasson M. P., Maubois J. L., Beaufrère B. (1997). *Slow and fast dietary proteins differently modulate postprandial protein accretion.* PNAS 94(26):14930–14935.
7. Trichopoulou A., Costacou T., Bamia C., Trichopoulos D. (2003). *Adherence to a Mediterranean diet and survival in a Greek population.* New England Journal of Medicine 348(26):2599–2608.
8. Sahyoun N. R., Anderson A. L., Tylavsky F. A., Lee J. S., Sellmeyer D. E., Harris T. B. (2008). *Dietary glycemic index and glycemic load and the risk of type 2 diabetes in older adults.* American Journal of Clinical Nutrition 87(1):126–131.
9. Le K. A., Tappy L. (2008). *Metabolic effects of fructose.* Current Opinion in Clinical Nutrition and Metabolic Care 11(4):479–484. (PMID 18550600).
10. Stanhope K. L. et al. (2009). *Consuming fructose-sweetened, not glucose-sweetened, beverages increases visceral adiposity and lipids and decreases insulin sensitivity in overweight/obese humans.* Journal of Clinical Investigation 119(5):1322–1334.

---

**End of technical report.** This document contains **no new statistical results**; every number is a verified read from the v4 Statistical Evidence Lock (`nis_evidence_lock.json`). It is suitable as the foundation for a subsequent peer-reviewed methodological publication, with the Limitations and Future-Validation sections preserved verbatim.
