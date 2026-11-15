# NIS v1.1.10 — Documentation Correction Release

**Date.** (set at publication)
**Nature.** Documentation-only. **No code change. No coefficient change. No behavioural change.** The compute path is byte-identical to `v1.1.9`.

---

## TL;DR

This release corrects documentation inconsistencies that were identified by an independent reproducibility audit (v4 + v5 + v6). No user of `v1.1.9` needs to upgrade for correctness; the numeric predictions of `compute_nis` are unchanged. The release exists so that the PyPI long-description, GitHub README, and bundled citation metadata accurately describe the model's scientific status, training cohort, calibration method, and limitations.

If you depend on `nutramilo-nis==1.1.9`, you may pin to it indefinitely. Nothing breaks in `v1.1.10`.

---

## Byte-level equivalence to v1.1.9

| File | SHA-256 at v1.1.9 | SHA-256 at v1.1.10 | Change |
|---|---|---|---|
| `nutramilo_nis/nis.py` | `fa36213c…ef6e744` | `fa36213c…ef6e744` | **IDENTICAL** |
| `nutramilo_nis/classify.py` | `79af0aa9…aede8d74` | `79af0aa9…aede8d74` | **IDENTICAL** |
| `nutramilo_nis/__init__.py` | `11c07f67…dca6f591` | updated `NIS_VERSION = "1.1.10"` only | 1-line version string |

All numeric fields (`nis_percent`, `piru`, `tier`, `contributions`) returned by `compute_nis` are byte-identical to `v1.1.9` — verified against the full 63-row validation CSV and the 18-test suite (`tests/test_nis.py`).

---

## What changed in this release

### Documentation
- **`README.md`** — rewritten for accuracy and consistency with the v4 Statistical Evidence Lock. Six substantive corrections:
  1. Training cohort size: n = 147 → **n = 151** (zero exact duplicates); the legacy "effective n = 147" MANIFEST claim is **UNRESOLVED**.
  2. Validation framing: the n = 25 subset is out-of-sample vs the **regression** step but **not** vs the **calibration** step; LOO-refit of calibration raises MAE 10.20 → 11.72.
  3. The n = 9 subset is relabelled **"algorithmically filtered non-overlap"**; experimental independence at the primary-source level is not established.
  4. Reference standard disclosed: white-bread Holt-FII, **not** interchangeable with glucose-referenced indices.
  5. Clinical disclaimer tightened: explicit EU MDR 2017/745 and 21 CFR 820 exclusions; explicit statement that no prospective clinical validation was performed.
  6. Selective reporting corrected: single "n = 25 hold-out" row replaced with the full four-regime evaluation table + Wilcoxon statistic (p = 0.003822).
- **`docs/SCIENTIFIC_METHODS_AND_RESULTS.md`** — new, pre-manuscript technical report (foundation for a subsequent peer-reviewed article).
- **`CITATION.cff`** — abstract rewritten to reflect the corrected cohort size and the three-regime evaluation framing.
- **`CHANGELOG.md`** — added.
- **`pyproject.toml`** — fixed `[project.urls] Issues` double-slash typo; added `Changelog` URL.

### Code
- **`__init__.py`** — bumped `NIS_VERSION = "1.1.10"`. **No other code changes.**

### Tests
- **`tests/test_nis.py`** — updated the `test_version_frozen` assertion to the new version string. All 18 numerical regression tests are unchanged and pass unchanged.

---

## Upgrade guide

```bash
pip install --upgrade nutramilo-nis
```

No API change. No behaviour change. No deprecations.

Code that asserts `nutramilo_nis.NIS_VERSION == "1.1.9"` must be updated to `"1.1.10"` (or relaxed to `nutramilo_nis.NIS_VERSION.startswith("1.1.")`).

---

## Reproducibility

```bash
python -m venv .venv && . .venv/bin/activate
pip install --no-cache-dir nutramilo-nis==1.1.10 numpy pandas scikit-learn pytest

# 18/18 bundled tests
python -m pytest tests -v

# Full v4 reproducibility pack
# (download nutramilo_nis_public_release_verification.zip; unzip; run)
python v5/phase6_portable/verify_nis.py
```

Artefact hashes (computed from a clean build of this release):

| Artefact | SHA-256 |
|---|---|
| `nutramilo_nis-1.1.10-py3-none-any.whl` | (set at PyPI publish) |
| `nutramilo_nis-1.1.10.tar.gz` | (set at PyPI publish) |

---

## Items NOT changed

- Coefficients: `(net_carbs = +1.61, protein = +0.66, fat = +1.20, fiber = −1.14)`
- Calibration: slope `0.7275`, intercept `8.111`, fit on all 63 validation rows
- Source-type multipliers: plant / mixed / animal 0.55 / 1.00 / 1.30 (protein); 0.45 / 1.00 / 1.25 (fat)
- Pure-fat guard: `PURE_FAT_ATTENUATION = 0.15`
- Fructose split: `FRUCTOSE_MULT = 0.30`, `FRUCTOSE_OF_SUGAR = 0.50`
- Tier floors and labels
- Any function body in `nis.py`, `classify.py`
- The validation CSV (`foods_v1_0_1_validation.csv`)

---

## Zenodo

A description-only edit of the existing record `10.5281/zenodo.20571802` is recommended for immediate publication (same DOI). A new Zenodo version bundling the `nutramilo_nis_statistical_evidence_lock.zip` and `nutramilo_nis_public_release_verification.zip` evidence bundles is an optional later step (new DOI, same concept).

See `docs/audit/ZENODO_CORRECTION_NOTE.md` for the exact editorial text.

---

## Known not-fixed

- **Independent external validation** — NOT ACHIEVED. No cohort collected outside the training publications is included in this release. External validation is explicitly a v2.0.x roadmap item.
- **The n = 147 historical row-exclusion rule** — UNRESOLVED. The frozen CSV contains 151 rows with zero exact duplicates; no documented procedure reduces it to 147.
- **Primary-source provenance of the n = 9 non-overlap subset** — not retrievable from the shipped artefacts. The subset is algorithmically defined, not experimentally verified.

---

## Thanks

Thanks to the independent reproducibility audit team (v4 Statistical Evidence Lock, v5 Public Release Verification, v6 Final Documentation Correction) for identifying every item in this release.
