# F-05 — Annotation Codebook v0.3-draft (NEVER FROZEN, NEVER PILOTED)

**Project:** Evidence-Bounded Conversational Activity Discovery (London Sport 1)
**Owner:** Fahmi Alshahabi (benchmark / statistics / adjudication stream)
**Status as at 2026-09-13:** This codebook was never frozen and the F-05 pilot was never run. It is published as a design artefact, not as an instrument that governed any collected judgment. No labels were collected under it. See `F-SCOPE-declaration.md` §5 entry 5 and `F-22-stream-status.md`.
**Original status line:** DRAFT — constructs frozen 10 Aug 2026 (CB-D1/D2/D3); boundary rules CB-D4/D5/D6 and the full worked-example set authored 10 Aug 2026. Binding only at the semantic/fixture freeze gate after pilot and ratification. *(That gate was never reached.)*
**Changes from v0.2:** §2 usefulness and §4 evidence-support fully specified (U1–U4, V1–V3) with derived principles. The example set for all three judgments is now complete.
**Authorship notice:** AI-assisted scaffold; every ruling, boundary value and principle in §§2–4 is the owner's own judgment, recorded verbatim from the 10 Aug authoring sessions. Remaining `[FAHMI]` slots were dependencies on other streams, not open authorship; their disposition as at 2026-09-13 is recorded inline below.

---

## 0. Frozen design decisions

| ID | Decision | Choice | Rationale (owner) |
|---|---|---|---|
| CB-D1 | Judgment constructs | Three separate judgments: task-level usefulness; listing-level relevance; predicate-level evidence-support | Cleanest estimands — each construct measured alone |
| CB-D2 | Relevance scale | 4-point ordinal (0–3) | Enough resolution for ordinal alpha; few enough for two assessors to hold shared meanings. Resolves F-02 D-2 (scale half) |
| CB-D3 | Alpha weighting | Linear distance weights, frozen before data | Simplest scheme respecting ordinality; nothing left to tune post hoc (A&P §2.6, pp. 564–568) |
| CB-D4 | "Evening" boundary | Evening starts **≥18:00**; 17:00–17:59 is the near-miss band | A stated time window needs a clock, or two assessors draw the line differently and alpha absorbs the difference |
| CB-D5 | Staleness | No occurrence in the past **30 days** and no current/future schedule = stale | A listing that cannot be attended now cannot serve a current request |
| CB-D6 | Distance / borough | An explicitly requested borough is a **hard** constraint; proximity does not satisfy it | Prevents "nearby" quietly substituting for what the person asked for |

Distance matrix from CB-D3 (grades 0–3): d = |a−b| / 3.

---

## 1. What assessors see (masking rules)

Assessors judge sampled task–response pairs, seeing: the frozen task text; the response as rendered; the source lineage pack for evidence reconstruction.

Assessors NEVER see: which system/condition produced the response; stage or policy labels; the other assessor's judgments; any headline results. Arbitration occurs without sight of condition labels.

> **Masking mechanics — NOT RESOLVED, 2026-09-13.** Wesley confirmed on 2026-09-10 that he owns no assessor-facing harness; the rendering surface is Clarence's public application. Two structural limits on masking were identified and are recorded rather than fixed: P2 is a multi-turn episode while P0 and P1 are lists, so arms are distinguishable by format regardless of labels (Wesley, 2026-09-10); and evidence-state wording exists only in P1 and P2, which identifies those arms to their author (Clarence, 2026-09-10). Blinding by hidden labels alone was therefore not achievable as specified. No judgments were collected, so nothing was masked or un-masked in practice.

## 2. Judgment 1 — Task-level usefulness (feeds U) — SPECIFIED, NOT IN FORCE

> **NOT_IN_FORCE as at 2026-09-10.** U is withdrawn. The benchmark task set was never minted into the P0/P1/P2 conditions, so no arm-rendered material existed to judge. See `F-SCOPE-declaration.md` §5 entry 4. Retained as a design artefact.

