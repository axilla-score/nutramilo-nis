# Zenodo record `10.5281/zenodo.20571802` — final description (draft for maintainer)

> Draft for maintainer review. Zenodo deposits are immutable; this document proposes a **description-level correction** — no re-upload of the software files is required. The DOI is preserved.

---

## Title

**Nutramilo Insulin Score (NIS) v1.1.9 — open, macronutrient-derived algorithm for estimating the relative insulinogenic potential of meals**

## Authors

Inkov, I. (International Sci Ink Press Ltd EOOD) — plus co-authors per `CITATION.cff`.

## Description

The **Nutramilo Insulin Score (NIS) v1.1.9** is an open, reproducible computational surrogate for the white-bread-referenced Food Insulin Index (FII) of Holt et al. (1997) and derivative literature. From a meal's macronutrient composition alone, NIS estimates how the meal would rank on that historical FII scale. **NIS is an exploratory methodology; it is not a medical device, has not been clinically validated, and does not predict any individual's postprandial insulin or glycaemic response.**

### Reference standard

NIS is bound to the **white-bread-referenced Holt FII scale**, extended by Bell (2014 PhD thesis), Bao (2009, 2011), Nilsson (2004), Boirie (1997), Trichopoulou (2003), and Sahyoun (2008). Pure glucose has a Holt-FII of approximately 100; white bread is the reference anchor at 100. **NIS values are not equivalent to glucose-referenced insulinaemic indices** and must not be used interchangeably with them.

### Algorithm (five-step pipeline)

1. Per-1000 kJ normalisation (Atwater factors).
2. OLS linear regression (no intercept) with coefficients `(net_carbs = +1.61, protein = +0.66, fat = +1.20, fiber = −1.14)` per 1000 kJ and source-type modifiers (plant / mixed / animal).
3. Pure-fat extrapolation guard (0.15× when `(net-carb + protein) / 1000 kJ < 5 g`).
4. Cross-cohort linear calibration `obs ≈ 0.7275 × raw + 8.111`, fit on **all 63** cross-cohort validation rows.
5. Optional Holt cross-track + clinical-tier floor; `Final NIS = max(…)` clamped `[0, 100]`.

### Training data

File: `HoltBellBao_v1_frozen_2026.csv` — **n = 151 rows**, SHA-256 `b41eb157661b2d8ad0f1e2bd0447f7cb61dfc460bb27bff754a59f3f50a2aaec`. OLS on all 151 rows reproduces the deployed coefficients to two decimal places. A legacy manifest note referring to an *"effective n = 147 after duplicate removal"* **cannot be reconstructed** from the frozen artefacts and is flagged `HISTORICAL_METHOD_UNRESOLVED` in the v4 Statistical Evidence Lock.

### Calibration data

The 63-row cross-cohort validation set (`foods_v1_0_1_validation.csv`, SHA-256 `6e2868c8…43f5cf`) draws from Holt (1997), Bao (2011), Nilsson (2004), Boirie (1997), Trichopoulou (2003), and Sahyoun (2008). The single-slope / single-intercept calibration `obs ≈ 0.7275 × raw + 8.111` was fit on **all 63** of these rows. Consequently, any subset of these rows used for evaluation **overlaps** the data used to derive the calibration; this must be stated when citing performance numbers.

### Evaluation methodology

Four complementary regimes are reported:

| Regime | Protocol | n | MAE | RMSE | Pearson r |
|---|---|---:|---:|---:|---:|
| Full pooled literature cohort | fixed production calibration | 63 | 14.27 | 19.19 | 0.773 |
| Non-Holt subset | fixed production calibration | 25 | 10.20 | 13.46 | 0.826 |
| Non-Holt subset | leave-one-out refit of calibration | 25 | 11.72 | 14.50 | 0.799 |
| Algorithmically filtered non-overlap subset | fixed production calibration | 9 | 12.81 | 17.10 | 0.447 |

Paired Wilcoxon signed-rank (baseline vs full NIS on n = 25): **W = 55.5, z = −2.89, p = 0.003822**.

The "algorithmically filtered non-overlap subset" is defined by normalised-name, alias, macro-tuple, and publication-manifest non-overlap criteria; **experimental independence at the primary-source level is not established**.

### Status

| Item | Status |
|---|---|
| 2-decimal-place reproducibility of training coefficients | CONFIRMED (n = 151) |
| Full-precision reproducibility of training coefficients | NOT ACHIEVED (2-dp match only) |
| n = 147 historical row-exclusion rule | UNRESOLVED |
| Apparent-performance on the pooled 63-row cohort | DEFENSIBLE |
| Name-level out-of-sample performance (n = 25) | DEFENSIBLE as framed above |
| Independent external validation | **NOT ACHIEVED** |

### Scientific limitations

1. No cohort collected outside the training publications is included; independent external validation has not been achieved.
2. The post-hoc linear calibration was fit on all 63 validation rows; the "OOS" slice therefore overlaps the calibration-fit set.
3. The "effective n = 147" line in the training manifest is unreconstructible from the shipped artefacts.
4. Pearson r = 0.447 on the n = 9 non-overlap subset has wide bootstrap CI reflecting the small sample.
5. NIS is bound to the Holt-FII reference standard and is not interchangeable with glucose-referenced indices.

### Deliverables in this record

* `nutramilo_nis-1.1.9-py3-none-any.whl` — SHA-256 `7d4c29cc533c3fd43447666500b76fee851f536bf91577ea54777e2125c533d6`
* `nutramilo_nis-1.1.9.tar.gz` — SHA-256 `75da8335938d7876430c873c8be0973197ff06a3bce199ceef31beb77878ca7d`

**Recommended companion upload (in a new Zenodo version, see Correction Note):** `nutramilo_nis_statistical_evidence_lock.zip` and `nutramilo_nis_public_release_verification.zip`.

### Keywords

insulin, postprandial, food insulin index, Holt FII, macronutrient, nutrition, open-source algorithm, reproducibility, exploratory methodology

### License

Software: Apache 2.0. Documentation: CC BY 4.0.

### Related identifiers

* Software repository: <https://github.com/axilla-score/nutramilo-nis>
* PyPI distribution: <https://pypi.org/project/nutramilo-nis/>
* Companion statistical evidence bundle: forthcoming Zenodo DOI (TBD, maintainer decision)

### Disclaimer

NIS is **not** a medical device under EU MDR 2017/745 or US 21 CFR 820. It is **not** intended for diagnosis, treatment, or dosing decisions and does not replace professional clinical judgement.
