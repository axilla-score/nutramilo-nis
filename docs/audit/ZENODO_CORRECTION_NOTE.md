# ZENODO_CORRECTION_NOTE — editorial addendum (final draft)

> **Proposed note for Zenodo record [`10.5281/zenodo.20571802`](https://doi.org/10.5281/zenodo.20571802).**
> The deposited software files are **unchanged**. This is a documentation-level clarification only. No new DOI is required for a description-only edit.

---

## Zenodo edit mechanics (reference for maintainer)

Zenodo preserves immutable version snapshots. Three legitimate options exist:

| Option | Mechanism | DOI effect | When to use |
|---|---|---|---|
| **A. Description-only edit** | Edit record metadata / description via the Zenodo UI. | **Same DOI preserved.** No new version. | Pure documentation corrections that do not add or replace files. **This correction note qualifies.** |
| **B. New version of the same record** | Upload a new version containing the corrected `README.md` and the companion evidence bundles. | New DOI (same concept-DOI). Previous DOI remains valid. | When new supplementary files (e.g. `nutramilo_nis_statistical_evidence_lock.zip`) are added. |
| **C. New record (new concept)** | Separate deposit. | New concept-DOI. | Not recommended; breaks the citation chain. |

**Recommended:** Option A for this correction note; Option B at a later date if the maintainer chooses to bundle the companion evidence packs into the Zenodo record.

---

## Correction note (text to paste into the Zenodo description)

Readers of this record should be aware of the following documentation clarifications identified by an independent reproducibility audit (`nutramilo_nis_public_release_verification.zip`, v5). **The deposited software, the mathematical model, and the dataset files are unchanged.** Every item below corrects wording, not computation.

### 1. Training-cohort size

The dataset `HoltBellBao_v1_frozen_2026.csv` is archived with **n = 151 rows** (SHA-256 `b41eb157…a2aaec`). Earlier text referred to an *"effective n = 147 after duplicate removal."* An exhaustive audit of the archived CSV finds **zero exact normalised-name duplicates** and **zero exact macro-tuple duplicates**; no deterministic row-exclusion rule can be reconstructed from the shipped artefacts that would take 151 → 147. The published regression coefficients `(1.61, 0.66, 1.20, −1.14)` reproduce **to two decimal places** when OLS is fit on all 151 rows. The historical "effective n = 147" claim is therefore flagged UNRESOLVED and should be read with this caveat.

### 2. Validation framing

The non-Holt subset of the cross-cohort validation set (**n = 25**, publications: Bao 2011, Nilsson 2004, Boirie 1997, Trichopoulou 2003, Sahyoun 2008) is out-of-sample relative to the **regression** step but is **not** independent of the **calibration** step (`slope = 0.7275, intercept = 8.111`), which was fit on **all 63** validation rows.

Readers quoting evaluation performance should always use the three complementary regimes:

| Regime | Protocol | n | MAE | RMSE | Pearson r |
|---|---|---:|---:|---:|---:|
| Full pooled cohort | fixed calibration | 63 | 14.27 | 19.19 | 0.773 |
| Non-Holt subset | fixed calibration | 25 | 10.20 | 13.46 | 0.826 |
| Non-Holt subset | leave-one-out refit of calibration | 25 | 11.72 | 14.50 | 0.799 |

The LOO-refit row quantifies the empirical optimism attributable to calibration leakage (+1.52 MAE).

### 3. The n = 9 non-overlap subset

The subset previously labelled "CONFIRMED_INDEPENDENT" in the companion audit should be read as **"algorithmically filtered non-overlap subset; experimental independence not fully established at the primary-source level"** (MAE 12.81, Pearson r 0.447 on n = 9, with wide bootstrap CIs reflecting the small sample).

### 4. Reference standard

NIS is bound to the white-bread-referenced Holt Food Insulin Index. **NIS values are not interchangeable with glucose-referenced insulinaemic-index measurements** reported in other literature.

### 5. Clinical interpretation

NIS is an exploratory computational surrogate. It has **not** undergone prospective clinical validation on any patient cohort and must not be used for diagnosis, prognosis, dosing, or any clinical decision.

### 6. External validation status

No cohort collected outside the training publications is included in this record; **independent external validation has not been achieved**. "Externally validated" status will require a new major release (v2.0.x) based on a prospectively collected cohort.

---

## Items NOT changed by this correction

* The deposited files `nutramilo_nis-1.1.9-py3-none-any.whl` and `nutramilo_nis-1.1.9.tar.gz` and their SHA-256 hashes.
* The DOI `10.5281/zenodo.20571802`.
* Any prior citation to this DOI.
* The mathematical model, coefficients, calibration parameters, or dataset.

---

## Maintainer action checklist

- [ ] Open the Zenodo record and select **Edit** on the description.
- [ ] Prepend the Correction Note text (§1–§6 above) to the existing description, or paste the full `ZENODO_DESCRIPTION_FINAL.md` content.
- [ ] Save — Zenodo keeps the DOI. No new upload required.
- [ ] (Optional) Later, upload `nutramilo_nis_statistical_evidence_lock.zip` and `nutramilo_nis_public_release_verification.zip` as a **new version** of this record (Option B); publishes a new DOI pointing to the same concept.
