# F-05 — Annotation Codebook v0.2-draft

**Project:** Evidence-Bounded Conversational Activity Discovery (London Sport 1)
**Owner:** Fahmi Alshahabi (benchmark / statistics / adjudication stream)
**Status:** DRAFT — constructs frozen 10 Aug 2026 (CB-D1/D2/D3); relevance examples and boundary rules authored 10 Aug 2026 (CB-D4/D5/D6); binding only at the semantic/fixture freeze gate after pilot and ratification.
**Changes from v0.1:** §3 relevance judgment fully specified — ten worked examples, three boundary rules, three derived principles. Usefulness (§2) and evidence-support (§4) examples remain open.
**Authorship notice:** AI-assisted scaffold; all relevance rulings, boundary values and principles in §3 are the owner's own judgments, recorded verbatim from the 10 Aug authoring session. Remaining `[FAHMI]` slots must be authored before pilot.

---

## 0. Frozen design decisions

| ID | Decision | Choice | Rationale (owner) |
|---|---|---|---|
| CB-D1 | Judgment constructs | Three separate judgments: task-level usefulness; listing-level relevance; predicate-level evidence-support | Cleanest estimands — each construct measured alone |
| CB-D2 | Relevance scale | 4-point ordinal (0–3) | Enough resolution for ordinal alpha; few enough for two assessors to hold shared meanings. Resolves F-02 D-2 (scale half) |
| CB-D3 | Alpha weighting | Linear distance weights, frozen before data | Simplest scheme respecting ordinality; nothing left to tune post hoc (A&P §2.6, pp. 564–568) |
| CB-D4 | "Evening" boundary | Evening starts **≥18:00**; 17:00–17:59 is the near-miss band | A stated time window needs a clock, or two assessors draw the line differently and alpha absorbs the difference |
| CB-D5 | Staleness | No occurrence in the past **30 days** and no current/future schedule = stale | A listing that cannot be attended now cannot serve a current request |
| CB-D6 | Distance / borough | An explicitly requested borough is a **hard** constraint; proximity does not satisfy it. Distance may be noted as contextual relevance but never overrides the borough requirement | Prevents "nearby" quietly substituting for what the person asked for |

Distance matrix from CB-D3 (grades 0–3): d = |a−b| / 3.

---

## 1. What assessors see (masking rules)

Assessors judge sampled task–response pairs, seeing: the frozen task text; the response as rendered; the source lineage pack for evidence reconstruction.

Assessors NEVER see: which system/condition produced the response; stage or policy labels; the other assessor's judgments; any headline results. Arbitration occurs without sight of condition labels.
`[FAHMI: confirm masking mechanics against the harness design]`

## 2. Judgment 1 — Task-level usefulness (feeds U)

**Question:** Would this response genuinely serve the person in the task scenario — could they act on it as a real decision?
**Scale:** binary — USEFUL / NOT USEFUL.
**Rule:** usefulness is judged against the task's stated need, not catalogue completeness. An honest "no supported match, here's why" CAN be useful; a confident wrong answer is NOT.
`[FAHMI: 3–5 sentence definition in your own words + 4 worked examples: clear-useful, clear-not, honest-abstention-useful, fluent-but-unsupported-not]`

## 3. Judgment 2 — Listing-level relevance (feeds Q) — SPECIFIED

**Question:** How well does this returned listing match what the task asked for?

**Scale (CB-D2):**
- **3 — Exact:** satisfies every stated constraint
- **2 — Relevant:** satisfies the core need; minor mismatch on a soft preference, or an unstated attribute
- **1 — Marginal:** clearly misses something the task treats as important, or is unusable in practice
- **0 — Not relevant:** does not serve the task

### 3.1 Principles derived from the worked examples

**P1 — Missing evidence is not violated evidence.** An attribute the listing simply does not state (price absent, level absent) keeps the listing plausibly relevant → grade 2. An attribute the listing states *in contradiction* to the request (£12 against "under £5"; mixed-gender against "women-only") → grade 1. This mirrors the project's four-valued evidence model: unknown and false are different states and must not collapse into one score. Whether the missing attribute can be *supported* is Judgment 3's question, not this one.

**P2 — Explicit constraints are hard; near-misses are soft.** Where the person states a constraint, missing it clearly is a grade-1 matter (Saturday against "weekday evening"). Where the listing lands just outside the stated window, it is a soft mismatch → grade 2 (17:15 against "evening"). The boundary between "clearly missed" and "just outside" is set by CB-D4/D5/D6, not by assessor feel.

**P3 — No attribute is privileged.** Borough, activity type, price and audience all demote equally when clearly missed (all → grade 1). What matters is whether a *stated* constraint is clearly unmet, not which category it belongs to.

### 3.2 Worked examples

Reference task for E1–E10: *"Find a beginner-friendly women's swimming session in Tower Hamlets, weekday evening, under £5."*

