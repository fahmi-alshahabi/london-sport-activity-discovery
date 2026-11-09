# C-16 — Executable assurance case

**Owner (proposed):** Clarence (coordinates evidence) · **Independent assurance reviewer + authority:** not Clarence (WP §2.4, §2.6)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Basis: WP §12.1 (assurance chain), §12.9 (maturity states). Machine source: `docs/assurance/assurance-case.json`; runner: `validate_assurance.py`; generated view: `assurance-case.md`.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. Clarence
> coordinates the evidence chain; he **cannot** issue the residual-risk acceptance or the maturity
> decision — an authorised person does (WP §2.4, §12.9).

## 1. What it is

The single graph that ties Clarence's whole stream together, following the WP §12.1 chain:

```
permitted use → affected party & harm → control → executable test/evidence → independent review → residual risk → authorised maturity decision
```

It is **executable**: `validate_assurance.py` detects orphans (a missing use/harm/control/test/
reviewer/authority blocks the affected maturity state) **and runs every linked check live**, so the
graph shows exactly which claims are currently evidenced by passing tests versus which still await a
human gate.

## 2. Current state (live)

Fifteen claims, each linked to the real checks built across the stream. As run:

- **All fourteen linked test suites pass** (C-BLOCK-05 invariants, C-09 checker + mutation, C-01
  register, C-11 wording, C-04 IA, action-card gates, C-17 conditions, public slice, staff slice,
  C-13 privacy, C-15 ethics, C-14 security, C-08 conversation, CA-5 K7 reading log).
- **Graph is sound** — no orphans (every claim has a harm, a control with an owner, ≥1 resolving
  test, a reviewer scope and an authority).
- **Every claim's maturity verdict is BLOCKED**, on `non-author review pending` and
  `authority decision pending`. This is the correct, honest state: the executable evidence is green,
  but a maturity state is only reached when a non-author reviewer signs and the named authority
  records the decision (WP §12.9) — which Clarence cannot do himself.

Orphan detection is not vacuous: removing a control, dangling a test id, or omitting a reviewer are
each flagged (verified).

## 3. Claims covered

CL-1 non-interference · CL-2 no-collapse of unknown · CL-3 no unverified token · CL-4 certified
order/abstention · CL-5 disclosure + role gating · CL-6 independent checker · CL-7 no evaluation
confound · CL-8 governed-action gates · CL-9 reconciliation dispositioned · CL-10 accessibility
(evaluated-toward, with manual/AT testing recorded as outstanding residual).

## 4. How to run

```bash
python docs/assurance/validate_assurance.py     # runs all linked checks, renders assurance-case.md
```

Exit 0 means the graph is well-formed **and** all linked executable evidence passes; the per-claim
maturity verdicts separately report the human gates still open.

## 5. What remains (the human gates, by design)

For each claim: a **non-author** review (C-BLOCK-03 for accessibility; Michael/Wesley/Fahmi for their
boundaries) and a **named authority** decision (Section 15 / RATIFY items). Populating `reviewer.name`
+ `status: done` and `authority.holder` + `status: done` in `assurance-case.json` — only after the
real reviews happen — moves a claim's verdict to AUTHORISED. Those are not Clarence's to tick.