**Question:** Would this response genuinely serve the person in the task scenario — could they act on it as a real decision?
**Scale:** binary — USEFUL / NOT USEFUL. Judged on the **whole response**, not individual listings.

> **Judgment unit — unresolved.** `condition-manifest.json` records P2's judgment unit as the whole multi-turn episode, while this section specifies the whole response (Clarence, 2026-09-10). The episode-level anchor was never written, because the construct was withdrawn before the amendment was needed.

### 2.1 Principles

**PU1 — Usefulness means evidence-grounded service, not user satisfaction.** A response that looks and reads like a good answer but rests on unsupported inference is NOT USEFUL, however satisfying it would feel to receive. The system is not permitted to be right by accident.

**PU2 — Honest failure can be useful.** A clear statement that nothing matches, paired with actionable near-matches and an explanation of what is missing, serves the person's decision and is USEFUL. Abstention is a designed output, not a failure state.

**PU3 — Fluency and volume are not evidence.** Confident presentation, large result counts and absence of caveats carry no weight in this judgment.

### 2.2 Worked examples

Reference task: *"Find a beginner-friendly women's swimming session in Tower Hamlets, weekday evening, under £5."*

| # | Response | Verdict | Ruling (owner's words) |
|---|---|---|---|
| U1 | Three women's beginner sessions in Tower Hamlets, all weekday evenings, all under £5, times and prices shown | **USEFUL** | It directly satisfies all stated constraints with verifiable details. |
| U2 | "I found 12 swimming sessions in Tower Hamlets!" — mixed-gender, various times, prices mostly unstated; fluent, confident, no caveats | **NOT USEFUL** | It ignores key constraints, despite being fluent and confident. |
| U3 | "No sessions match all your constraints. Three come close but don't state their price — here they are, with links to check directly." | **USEFUL** | An honest statement of no exact matches plus actionable near-matches is useful. |
| U4 | One perfect-looking match — right day, time, price, women-only, beginners — but the listing never states women-only; the system inferred it from the venue description | **NOT USEFUL** | The apparent match relies on unsupported inference, so the answer is not evidence-grounded. |

**U3 vs U4 — the pairing that defines the construct.** U3 fails to deliver a match and is useful; U4 delivers an apparent match and is not. Usefulness tracks whether the person can *act on evidence*, not whether they got what they hoped for.

## 3. Judgment 2 — Listing-level relevance (feeds Q) — SPECIFIED, NOT IN FORCE

> **NOT_IN_FORCE as at 2026-09-08.** Q is not collected under the scope freeze. This section is retained rather than deleted: motion 4.3, which was the basis for removing it, has no recorded ratification outcome, and deleting a section on the authority of an unratified motion would misstate the record. Retained, marked, and not in force.

**Question:** How well does this returned listing match what the task asked for?

**Scale (CB-D2):**
- **3 — Exact:** satisfies every stated constraint
- **2 — Relevant:** satisfies the core need; minor mismatch on a soft preference, or an unstated attribute
- **1 — Marginal:** clearly misses something the task treats as important, or is unusable in practice
- **0 — Not relevant:** does not serve the task

### 3.1 Principles

**P1 — Missing evidence is not violated evidence.** An attribute the listing does not state (price absent, level absent) keeps it plausibly relevant → grade 2. An attribute stated *in contradiction* to the request (£12 against "under £5"; mixed-gender against "women-only") → grade 1. This mirrors the four-valued evidence model: unknown and false are different states. Whether a missing attribute can be *supported* is Judgment 3's question, not this one.

**P2 — Explicit constraints are hard; near-misses are soft.** Clearly missing a stated constraint is grade 1 (Saturday against "weekday evening"); landing just outside the stated window is grade 2 (17:15 against "evening"). The boundary is set by CB-D4/D5/D6, not by assessor feel.

**P3 — No attribute is privileged.** Borough, activity type, price and audience all demote equally when clearly missed. What matters is whether a *stated* constraint is unmet, not which category it belongs to.

