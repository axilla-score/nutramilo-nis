# Changelog

All notable changes to this project are documented here. The project adheres to [Semantic Versioning](https://semver.org/) with the explicit rule that **patch versions never change coefficients, calibration, or algorithm behaviour**.

## Unreleased — Documentation Correction (v6 audit) — 2026-02

**Nature.** Documentation-only. No change to the mathematical model, coefficients, calibration parameters, or any function body. Byte-identical compute path to `v1.1.9`.

### Added
- `docs/SCIENTIFIC_METHODS_AND_RESULTS.md` — pre-manuscript technical report (abstract, rationale, mathematical framework, data sources, calibration, three-regime internal evaluation, limitations, future-validation requirements, references). Foundation for a subsequent peer-reviewed methodology paper.
- `docs/audit/DOCUMENTATION_CONSISTENCY_MATRIX.md` — cross-file consistency check for every quantitative claim.
- `docs/audit/PUBLICATION_CHANGELOG.md` — maintainer checklist for the documentation release.
- `docs/audit/RELEASE_DECISION.md` — formal decision record (PASS / PASS WITH QUALIFICATIONS / UNRESOLVED matrix).
- `docs/audit/ZENODO_CORRECTION_NOTE.md` — editorial note for the Zenodo record `10.5281/zenodo.20571802`.
- `docs/audit/ZENODO_DESCRIPTION_FINAL.md` — proposed updated Zenodo description.
- `docs/audit/README_PYPI_FINAL.md` — PyPI long-description draft.

### Changed
- `README.md` — complete rewrite to align with the v4 Statistical Evidence Lock and the v5 Public Release Verification bundle. Specifically:
  - Replaced "n = 147 foods" (training cohort) with the corrected **n = 151** and the `HISTORICAL_METHOD_UNRESOLVED` flag for the legacy "effective n = 147" MANIFEST claim.
  - Re-framed the n = 25 "out-of-sample" subset: OOS with respect to the regression step, **not** independent of the calibration step (which was fit on all 63 validation rows).
  - Replaced the "Confirmed-Independent" label on the n = 9 subset with **"algorithmically filtered non-overlap subset"**; clarified that experimental independence at the primary-source level has not been established.
  - Added new sections: Scientific status, Intended use, Reference standard (white-bread Holt-FII binding; non-interchangeable with glucose-referenced indices), Scientific limitations.
  - Replaced the single "n = 25 hold-out" row with the full four-regime evaluation table (full n = 63, non-Holt n = 25 fixed cal., non-Holt n = 25 LOO-refit cal., algorithmically filtered non-overlap n = 9) + paired Wilcoxon signed-rank statistic.
  - Added SHA-256 of PyPI wheel, PyPI sdist, training CSV, and validation CSV for reproducibility.
  - Rewrote the Disclaimer: explicit EU MDR 2017/745 and 21 CFR 820 exclusions; explicit statement that no prospective clinical validation was performed.
  - Replaced the "DOI badge will be added after publication" placeholder with the live Zenodo DOI badge.
- `pyproject.toml` — fixed `[project.urls] Issues` double-slash typo (`github.com//axilla-score` → `github.com/axilla-score`); added `[project.urls] Changelog` URL pointing to GitHub Releases.
- `CITATION.cff` — rewrote the abstract to reflect the corrected training-cohort size (n = 151), the UNRESOLVED flag for the legacy n = 147 claim, the three-regime evaluation framing, and the exploratory-surrogate status.

### Items deliberately NOT changed
- `nutramilo_nis/nis.py`
- `nutramilo_nis/classify.py`
- `nutramilo_nis/__init__.py`
- `tests/test_nis.py` (except `NIS_VERSION` string if the maintainer also applies the optional v1.1.10 version-bump patch; see `docs/audit/RELEASE_DECISION.md`)
- `tests/test_v1_0_1_validation.py`
- `LICENSE`, `NOTICE.txt`
- Any coefficient, calibration parameter, source-type multiplier, threshold, or function body
- The bundled numerical regression values

### Verification
All numerical claims in the corrected documents are a verified read from the v4 Statistical Evidence Lock (`nis_evidence_lock.json`). The installed public package `nutramilo-nis==1.1.9` reproduces every number in the corrected README to 4 decimal places (see `nutramilo_nis_public_release_verification.zip`, Phase 3).

---

## [1.1.9] — 2026-06-06

Prior release. Changes summarised in the `Update NIS version from 1.1.8 to 1.1.9` commit (`ddb3ada`).

## [1.1.8] — earlier

See git tags and GitHub releases for older version history.