| # | Listing | Grade | Ruling (owner's words) |
|---|---|---|---|
| E1 | Women's Beginners Swimming, Mile End LC, Tower Hamlets — **Saturday 10:00** — £4.50 | **1** | Activity, location, audience and price match, but weekday evening is an important constraint. Saturday morning is a substantial mismatch, not a minor preference miss. |
| E2 | Same, but **Thursday 17:15** | **2** | 17:15 is close to the requested evening window, so this is a minor timing mismatch rather than a substantive failure. |
| E3 | Poplar Baths, Tower Hamlets — Wednesday 19:00 — beginners, women-only — **price not stated** | **2** | Strong match on activity, location, audience and timing; missing price evidence prevents confirming the under-£5 constraint but does not contradict it. |
| E4 | Women's Swimming (**no level information**), Mile End — Tuesday 19:30 — £4 | **2** | Matches the key stated constraints except beginner status, which is a missing attribute rather than a contradiction. |
| E5 | Women's Beginners Swimming, **Hackney** (~1.5 mi outside) — Tuesday 19:00 — £4.50 | **1** | Right activity, audience, timing and price, but the borough constraint is explicit and Hackney does not satisfy it. |
| E6 | Women's Beginners **Aqua Aerobics**, Tower Hamlets — Thursday 19:00 — £4.50 | **1** | Very close on audience, location, timing and price, but aqua aerobics is a different activity from swimming. |
| E7 | Women's Beginners Swimming, Tower Hamlets — Tuesday 19:00 — **£12** | **1** | Otherwise an excellent match, but £12 clearly violates the explicit under-£5 price constraint. |
| E8 | **Mixed-gender** Beginners Swimming, Tower Hamlets — Tuesday 19:00 — £4.50 | **1** | Right activity, location, timing and price, but mixed-gender directly contradicts the women-only requirement. |
| E9 | Women's Beginners Swimming, Tower Hamlets — Tuesday 19:00 — £4.50 — **SessionSeries, last occurrence 3 months ago**, no current schedule | **1** | It matches the stated attributes, but the absence of a current occurrence makes it unusable as a current session recommendation. |
| E10 | **Facility listing:** Mile End LC — pool, women-only sessions mentioned in the facility description, **no specific session, time or price** | **0** | A facility that merely might contain a suitable session is too indirect; there is no specific qualifying swimming session to match. |

**E9 vs E10 — the distinction, stated explicitly.** Both lack a usable current session, but E9 names a specific, verifiable session that genuinely existed and has expired (a real match, stale), while E10 never names a session at all (no match to evaluate). Specificity is what separates grade 1 from grade 0 here.
`[FAHMI: confirm this is your reasoning, or move one of the two]`

**Depth:** relevance judged to the frozen ranking depth (RATIFY — F-02 D-2 remainder).

## 4. Judgment 3 — Evidence-support verification (feeds L_evidence)

**Question:** For each checked claim/predicate, does the source lineage actually support it?
**Labels:** SUPPORTED / NOT SUPPORTED / CANNOT DETERMINE (with mechanism note).
**Rule:** reconstruction from lineage only; assessors never use outside knowledge of London provision. Bounded non-match claims are checked for the coverage qualifier, never against the real world.
`[FAHMI: define the checkable-claim unit against F-02 loss definitions; 3 worked examples incl. one CANNOT DETERMINE]`

## 5. Difficult cases and escalation

Assessors flag, never guess. Flagged items go to arbitration (roles per RATIFY-19-06). Arbitration records item, both judgments, resolution and a one-line reason. The arbiter never sees condition labels or headline effects.

Resolved case types already covered by §3: near-miss timing (CB-D4), stale listings (CB-D5), out-of-borough proximity (CB-D6), missing vs contradicted attributes (P1), adjacent activity types (E6), facility-level results (E10).
`[FAHMI: add remaining expected types — conflicting price across fields, partial accessibility information, ambiguous geography (blank-borough items are ~73% of the H1 geo file), multi-session series where only some occurrences qualify]`

## 6. Agreement reporting commitments (from A&P 2008, attested)

1. **Weighted Krippendorff's alpha** (linear weights, CB-D3) is the headline coefficient, with bootstrap intervals.
2. **Per-category agreement always reported alongside alpha** — with rare L_evidence events, overall alpha can look healthy while agreement on the rare category is poor; the rare category is the real test (A&P §3.2, pp. 573–574).
3. **Raw agreement and the grade distribution table always published** next to alpha.
4. **No universal threshold claimed.** 0.67/0.8 are not pass/fail (A&P §4.1.3, pp. 576–577); acceptable levels are argued per construct in the SAP, and low agreement narrows the claims built on that construct.
5. **Stated limitation:** two assessors plus arbiter is the minimum viable design; A&P recommend more coders to reduce accidental bias (§3.1, §5.2). Recorded in F-05 limitations and the SAP.

## 7. Pilot plan (development data only)

Round 1: both assessors judge N=`[RATIFY after sizing sim]` development items → weighted alpha + per-category table → revise wording where confusion clusters → Round 2 on fresh development items → freeze. Development items are permanently excluded from locked evaluation. A post-freeze wording change invalidates affected runs unless an untouched reserve exists (work package §7.4).

---
*Change log: v0.1-draft 10 Aug (constructs frozen) → v0.2-draft 10 Aug (§3 relevance specified: E1–E10, CB-D4/D5/D6, P1–P3).*
