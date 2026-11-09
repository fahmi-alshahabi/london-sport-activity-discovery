# Scope declaration — evaluation stream

**Owner:** Fahmi Alshahabi · **Declared:** 2026-09-08
**Covers:** every reduction of scope in the evaluation stream, with its reason.

This note exists so that what was not done is visible and reasoned, rather than
absent. Each entry below states what was dropped, why, and what claim is
consequently unavailable. Nothing here is a finding; nothing here was decided
after seeing outcome data.

---

## 1. Hypothesis

| Item | Status | Reason |
|---|---|---|
| **H-P** | **Estimative, not confirmatory** (CA-01.A9) | F-06 ran 2026-09-03 and produced a sensitivity grid requiring 30–762 templates across the plausible discordant-rate range. The assessor-hours envelope permits ~21–28. The design sits below the grid at every cell, so the honest move is demotion rather than a quietly under-powered confirmatory test. |
| **H-P as recommendation superiority** | Withdrawn | Michael confirmed 2026-08-29 that no recommender exists in any branch. Arms are presentation-only conditions over one shared terminal `DecisionEnvelope`, so decision-level estimands are invariant by construction and cannot carry a between-arm contrast. H-P was restated as an evidence-communication comparison. |
| **H-E, H-G** | Not run | Readiness-gated; the gates are not met and no data supports them. |

**Claim unavailable:** no confirmatory superiority claim, and no claim that any
arm produces better decisions than another.

## 2. Benchmark

| Item | Status | Reason |
|---|---|---|
| **Naturalistic suite** | Dropped | Time. The diagnostic suite is authored instead, because planted-defect probes are what the evaluation stream exists to test. |
| **Template count** | 14 | Above the design floor of ~13 (six families, seven defect mechanisms, one pass costing 7 templates) and below the ~21–28 assessor-hours ceiling. |
| **Per-family reporting** | Dropped | ~2.3 templates per family. Accepted in advance in F-03 rules §2, before authoring. |
| **ROBUST split** | Removed | Contradicted F-07 PD-6: a paraphrase shares its parent's template, and a template sits in exactly one split, so a paraphrase of a LOCKED task could not be in ROBUST. Robustness tasks sit in the parent's split. |
| **LSOA / IMD origin frame** | Replaced with borough | No LSOA or IMD file exists on any branch. `deprivation_tertile` fed only F-12 equity analysis, which is out of scope. |
| **Defect planting** | Not done | The DEV vintage is not fixed. Tasks declare their intended defect and expected state; the corpus has not been modified to contain them. |

**Claim unavailable:** no claim about realistic user-task performance, and no
per-family performance claim.

## 3. Estimands not reported

Each is marked `NOT_IN_FORCE` in F-02 v0.2.0-scope-frozen. `NOT_IN_FORCE` means
the parameter is not required and no claim depending on it may be made. It does
**not** mean a value was chosen.

| Estimand | Reason |
|---|---|
| **Q — ranking utility** | Listing-level relevance is not collected. Metric family, display depth and non-inferiority margin all depended on Clarence's P0/P1/P2 definitions. |
| **R_decision risk ceiling** | F-08 calibration descoped; the ceiling is also explicitly not Fahmi's to set alone (work package §19). |
| **supported_fact_completeness** | H-G descoped. |
| **Integrated regret, wasted questions** | H-E descoped. |
| **F-BLOCK-09 application outcomes** | Application analysis has no ethics route. |

## 4. Deliverables descoped

| Deliverable | Status | Reason |
|---|---|---|
| F-08 calibration spec | Not written | Route was ratified; the spec is unwritten and no calibration claim is made. |
| F-09 estimators | Conditional | If S1/S1b outputs do not land by 2026-09-10 23:59, Michael's 27 August fallback applies: F-09 becomes specification plus synthetic dry run. |
| F-10, F-12, F-14 | Out of scope | Declared previously. |
| F-11 robustness | Out of scope | Time. |
| F-13 application analysis | No-study fallback | No ethics route. |
| F-16 run registry | Conditional | Emitted from a run; if no locked run executes, none is emitted. |
| Phase E locked run | Conditional | Depends on the 10 September outputs. |
| P-BENCH-01 adjudication protocol | Superseded | Superseded by the 2026-09-08 scope freeze. It specifies at least 180 locked queries over six families × 30 population-weighted LSOA origins, and a primary estimand Δ = mean[A(q,S1b) − A(q,S0)] with a 95% interval. None survives: the LSOA/IMD origin frame is removed (§2), so the 180 has no multiplier; Δ requires a data-stage contrast, and the arms are presentation conditions over one shared `DecisionEnvelope`. Branch `docs/benchmark-protocol-p-bench-01`, last commit 2026-07-19. |

**Note on residual references.** The superseded Δ estimand is still quoted as a
live example in C-17 (`docs/applications/evaluation-conditions.md` §6, branch
`clarence/c-block-05`). Flagged here so the two documents are not read as
agreeing on a current estimand.

**Revived, not dropped:** clean-room reproduction. Michael accepted the
non-author reproducer role; the F-02 §10 out-of-scope entry has been deleted, and
its stated reason was false in any case (it claimed the eligibility matrix was
never ratified; it was ratified 2026-08-19).

## 5. Recorded deviations

