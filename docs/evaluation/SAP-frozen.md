# Statistical Analysis Plan — frozen

**Owner:** Fahmi Alshahabi · **Frozen:** 2026-09-08
**Registry:** F-02 `estimand-registry.yaml` v0.2.0-scope-frozen
**Benchmark:** `tasks/` — 14 templates, SHA-256 manifest root
`e7e02960a9bda5400238fff64c7d10e8f12411dc0ccfc8deb68ecf550fc2030b`

Frozen before any outcome data is inspected. Deviations after this date are
recorded as deviations, never as plan.

---

## 1. What this plan covers

A specification freeze, not a results freeze. No locked run has executed at the
time of freezing.

**Reported:** U (task-level usefulness) and the evidence-support judgment.
**Not reported:** Q (ranking utility), calibration, H-E, H-G, F-BLOCK-09
application outcomes, per-family results. Each is descoped in F-02 v0.2.0 and
marked `NOT_IN_FORCE` there.

## 2. Hypothesis

**H-P — estimative under CA-01.A9.** Not confirmatory.

Under the 2026-08-29 restatement, arms are presentation-only conditions over one
shared terminal `DecisionEnvelope`. Decision-level estimands are invariant by
construction, so H-P is an evidence-communication comparison, not a
recommendation-superiority claim.

**No numeric superiority margin is claimed.** F-06 produced a declared
sensitivity grid (30–762 templates across the plausible discordant-rate range),
not an estimate of required q. At 14 templates the design sits below the grid, so
no confirmatory threshold is asserted and none is tested.

Confirmatory wording is prohibited throughout the report.

## 3. Design

- **Unit of analysis:** task template. q counts `task_template_id`, never task
  rows and never judgments (F-03 rules §2).
- **Weights:** `equal_per_template_v1` — every template weighted equally over the
  declared task universe. No supply floor applies, so no supply-based reweighting
  is justified.
- **Splits:** DEV 4 templates, LOCKED 10. Seeded grouped random assignment on
  `task_template_id`, seed 42. DEV items are permanently excluded from locked
  evaluation.
- **Suite:** diagnostic only. No naturalistic coverage claim is made.

## 4. Judgments collected

| Construct | Scale | Assessors |
|---|---|---|
| Task-level usefulness | Binary USEFUL / NOT USEFUL | Two, independent |
| Predicate-level evidence-support | Per codebook §4 | Two, independent |

Listing-level relevance (Q) is **not collected**.

Arbitration by Michael Chellam Sebastian where assessors disagree, without sight
of condition labels.

## 5. Analysis

- **Agreement:** Krippendorff's alpha, reported with n stated. Linear distance
  weights, frozen before data (CB-D3). At the n available, the interval is wide;
  the interval is reported, never the point estimate alone.
- **Descriptives:** per-arm counts by construct, with the number of templates
  behind every figure.
- **No inferential test of H-P is run.** The hypothesis is estimative; reporting
  a p-value against a design that is below its own sizing grid would misrepresent
  the evidence.
- **Unjudged items** are treated as non-relevant, with pool depth, judged-item
  counts, contributing arms and the fact of incompleteness reported alongside
  every result (F-07 PD-4).

## 6. Declared limitations

1. Diagnostic suite only — no naturalistic task coverage.
2. 14 templates, below the F-06 grid at every cell. H-P estimative.
3. Roughly 2.3 templates per family — no per-family claim is available.
4. `time_schedule` probes land systematically on unknown-by-mechanism: all 6,455
   observed schedules are typed `PartialSchedule`, so nothing expands under OA-1
   and `schedule_derived` atoms may be absent. These are authored as
   unknown-probes deliberately.
5. Defects are authored but **not planted** — the DEV vintage is not fixed.
6. Split assignment followed authoring rather than preceding it (F-07 §5);
   recorded as a deviation in the F-04 record.
7. `L_decision.unacceptable_decision_condition` remains open, pending partner and
   workflow meaning. Any estimand depending on it is not reported.

## 7. Fallback

If S1/S1b outputs do not land by 2026-09-10 23:59, Michael's 27 August fallback
applies automatically: F-09 becomes specification plus synthetic dry run, and
**H-P is recorded unexecuted rather than failed.** This is a pre-agreed outcome,
not a failure state.

## SIGN-OFF — SAP freeze

- **Claim ID:** SAP-freeze
- **Artefacts checked:** `docs/evaluation/estimand-registry.yaml` v0.2.0,
  `tasks/` (14 files), `MANIFEST-sha256.txt`,
  `docs/evaluation/F-04-split-assignment-record.md`,
  `docs/evaluation/F-06-sizing-result.md`
  — branch `fahmi/proposal-v2-sections-6-7`, commit `e8caee3`
  - **Method:** Read the plan against F-02 v0.2.0-scope-frozen and confirmed no estimand marked NOT_IN_FORCE appears in the reported set; checked each limitation in §6 against its source record.
- **Outcome:** APPROVED
- **Conditions:** none
- **Not covered by this sign-off:** defect planting, DEV vintage, arm count,
  the open unacceptable-decision condition
- **Reference:** CA-01.A9, F-07 PD-1 to PD-6
- **Signed:** Fahmi Alshahabi · 2026-09-08


---

**Appended correction — 2026-09-13.** The sign-off block as committed on
2026-09-08 carried two template artefacts: an unclosed bracket on the Outcome
line, and an unfilled placeholder on the Conditions line. Both are
corrected above. The sign-off decision itself is unchanged; only the
transcription defects are repaired. Recorded here rather than silently, per the
append-only rule.
