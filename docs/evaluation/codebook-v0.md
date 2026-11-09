# F-05 — Annotation Codebook v0.1-draft

**Project:** Evidence-Bounded Conversational Activity Discovery (London Sport 1)
**Owner:** Fahmi Alshahabi (benchmark / statistics / adjudication stream)
**Status:** DRAFT — constructs frozen by owner decision 10 Aug 2026 (D1/D2/D3 below); wording and examples under development; becomes binding only at the semantic/fixture freeze gate after pilot and ratification.
**Authorship notice:** AI-assisted scaffold around owner-frozen design decisions. Sections marked `[FAHMI]` must be authored by Fahmi in his own words before pilot. Decision rationales recorded per the decision log.
**Reviewer:** per the eligibility matrix (RATIFY-19-06) — assessors are trained on this document and development examples only.

---

## 0. Frozen design decisions (recorded 10 Aug 2026, owner: Fahmi)

| ID | Decision | Choice | Rationale (owner) |
|---|---|---|---|
| CB-D1 | Judgment constructs | **Three separate judgments** per sampled item: task-level usefulness; listing-level relevance; predicate-level evidence-support | Cleanest estimands — each construct measured alone; U, Q and L_evidence never share one muddled score |
| CB-D2 | Relevance scale | **4-point ordinal** (0–3) | Enough resolution for ordinal alpha; few enough grades for two assessors to hold shared meanings. Resolves F-02 discrepancy D-2 (scale half); metric depth still RATIFY |
| CB-D3 | Alpha weighting | **Linear distance weights**, frozen now, before any data | Simplest scheme respecting ordinality; nothing left to tune post hoc — satisfies the A&P fix-weights-first rule (§2.6, pp. 564–568) |

Distance matrix implied by CB-D3 (grades 0–3): d = |a−b| / 3 → adjacent grades disagree ⅓, opposite ends disagree 1. This matrix is part of the freeze commit.

---

## 1. What assessors see (masking rules)

Assessors judge sampled task–response pairs. For every item they see: the frozen task text; the response as rendered (decision, listings, explanations); and the source lineage pack for evidence reconstruction.

Assessors NEVER see: which system/condition produced the response; stage or policy labels; the other assessor's judgments; any headline results. Arbitration happens without sight of condition labels. `[FAHMI: confirm the masking mechanics with the harness design — what file/interface actually delivers items?]`

## 2. Judgment 1 — Task-level usefulness (feeds U)

**Question to assessor:** Would this response genuinely serve the person in the task scenario — could they act on it as a real decision?
**Scale:** binary — USEFUL / NOT USEFUL.
**Rule of interpretation:** usefulness is judged against the task's stated need, not against completeness of the catalogue. An honest "no supported match, here's why" CAN be useful; a confident wrong answer is NOT.
`[FAHMI: write 3–5 sentence definition in your own words + at least 4 worked examples from development tasks: clear-useful, clear-not, honest-abstention-useful, fluent-but-unsupported-not]`

## 3. Judgment 2 — Listing-level relevance (feeds Q)

**Question to assessor:** How well does this returned listing match what the task asked for?
**Scale (CB-D2, frozen):**
- **3 — Exact:** satisfies every stated constraint of the task
- **2 — Relevant:** satisfies the core need; minor mismatch on a soft preference
- **1 — Marginal:** related activity or area, but misses something the task treats as important
- **0 — Not relevant:** does not serve the task
`[FAHMI: one worked example per grade, drawn from development queries — write these yourself; they are what the assessors will actually lean on]`
**Depth:** relevance judged to the frozen ranking depth (value: RATIFY — F-02 D-2 remainder).

## 4. Judgment 3 — Evidence-support verification (feeds L_evidence)

**Question to assessor:** For each checked claim/predicate, does the source lineage actually support it?
**Labels:** SUPPORTED / NOT SUPPORTED / CANNOT DETERMINE (with mechanism note).
**Rule:** reconstruction from lineage only — assessors never use outside knowledge of London provision. "No observed listed match" claims are checked for the coverage qualifier, never against the real world.
`[FAHMI: define the checkable-claim unit precisely against the F-02 loss definitions; 3 worked examples incl. one CANNOT DETERMINE]`

## 5. Difficult cases and escalation

Assessors flag, never guess. Flagged items go to arbitration (roles per eligibility matrix). Arbitration records: item, both judgments, resolution, one-line reason. Arbiter never sees condition labels or headline effects.
`[FAHMI: list the 4–6 difficult-case types you expect from development data — ambiguous geography, stale schedule, partial accessibility info, conflicting price... — with the ruling for each]`

## 6. Agreement reporting commitments (from A&P 2008, attested row 2)

Frozen commitments, stated before any data:
1. **Weighted Krippendorff's alpha** (linear weights per CB-D3) is the headline coefficient, with bootstrap intervals.
2. **Per-category agreement is always reported alongside alpha** — with rare L_evidence events, overall alpha can look healthy while agreement on the rare category is poor; the rare category IS the test (A&P §3.2, pp. 573–574).
3. **Raw agreement and the grade distribution table are always published** next to alpha — alpha is never the whole story.
4. **No universal threshold is claimed.** 0.67/0.8 are not treated as pass/fail (A&P §4.1.3, pp. 576–577); the acceptable level is argued per construct in the SAP, and low agreement on a construct narrows the claims built on it rather than being explained away.
5. **Stated limitation:** two assessors + arbiter is the minimum viable design; A&P recommend more coders to reduce accidental bias (§3.1/§5.2). Recorded in F-05 limitations and the SAP.

## 7. Pilot plan (development data only)

Round 1: both assessors judge N=`[RATIFY after sizing sim]` development items → compute weighted alpha + per-category table → revise wording where confusion clusters → Round 2 on fresh development items → freeze. Development items are permanently excluded from locked evaluation. A post-freeze wording change invalidates affected runs unless an untouched reserve exists (per work package §7.4).

---
*Change log: v0.1-draft created 10 Aug 2026 — constructs frozen (CB-D1/D2/D3); all `[FAHMI]` slots open; binding only at semantic/fixture gate.*
