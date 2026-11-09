# F-22 — Evaluation stream status

**Owner:** Fahmi Alshahabi
**Date:** 2026-09-13
**Branch:** `fahmi/proposal-v2-sections-6-7`
**Status:** Design complete. Execution not carried out. Reasons recorded below.

---

## 1. What this stream was for

The evaluation stream existed to answer whether the proposed
evidence-communication conditions could produce more useful evidence for
decisions, rather than simply whether the system could produce an answer. In
particular, it was intended to test whether presenting the same underlying
evidence in different ways changed the usefulness of that evidence across the
defined conditions. The stream therefore needed a defensible comparison between
conditions, supported by a benchmark and judged material, rather than a
collection of illustrative examples. Where that comparison could not be made
honestly, the relevant claim was withdrawn rather than inferred.

## 2. What was designed and signed off

| Artefact | File | Signed | Non-author review |
|---|---|---|---|
| Estimand registry (F-02) | `estimand-registry.yaml` v0.2.0 | 2026-09-08 | Not recorded |
| Statistical analysis plan | `SAP-frozen.md` | 2026-09-08 | Not recorded |
| Sizing analysis (F-06) | `F-06-sizing-result.md` | 2026-09-03 | Not recorded |
| Benchmark task set (F-03) | `tasks/`, 14 templates | 2026-09-08 | Not recorded |
| Annotation codebook (F-05) | `codebook-v0.3.md` | Never frozen | Not recorded |
| Assessor assignments (F-01) | `F-01-assessor-assignments.md` | 2026-08-29 | Not recorded |
| Scope declaration | `F-SCOPE-declaration.md` | 2026-09-08 | Not recorded |
| Interface review (F-15) | `F-15-interface-review-signed.md` | Signed | n/a — is itself a review |

**Verified reproducible as at 2026-09-13.** The 14 task templates check against
`tasks/MANIFEST-sha256.txt` (14/14 OK) and the structural linter passes: 14
templates, 10 LOCKED / 4 DEV, six families, no cross-task defects.

The substantive design finding is the sizing result. F-06 established that the
confirmatory test of H-P was not available at any feasible design size — the
sensitivity grid required 30–762 templates against an assessor-hours envelope
permitting roughly 21–28. That is a finding about what this project could
establish, reached before any outcome data existed. It is also the behaviour the
ratified proposal specifies: §9 states that if the feasible design cannot support
the confirmatory rule, the result is reclassified as estimative before LOCKED
evaluation.

## 3. What was not executed, and why

| Not executed | Recorded where | Date |
|---|---|---|
| Confirmatory test of H-P | F-SCOPE §1, F-06 | 2026-09-03 |
| Usefulness across arms | F-SCOPE §5 entry 4 | 2026-09-10 |
| F-05 codebook pilot | F-SCOPE §5 entry 5 | 2026-09-13 |
| Judging window, both assessors | F-SCOPE §5 entry 5 | 2026-09-13 |
| Baseline unacceptable-decision rate | F-02 Row 5, F-BLOCK-09 | 2026-09-13 |
| F-08, F-10, F-11, F-12, F-13, F-14, naturalistic suite | F-SCOPE §§3–4 | 2026-09-08 |

The confirmatory test was first demoted when F-06 showed that the available
assessor-hours could not support the required template counts; that decision is
recorded in the sizing result and the scope declaration. Usefulness across arms
was then withdrawn when the condition manifest was found still to have the
benchmark task set marked `PENDING`; that dependency had existed since 30 August
and was confirmed from Clarence's artefact on 10 September. The pilot and
judging were subsequently not completed: the lineage pack remained uncommitted,
Clarence's copy arrived on 10 September, and the three days of the judging window
went to other work — a resourcing failure on my part, not a design decision. Each
step was recorded with the relevant artefact rather than being silently removed
from the record.

