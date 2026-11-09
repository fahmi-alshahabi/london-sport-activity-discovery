# F-04 — split assignment and frozen hashes

**Owner:** Fahmi Alshahabi
**Assigned:** 2026-09-08

## 1. Method

Splits assigned by grouped random assignment on `task_template_id` (PD-6),
seeded. Every task sharing a `task_template_id` lands in the same split.

- **Seed:** `42` — fixed at assignment; never changed.
- **Procedure:** the 14 `task_template_id` values sorted ascending, shuffled by
  Python `random.Random(42).shuffle`, first 4 assigned DEV, remainder LOCKED.
- **Reproducible:** re-running the same procedure with seed 42 reproduces the
  assignment exactly.

## 2. Scheme

**Scheme A — DEV + LOCKED only.**

| Split | Templates | Count |
|---|---|---|
| DEV | TT-0007, TT-0008, TT-0009, TT-0013 | 4 |
| LOCKED | TT-0001–0006, TT-0010, TT-0011, TT-0012, TT-0014 | 10 |
| CAL_MODEL | — | 0 |
| CAL_RISK | — | 0 |

`CAL_MODEL` and `CAL_RISK` are recorded **empty by decision**, not by oversight:
F-08 calibration is descoped, so no split consumes calibration items. The enum
values remain in the schema; no task is assigned to them.

DEV items are permanently excluded from locked evaluation (F-07 §5).

## 3. Deviation from F-07 §5 — recorded

F-07 §5 requires split assignment "before any task text is written to disk in
final form; the assignment is part of the freeze commit."

Assignment here **followed** authoring: the 14 tasks were committed with a
placeholder `split` value, then assigned. No freeze gate had been passed at any
point, and no task text was final. The assignment is nonetheless seeded and
reproducible, and the leakage property PD-6 protects is satisfied and verified.

Recorded as a deviation rather than corrected silently.

## 4. Verification

`src/evaluation/lint_tasks.py` run against `tasks/` on 2026-09-08:

```
Tasks: 14   Templates: 14
  by split:  {'LOCKED': 10, 'DEV': 4}
  by suite:  {'diagnostic': 14}
  by family: {'activity_geography': 3, 'time_schedule': 3, 'price_visibility': 2,
              'age_information': 2, 'accessibility_information': 2, 'compound_referral': 2}

PASS - all structural and cross-task checks clean.
```

No `task_template_id` appears in more than one split.

## 5. Frozen hashes

SHA-256 per task file, recorded in `MANIFEST-sha256.txt`.

**Manifest root (SHA-256 of the manifest file):**
`e7e02960a9bda5400238fff64c7d10e8f12411dc0ccfc8deb68ecf550fc2030b`

Any edit to any task file changes its hash and the manifest root. These are the
values to compare against at the freeze gate and at reproduction.

## 6. Not covered

The DEV vintage is not fixed (F-03 rules §3), so **defects are authored but not
yet planted in the corpus**. These hashes freeze the task text and metadata
only, not the corpus state the tasks will run against.

The arm count is not final until 4.2 ratifies the designation pair.

## SIGN-OFF — F-04 split assignment

- **Claim ID:** F-04-splits
- **Artefacts checked:** `tasks/` (14 files), `MANIFEST-sha256.txt`,
  `src/evaluation/lint_tasks.py`, `src/evaluation/task.schema.json`
  — branch `fahmi/proposal-v2-sections-6-7`, commit `e8caee3`
  - **Method:** Chose scheme A and seed 42; reviewed the linter output showing 14 templates across 4 DEV and 10 LOCKED with no template in two splits; checked the hash manifest against the task files.
- **Outcome:** APPROVED
- **Conditions:** [if any]
- **Not covered by this sign-off:** defect planting, DEV vintage, arm count
- **Reference:** F-07 PD-6, CA-01.A3
- **Signed:** Fahmi Alshahabi · 2026-09-08
