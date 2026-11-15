# RELEASE DECISION — Nutramilo NIS v1.1.9 final documentation

**Status.** DRAFT recommendation. Pending explicit maintainer approval. No publish, push, or Zenodo edit was performed by this audit.

---

## 1. Overall verdict

| Item | Classification |
|---|---|
| Software integrity (PyPI ↔ GitHub ↔ installed package) | **PASS** (bit-identical) |
| Numerical reproducibility of statistical results | **PASS** (4-dp match to v4 Evidence Lock) |
| Dataset provenance (n = 147 vs n = 151) | **UNRESOLVED** — documentation-level fix proposed |
| Public scientific claims | **PASS WITH QUALIFICATIONS** after this correction set is applied |
| Documentation can be corrected without changing the model | **PASS** |
| Manuscript readiness (methodology paper) | **PASS WITH QUALIFICATIONS** — `SCIENTIFIC_METHODS_AND_RESULTS.md` supplies the foundation |
| Independent external validation | **FAIL (missing)** — v2.0.x roadmap item |

**No change to the mathematical model, coefficients, calibration parameters, dataset files, or deployed application is required.**

---

## 2. Recommended release path (per surface)

### 2.1 GitHub — recommended: **APPLY NOW**

Open a documentation-only PR against `main` that:

1. Replaces `README.md` with `README_GITHUB_FINAL.md` (verbatim).
2. Fixes the `[project.urls] Issues` double-slash typo in `pyproject.toml`.
3. Annotates `HoltBellBao_v1_frozen_2026.MANIFEST` with the UNRESOLVED flag for the "effective n = 147" line.
4. Adds `docs/SCIENTIFIC_METHODS_AND_RESULTS.md` (foundation for the planned methodological manuscript).

No code change in the PR. CI remains green because `nis.py`, `classify.py`, `__init__.py` are untouched.

### 2.2 Zenodo — recommended: **APPLY NOW (Option A)**

Open Zenodo record `10.5281/zenodo.20571802` → Edit → paste the content of `ZENODO_DESCRIPTION_FINAL.md`, with `ZENODO_CORRECTION_NOTE.md` §1–§6 prepended as an "Editorial note" block. Save. The DOI is preserved; no new version is required for a description-only correction.

*Optional later step.* Once the GitHub PR is merged, upload `nutramilo_nis_statistical_evidence_lock.zip` and `nutramilo_nis_public_release_verification.zip` as a new **version** of the same Zenodo record (Option B), which produces a new DOI pointing at the same concept.

### 2.3 PyPI — recommended: **DEFER** (choose one of the two options below)

PyPI versions are immutable, so the existing `1.1.9` long-description cannot be edited in place. Two acceptable paths:

#### Option A — leave PyPI at `1.1.9` unchanged

Pros:
* No new release. No version-bump noise.
* PyPI project page already links to the GitHub Homepage; users reach the corrected README through that link.
* No compatibility risk (there is none anyway — no code change).

Cons:
* The PyPI long-description continues to carry the uncorrected text until a future release.

#### Option B — publish `v1.1.10` as a documentation-only release

Pros:
* PyPI long-description shows the corrected text immediately.
* `pyproject.toml` Issues URL typo is fixed in a tagged release.

Cons:
* Requires a version bump across `__init__.py`, `pyproject.toml`, `CITATION.cff`, and the test suite's pinned `NIS_VERSION` assertion.
* Does not change behaviour; the bundled test suite must be updated to assert `NIS_VERSION == "1.1.10"`.
* Creates a release-note request to explain that `v1.1.9 == v1.1.10` byte-for-byte on the compute path.

**Recommendation.** Option A unless the maintainer plans substantive feature work in the near future. The Zenodo DOI already serves as the canonical citation anchor, and the GitHub README is the user-facing documentation surface.

---

## 3. What this release decision does NOT authorise

* Any modification to the NIS algorithm, coefficients, or calibration.
* Any retraining, re-regression, or coefficient refit.
* Any modification to the deployed Nutramilo application.
* Any claim of clinical validation.
* Any claim of independent external validation.
* Any push to GitHub `main` or any PyPI publish without explicit maintainer approval.
* Any edit to the Zenodo record without explicit maintainer approval.

---

## 4. Manuscript readiness (for the eventual peer-reviewed article)

`SCIENTIFIC_METHODS_AND_RESULTS.md` is manuscript-ready in substance. It:

* Includes abstract, rationale, model development, mathematical framework, data sources, calibration, evaluation, limitations, future-validation requirements, reproducibility, references.
* Quotes every performance number verbatim from the v4 Statistical Evidence Lock.
* Preserves "NOT ACHIEVED" status on independent external validation and "UNRESOLVED" status on n = 147.

To convert the pre-manuscript to a submittable article:

1. Convert to journal template (typically LaTeX + BibTeX).
2. Add any additional figures (e.g. training-cohort residual diagnostics, per-cohort scatter plots) — their data is already in the v4 Evidence Lock JSON.
3. Fill the journal-side author / affiliation / ORCID / funding boilerplate.
4. Keep §7 Limitations and §9 Future Independent Validation Requirements verbatim.

---

## 5. Final remark

The scientific content of NIS v1.1.9 is **sound as an exploratory methodology** and **defensible with the three-regime evaluation framing**. The required work is documentation alignment and transparent limitations, not model revision. This bundle completes that work.
