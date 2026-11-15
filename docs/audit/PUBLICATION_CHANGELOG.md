# PUBLICATION CHANGELOG — Nutramilo NIS v1.1.9 final documentation

> **Status.** DRAFT — pending explicit maintainer approval. No publish, push, or Zenodo edit was performed by this audit.

## Which file goes where

| File in this bundle | Use for | Destination action |
|---|---|---|
| `README_GITHUB_FINAL.md` | Full GitHub `README.md` (public landing page) | Replace `README.md` on branch `main` (or a `docs/correction` PR) |
| `README_PYPI_FINAL.md` | PyPI long description | Use as the `README.md` bundled with a documentation-only `v1.1.10` release, *or* leave PyPI at `1.1.9` and rely on the GitHub Homepage link (maintainer choice — see `RELEASE_DECISION.md`) |
| `ZENODO_DESCRIPTION_FINAL.md` | New Zenodo "description" field | Paste into the existing record's Edit UI — DOI preserved |
| `ZENODO_CORRECTION_NOTE.md` | Editorial addendum | Prepend to the Zenodo description (same record; §1–§6 of the file) |
| `SCIENTIFIC_METHODS_AND_RESULTS.md` | Pre-manuscript technical report | Keep in `docs/` folder on GitHub; cite as the foundation of the upcoming peer-reviewed article |
| `DOCUMENTATION_CONSISTENCY_MATRIX.md` | Internal reviewer tool | Not public-facing; keep in `docs/audit/` |
| `PUBLICATION_CHANGELOG.md` | This file — maintainer checklist | Keep in `docs/audit/` |
| `RELEASE_DECISION.md` | Decision record | Keep in `docs/audit/` |

---

## Changes applied in this corrected documentation set

### GitHub README

| Section | Nature of change |
|---|---|
| Badges | Replaced the "will be added after publication" placeholder with the live Zenodo DOI badge |
| New "Scientific status" standalone section | Highlights exploratory methodology; absence of prospective clinical validation |
| New "Intended use" section | Spells out that NIS is comparative and research-only |
| New "Reference standard" section | Explicitly states white-bread-referenced Holt-FII binding; non-interchangeable with glucose-referenced indices |
| Algorithm step 2 | Replaced "n = 147 foods" with the 151-row explanation and the UNRESOLVED flag for the historical "effective n = 147" claim |
| Algorithm step 4 | Added explicit note that calibration was fit on **all 63** validation rows |
| "Note on validation framing" | Replaced with full four-row Evaluation table + Wilcoxon statistic |
| New "Scientific limitations" section | Lists six limitations in priority order |
| Reproducibility | Added SHA-256 of wheel / sdist / CSVs; added pytest + verifier commands |
| Disclaimer | Rewritten: EU MDR 2017/745 and 21 CFR 820 explicit; prospective clinical validation explicitly disavowed |

### PyPI long description

Same substantive content as GitHub README, condensed:

* Evaluation table reduced to four rows.
* API/worked-examples/API-reference references delegated to the GitHub link.
* Added footer "Deployment note" for the maintainer (release options A / B).

### Zenodo record `10.5281/zenodo.20571802`

* `ZENODO_DESCRIPTION_FINAL.md` is the proposed **replacement description**. Can be pasted into the Edit UI without changing the DOI (Zenodo Option A — description-only edit).
* `ZENODO_CORRECTION_NOTE.md` is the proposed **editorial addendum** covering the six documentation items (§1–§6). Can be prepended to the description for high visibility.
* Zenodo mechanics (Options A / B / C) are enumerated inside `ZENODO_CORRECTION_NOTE.md`.

---

## Items NOT changed

* `NIS_COEFFICIENTS` (1.61 / 0.66 / 1.20 / −1.14)
* `_FAT_TYPE_MULT`, `_PROTEIN_TYPE_MULT`
* `PURE_FAT_DENSITY_THRESHOLD`, `PURE_FAT_ATTENUATION`
* `FRUCTOSE_MULT`, `FRUCTOSE_OF_SUGAR`
* `NIS_CALIBRATION` (slope 0.7275, intercept 8.111)
* Any function body in `nis.py`, `classify.py`, `__init__.py`
* `HoltBellBao_v1_frozen_2026.csv` contents and SHA-256
* `foods_v1_0_1_validation.csv` contents and SHA-256
* The deposited PyPI wheel, PyPI sdist, and Zenodo files

**No code change is required to apply any correction in this bundle.**

---

## Maintainer checklist (sequence)

- [ ] 1. Read `RELEASE_DECISION.md` and confirm the overall release strategy.
- [ ] 2. Open a PR against `main` replacing `README.md` with `README_GITHUB_FINAL.md`.
- [ ] 3. In the same PR, fix the `pyproject.toml` `[project.urls] Issues` double-slash typo.
- [ ] 4. In the same PR, annotate `HoltBellBao_v1_frozen_2026.MANIFEST` with the UNRESOLVED flag for the "effective n = 147" line (or remove that line).
- [ ] 5. Review + merge the PR.
- [ ] 6. Open the Zenodo record and apply `ZENODO_CORRECTION_NOTE.md` + `ZENODO_DESCRIPTION_FINAL.md` via the Edit UI (Option A — same DOI).
- [ ] 7. Decide PyPI path: publish documentation-only `v1.1.10` *or* leave PyPI at `1.1.9`.
- [ ] 8. (Optional) Later: upload `nutramilo_nis_statistical_evidence_lock.zip` and `nutramilo_nis_public_release_verification.zip` as a new Zenodo version (Option B — new DOI).
- [ ] 9. (Future) Begin v2.0.x planning: prospective external cohort collection; pre-registered evaluation protocol.