1. **Split assignment followed authoring.** F-07 §5 requires assignment before
   task text is written to disk in final form. The 14 tasks were committed with a
   placeholder split value, then assigned by seed 42. No freeze gate had been
   passed and no text was final. The assignment is seeded and reproducible and
   PD-6 is satisfied and verified. Recorded in the F-04 record rather than
   corrected silently.
2. **Sign-off ledger misdating.** Entries were first written with the date
   2026-08-23, which was wrong. Corrected by appended entry; the ledger is
   append-only.
3. **Margin fallback trigger passed.** The 2026-08-26 partner trigger passed
   unanswered, so Q and U margins are design-derived last-resort bounds by the
   rule set before the trigger. Recorded and declared, not re-decided.

4. **Usefulness across arms — dropped, 2026-09-10.**

   FACT. The benchmark task set was never minted into the evaluation
   conditions. `packages/evaluation/condition-manifest.json` v0.2.1-PROPOSED
   (branch `clarence/c-block-05`) binds exactly three tasks —
   `T-swim-croydon`, `T-climb-havering`, `T-yoga-croydon` — under
   `task_set_role: "demonstration"`, with `min_tasks_for_benchmark: 20` and
   `benchmark_requirements.status: "PENDING — benchmark task set not yet
   minted"`. The manifest has carried that status since 2026-08-30. Clarence
   confirmed it as fact from his own artefact on 2026-09-10. The 14 tasks in
   `tasks/` were therefore never rendered in any arm.

   CONSEQUENCE. U is withdrawn from the in-force set in
   `estimand-registry.yaml`. `L_evidence` is the only estimand that remains in
   force. No between-arm contrast is reported anywhere in this stream.

   This was a dependency that never arrived, not a scope decision or a cut: the
   manifest had explicitly remained `PENDING` since 30 August, and I only
   discovered that on 10 September when reviewing Clarence's artefact; it had
   not been flagged to me beforehand.

   The cost is the loss of the P1-vs-P0 evidence-communication contrast — the
   closest direct test of the project's own thesis.

   NOTED. The confound control itself was built and verified:
   `validate_conditions.py` enforces byte-identical projected digests across a
   family and its negative control fires on a deliberately confounded binding.
   What was never produced is the judged material.

5. **F-05 pilot and judging window — not executed, 2026-09-13.**

   FACT. No pilot round was run. No labels were collected. No agreement
   statistic was computed. No artefact of any of these exists on any branch.

   FACT — the chain. The worked lineage pack was the stated blocker on the
   pilot and was never committed to any branch (§6). Clarence's copy reached me
   on 2026-09-10. Assessor availability then closed: Clarence confirmed on
   2026-09-10 that he could judge 11–13 September and not 14–15, against his own
   chapter and individual components. Pilot N was never set, because the sizing
   ratification it depended on has no recorded outcome. The window passed
   without the pilot being run.

   REASON. Time. The three days of the judging window went to other work and
   the pilot was not run in them. This is a resourcing failure on my part, not a
   design decision, and it is recorded as such.

   DECISION, 2026-09-13. Not to run the judging in the time remaining. The
   design requires two assessors labelling independently so that an agreement
   coefficient can be computed; a coefficient produced from labels collected in
   a single unplanned session, under a codebook that was never piloted and never
   frozen and that carries two unresolved placeholders, would be a number I
   could not defend. No number is the more honest outcome than a number
   collected that way.

   CONSEQUENCE. The stream reports no empirical result. `L_evidence` is
   specified and unexecuted. No agreement statistic is reported anywhere.

## 6. Open dependencies not resolved

| Item | Owner |
|---|---|
| `L_decision.unacceptable_decision_condition` | Must be frozen from partner and workflow meaning; Michael's B0 lands with or before 10 Sep |
| Arm count | Not final until 4.2 ratifies the designation pair |
| DEV vintage | Not fixed |
| `LINEAGE_PACK_WORKED_EXAMPLE_v0_1.json` | Not committed to any branch; blocks the F-05 pilot |
| Codebook masking mechanics | Depends on Wesley's harness design |
| Wesley's eligibility to judge relevance | Never ruled on; moot while Q is not collected |

## SIGN-OFF — scope declaration

- **Claim ID:** SCOPE-declaration
- **Artefacts checked:** `docs/evaluation/estimand-registry.yaml` v0.2.0,
  `docs/evaluation/SAP-frozen.md`, `docs/evaluation/F-04-split-assignment-record.md`,
  `docs/evaluation/F-06-sizing-result.md`, `docs/evaluation/F-03-authoring-rules.md`
  — branch `fahmi/proposal-v2-sections-6-7`, commit `F-SCOPE-declaration.md`
- **Outcome:** APPROVED
- **Method:** Checked each drop in §§1–4 against where it is recorded elsewhere — F-02 v0.2.0, the F-04 split record, the F-03 authoring rules and the F-06 sizing result.
- **Conditions:** None.
- **Not covered by this sign-off:** the open dependencies in §6
- **Reference:** CA-01.A9, F-07 PD-6
- **Signed:** Fahmi Alshahabi · 2026-09-08
- **Amended:** 2026-09-13 — §5 entries 4 and 5 appended, and P-BENCH-01 recorded
  as superseded in §4. Sign-off scope unchanged; the appended entries record
  scope reductions, not new approvals.