These are therefore instances of the same practice: refusing to turn an
unsupported design or an incomplete execution into a number that could be
presented as evidence. The confirmatory result would not have been defensible at
the available sample size; the between-arm usefulness contrast could not be
produced without the benchmark conditions; and the pilot and judging could not
honestly support an agreement result without the required material and a
completed process.

The last two constraints were not decisions made in advance. The missing
benchmark dependency and the failure to complete the pilot and judging emerged
during execution and are recorded as such, rather than being retrospectively
presented as planned design choices.

## 4. What this stream reports

Nothing empirical. `L_evidence` is specified and unexecuted. U is withdrawn. Q
was never collected. No agreement statistic was computed, because no labels were
collected.

The inputs it would have consumed do exist and are frozen: Michael's corpus-wide
S1/S1b delivery of 2026-09-10, independently hash-verified and recounted from the
underlying JSONL (see `F-BLOCK-09-decision.md`).

A stream with a documented method, verified inputs, and explicit limits still
provides a reproducible account of what could and could not be established, but
it does not provide the missing evaluation result.

## 5. Assurance gaps, stated

- **No independent review of this stream was recorded.** C-20 was requested of
  Clarence on 2026-09-10; the worksheet was pushed the same day with artefact
  excerpts pulled and findings left blank (`089615c`), and was not returned. The
  deliverable register also assigns Michael review of F-04 and F-06; neither is
  recorded. Every sign-off in §2 is therefore author-signed only.
- **Adjudication concentrates on one person.** The eligibility matrix flags at
  §3.1 that the sole remaining arbiter is also the sole task author and the
  codebook author. No judgments were collected, so the conflict never operated —
  but the design carries it.
- **Blinding was not achievable as specified.** P2 is a multi-turn episode and
  P0/P1 are lists, so arms are distinguishable by format regardless of labels
  (Wesley, 2026-09-10). Evidence-state wording exists only in P1 and P2, which
  identifies those arms to their author (Clarence, 2026-09-10). Recorded as a
  declared limitation, not a fixable defect.
- **Six motions bear on this stream and none has a recorded outcome** — 4.1,
  4.2, 4.3, 4.6, 4.7, 4.8. The 2026-09-04 scribe notes were never filed and no
  team member holds them.
- **The codebook was never frozen.** `codebook-v0.3.md` carries two unresolved
  placeholders and was never piloted.

The weaknesses are listed because they materially limit what a marker can
conclude from the stream, and hiding them would make the record look stronger
than the evidence warrants. Making them explicit lets the work be judged on what
was actually established rather than on what the design intended to establish.

## 6. If this stream were resumed

1. **Mint the 14 benchmark tasks into the P0/P1/P2 conditions.** Everything
   downstream depends on it. `condition-manifest.json` also sets
   `min_tasks_for_benchmark: 20` against the 14 authored, so either the task set
   grows or the threshold is renegotiated.
2. **Run the F-05 pilot** on predicate-level items from the lineage packs, set
   pilot N, resolve the two open placeholders, then freeze the codebook.
3. **Ratify the six open motions**, or record them as never ratified, before any
   judging opens.
4. **Secure two eligible assessors per construct**, given the recusals in F-01
   and the open question of whether Clarence's recusal extends to
   evidence-support.
5. **Then execute**, and compute agreement as specified in the SAP — weighted
   Krippendorff's alpha with bootstrap uncertainty, raw agreement and prevalence,
   n stated.

---

## SIGN-OFF — stream status

- **Claim ID:** F-22-stream-status
- **Artefacts checked:** all files listed in §2, on branch
  `fahmi/proposal-v2-sections-6-7` as at 2026-09-13
- **Method:** Re-ran the task manifest check (14/14 OK) and the structural linter
  (PASS); read each artefact in §2 against the status claimed for it here;
  verified the six delivery member hashes and recounted the S1b occurrence total
  from the underlying JSONL.
- **Outcome:** ACCURATE AS AT DATE
- **Conditions:** None.
- **Not covered by this sign-off:** any claim about work owned by other streams
- **Signed:** Fahmi Alshahabi · 2026-09-13
