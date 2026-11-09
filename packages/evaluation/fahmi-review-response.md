# Review response — Fahmi on `condition-manifest.json` (C-17)

**Reviewer:** Fahmi (evaluation-stream owner) · **Artefact:** `packages/evaluation/condition-manifest.json`
**Received:** 2026-08 · **Disposition by:** Clarence (owner of the frozen builds) · **Seam:** C-BLOCK-06 / F-BLOCK-09
**Result:** all four findings **ACCEPTED and implemented**; `validate_conditions.py` now enforces each
(`ALL CONDITION CHECKS PASS`, and each new gate is proven to fail on its defect).

| # | Finding | Disposition | What changed | Enforced by |
|---|---------|-------------|--------------|-------------|
| R1 | 3 tasks → power ceiling ~0.18; ~20+ needed for a benchmark | Accepted | Current 3 explicitly marked `task_set_role: "demonstration"`; `benchmark_requirements` records the ≥20 minimum, the power rationale, and joint ownership | validator: a `benchmark` set with `< min_tasks_for_benchmark` fails; a `demonstration` set is reported as fixtures |
| R2 | Origins/publishers not recorded → can't build PD-6 splits / CAL-RISK clusters | Accepted | `origin` + `publisher` added to every task (demonstration values for the fixtures) | validator: every task must record non-empty `origin` + `publisher` |
| R3 | No field/convention to mint a conversation-changed (repaired) query task | Accepted | `repair_minting` convention added — a repaired task sets `repair_of: <base task_id>`, a distinct id, and its own envelope (exempt from same-envelope-as-base; the changed query is the point) | validator: a `repair_of` must reference a distinct, existing base task |
| R4 | Conditions not bound to a vintage → two conditions could run at different vintages | Accepted | `frozen_vintage` added at the manifest level | validator: every task must resolve an envelope at `frozen_vintage`, else fail |

## Remaining (joint / Fahmi's to own)
- **Mint the ≥20 benchmark task set** with real feed origins and publishers, bound to Fahmi's power
  target and sampling (RATIFY-14-07/08). The manifest now *carries the structure* for this; the
  demonstration fixtures and placeholder origins/publishers are replaced when the real set is minted.
- This closes the manifest side of **F-BLOCK-09** (the repair-minting convention the repair screen
  needs); the shared `L_reliance` referent (CA-1 / C-BLOCK-15) is unchanged and still binds to the
  terminal `DecisionEnvelope`.

## Evidence
`python packages/evaluation/validate_conditions.py` → the four new checks pass on the real manifest;
negative proofs confirm each fails on a missing origin/publisher, a dangling `repair_of`, and a
`benchmark` role below the floor. Recorded here so the disposition is not "silence" (WP §3).