### 3.2 Worked examples

Reference task as above.

| # | Listing | Grade | Ruling (owner's words) |
|---|---|---|---|
| E1 | Mile End LC, Tower Hamlets — **Saturday 10:00** — £4.50 | **1** | Activity, location, audience and price match, but weekday evening is an important constraint. Saturday morning is a substantial mismatch, not a minor preference miss. |
| E2 | Same, but **Thursday 17:15** | **2** | 17:15 is close to the requested evening window, so this is a minor timing mismatch rather than a substantive failure. |
| E3 | Poplar Baths, Tower Hamlets — Wed 19:00 — beginners, women-only — **price not stated** | **2** | Strong match on activity, location, audience and timing; missing price evidence prevents confirming the under-£5 constraint but does not contradict it. |
| E4 | Women's Swimming (**no level information**), Mile End — Tue 19:30 — £4 | **2** | Matches the key stated constraints except beginner status, which is a missing attribute rather than a contradiction. |
| E5 | **Hackney** (~1.5 mi outside) — Tue 19:00 — £4.50 | **1** | Right activity, audience, timing and price, but the borough constraint is explicit and Hackney does not satisfy it. |
| E6 | Women's Beginners **Aqua Aerobics**, Tower Hamlets — Thu 19:00 — £4.50 | **1** | Very close on audience, location, timing and price, but aqua aerobics is a different activity from swimming. |
| E7 | Tower Hamlets — Tue 19:00 — **£12** | **1** | Otherwise an excellent match, but £12 clearly violates the explicit under-£5 price constraint. |
| E8 | **Mixed-gender** Beginners Swimming, Tower Hamlets — Tue 19:00 — £4.50 | **1** | Right activity, location, timing and price, but mixed-gender directly contradicts the women-only requirement. |
| E9 | Tower Hamlets — Tue 19:00 — £4.50 — **last occurrence 3 months ago**, no current schedule | **1** | It matches the stated attributes, but the absence of a current occurrence makes it unusable as a current session recommendation. |
| E10 | **Facility listing:** Mile End LC — pool, women-only sessions mentioned in the facility description, **no specific session** | **0** | A facility that merely might contain a suitable session is too indirect; there is no specific qualifying swimming session to match. |

**E9 vs E10.** Both lack a usable current session, but E9 names a specific, verifiable session that existed and has expired (a real match, stale), while E10 never names a session at all (no match to evaluate). Specificity separates grade 1 from grade 0.

**Depth:** relevance judged to the frozen ranking depth (RATIFY — F-02 D-2 remainder). *Never ratified; moot while Q is not collected.*

## 4. Judgment 3 — Evidence-support verification (feeds L_evidence) — SPECIFIED, NOT EXECUTED

> **Status as at 2026-09-13.** `L_evidence` is the only estimand that remained in force. It was specified and never executed: no pilot was run, no labels were collected, and no agreement statistic was computed. See `F-SCOPE-declaration.md` §5 entry 5.

**Question:** For each checked claim, does the source lineage actually support it?
**Labels:** SUPPORTED / NOT SUPPORTED / CANNOT DETERMINE (the latter two carry a mechanism note).
**Rule:** reconstruction from lineage only. Assessors never use outside knowledge of London provision.

### 4.1 Principles

**PV1 — The evidence store is the boundary of support.** A claim that may well be true in the world but traces to a source outside the store is NOT SUPPORTED. Truth is not the test; supportability by stored lineage is.

**PV2 — Staleness is indeterminacy, not falsity.** Where lineage establishes that something *was* valid but cannot establish it *now*, the label is CANNOT DETERMINE with a staleness mechanism — never NOT SUPPORTED. Collapsing expiry into falsity would erase the distinction between a harvest problem and a publisher problem, which have different remedies. Consistent with CB-D5.

**PV3 — Mechanism is always recorded.** Every non-SUPPORTED label carries its mechanism (source absence, outside-store provenance, staleness, projection loss, conflict), because the mechanism is what makes the finding actionable for publishers.

