# F-04 — Provisional vintage → partition role note

**Status:** PROVISIONAL. Roles are fixed at F-04 splits, after ratification.
**Authored:** 18 August 2026
**Owner:** Fahmi Alshahabi
**Purpose:** record which acquisition vintages are already development-exposed, before the
question becomes unanswerable.

---

## 1. Why this note exists now

A vintage that has been used for development, debugging or outcome inspection cannot later serve
as an unexposed holdout. This is irreversible and it is not recoverable by documentation after the
fact. Harvest vintages are currently being produced by the acquisition stream ahead of any agreed
partition scheme, so the exposure status of each vintage must be recorded as it happens rather
than reconstructed later.

This note does not fix partition roles. It records exposure so that F-04 can fix roles from
accurate information.

---

## 2. Vintage status as of 18 August 2026

| Vintage | Status | Exposure | Provisional role |
|---|---|---|---|
| **H1** | Built 2026-07-20, `git_sha 78ffa09`, committed 15 Aug | Development-exposed | DEV only |
| **H2** | Run, large files not yet uploaded | Presumed development-exposed | DEV only, unless non-inspection can be established |
| **H3** | Not yet harvested | None | **Reserved — candidate temporal-robustness holdout** |

**H1** is exposed by construction: it has been inspected during pipeline development and its
manifest metrics have been read in the course of this stream's own planning.

**H2** should be treated as exposed by default. If the acquisition owner can establish that no
outcome-level inspection occurred, the classification can be revisited before F-04 — but the
burden is on establishing non-exposure, not on assuming it.

**H3** is requested to be harvested and left untouched: no development use, no debugging against
it, no outcome inspection. Requested from Wesley on 18 August 2026.

---

## 3. Rules this note asserts

1. Exposure is one-way. A vintage cannot be un-exposed.
2. Default classification is exposed. A vintage is DEV unless its non-exposure is positively
   established and recorded.
3. Exposure status is recorded at the time of use, not reconstructed at analysis time.
4. Holdout status requires a named vintage identifier and a content hash, so the claim of
   non-exposure is auditable rather than asserted.
5. This note is provisional and carries no ratification authority. F-04 fixes roles.

---

## 4. Frame problem to carry into F-04

From the H1 manifest, the acquired corpus does not straightforwardly define the target population:

| Quantity | H1 value |
|---|---|
| S0 records | 2,329,014 |
| Tombstones | 743,537 |
| Feeds attempted / converged / failed | 413 / 334 / 82 |
| Located records | 356,846 |
| **Known inside London** | **95,511** |
| Known outside London | 260,661 |
| Scope-indeterminate | 674 |
| **No coordinates at S0** | **1,972,168** |

Two consequences for F-04 and for the estimand registry:

- Roughly 85% of S0 records carry no coordinates, so any London-scoped frame built on located
  records alone is a small and possibly non-representative subset of the corpus. The declared
  universe must state this explicitly, and no coverage quantity should be reported as if the
  frame were the corpus.
- 82 of 413 feeds failed. Feed-level failure is a typed system failure and belongs in the
  intention-to-evaluate denominator, not silently outside it.

Neither point is settled here. Both must be resolved before splits are frozen.

---

## 5. Dependencies

- `lineage_metrics` and `schedule_metrics` in the H1 manifest are recorded as pending S1 and S1b.
  Until the evidence engine produces those stages, vintage roles cannot be finalised for any
  estimand that depends on state transitions.
- Ratification of the pivot and of the F-02 RATIFY values remains outstanding.

---

## 6. Action taken

- 18 Aug 2026 — requested that H3 be harvested and left untouched pending F-04.
- 18 Aug 2026 — requested confirmation of H2's location and inspection status.