### 4.2 Worked examples

| # | Claim and lineage | Label | Ruling (owner's words) |
|---|---|---|---|
| V1 | *"£4.50 per session."* Lineage: `price` = 4.50, `priceCurrency` = GBP | **SUPPORTED** | The lineage directly contains the stated price and GBP currency. |
| V2 | *"step-free access available."* Lineage: no accessibility fields; claim traces to the venue's general website, not in the evidence store | **NOT SUPPORTED** *(mechanism: outside-store provenance)* | The claim comes from a source outside the evidence store; it cannot be supported by the stored lineage. |
| V3 | *"runs every Tuesday at 19:00."* Lineage: valid SessionSeries Schedule, but stated end date passed two months ago; no later occurrences published | **CANNOT DETERMINE** *(mechanism: staleness)* | The historical schedule supports that it ran Tuesdays at 19:00, but its expiry means the current recurrence cannot be established. |

## 5. Difficult cases and escalation

Assessors flag, never guess. Flagged items go to arbitration (roles per RATIFY-19-06). Arbitration records item, both judgments, resolution and a one-line reason. The arbiter never sees condition labels or headline effects.

Resolved case types already covered: near-miss timing (CB-D4), staleness (CB-D5, PV2), out-of-borough proximity (CB-D6), missing vs contradicted attributes (P1), adjacent activity types (E6), facility-level results (E10), outside-store provenance (PV2/V2), unsupported inference presented fluently (PU1/U4).

> **Pilot-observed case types — NOT POPULATED, 2026-09-13.** This slot was to be filled from the pilot, which was never run. The candidates identified in advance were: conflicting price across fields, partial accessibility information, ambiguous geography (blank-borough items are ~73% of the H1 geo file), and multi-session series where only some occurrences qualify. They remain untested expectations, not findings.

## 6. Agreement reporting commitments (from A&P 2008, attested)

1. **Weighted Krippendorff's alpha** (linear weights, CB-D3) is the headline coefficient, with bootstrap intervals.
2. **Per-category agreement always reported alongside alpha** — with rare L_evidence events, overall alpha can look healthy while agreement on the rare category is poor; the rare category is the real test (A&P §3.2, pp. 573–574).
3. **Raw agreement and the grade distribution table always published** next to alpha.
4. **No universal threshold claimed.** 0.67/0.8 are not pass/fail (A&P §4.1.3, pp. 576–577); acceptable levels are argued per construct in the SAP, and low agreement narrows the claims built on that construct.
5. **Stated limitation:** two assessors plus arbiter is the minimum viable design; A&P recommend more coders to reduce accidental bias (§3.1, §5.2). Recorded in F-05 limitations and the SAP.

> **Not exercised.** No agreement coefficient was computed, because no labels were collected. These commitments stand as specification only.

## 7. Pilot plan (development data only)

> **NOT EXECUTED, 2026-09-13.** Pilot N was never set — the sizing ratification it depended on has no recorded outcome — and no pilot round was run. See `F-SCOPE-declaration.md` §5 entry 5.

Round 1: both assessors judge N=`[RATIFY after sizing sim]` development items → weighted alpha + per-category table → revise wording where confusion clusters → Round 2 on fresh development items → freeze. Development items are permanently excluded from locked evaluation. A post-freeze wording change invalidates affected runs unless an untouched reserve exists (work package §7.4).

---
*Change log: v0.1 10 Aug (constructs frozen) → v0.2 10 Aug (§3 relevance: E1–E10, CB-D4/D5/D6, P1–P3) → v0.3 10 Aug (§2 usefulness: U1–U4, PU1–PU3; §4 evidence-support: V1–V3, PV1–PV3). Example set complete for all three judgments. 2026-09-13: status stamps added throughout — never frozen, never piloted, §§2 and 3 not in force, open slots dispositioned. No construct definition, principle, boundary value or worked example was altered.*
