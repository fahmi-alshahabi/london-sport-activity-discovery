# C-07 — Staff assurance application (slice)

**Owner (proposed):** Clarence · **Review:** Fahmi (evaluation parity) + Wesley (integration/IAM) + non-author HCI reviewer
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Stack per ADR-0001 (FastAPI SSR, no-JS core). Maturity: `research_demonstration` (C-BLOCK-12).

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. The role
> gate is a demonstration stub — real IAM/auth/break-glass is Wesley's (Section 16, C-BLOCK-04).

## What it demonstrates

A restricted, **role-gated** workbench that is **evidence-symmetric** with the public app yet
**authority-asymmetric**: it renders the **staff projection** of the same `DecisionEnvelope`
(receipts, why-not, mechanisms, aggregates) that the public projection drops.

- **Public-state replay** — recomputes the digest of the retained public payload and confirms it
  matches (semantic replay, C-BLOCK-09).
- **Failure-chain explorer** — acquisition → reconstruction/evidence → gate (why-not) → interface,
  using staff-only mechanism and blocking-state detail.
- **Collection / vintage health** — denominators and freshness, with provision framed as a lower bound.
- **Action-card workflow** — the §8.5 state machine surfaced with its gates; no step skips review/approval.
- Every panel carries the **§8.2 provenance block** (universe, denominator, vintage, versions,
  access role, permitted action, permitted wording).

## Verified (`apps/staff-assurance/test_staff.py`, all passing)

- **Role gate:** every staff route returns 403 with no valid role and 200 with one; the forbidden
  page shows no staff content.
- **Evidence symmetry:** staff and public agree on terminal decision, scope, recommendation,
  candidate id + order, vintage.
- **Authority asymmetry:** `internal_score`, `model_version` and why-not `blocking_state` are present
  in the staff view and **absent** from the public projection.
- **Public-state replay:** stored digest == recomputed for every scenario.
- **Value-level non-interference:** mutating only non-public fields leaves the public projection
  byte-identical (reuses the C-BLOCK-05 invariant).
- **Action-card no-skip:** `drafted`/`investigated` cannot reach approval/send; sending requires an
  authorised role.
- **Accessibility (static subset)** clean on every staff page and the forbidden page; no
  RESEARCH_RESTRICTED identity (`episode_id`/`trace_id`) leaks into the staff view.

## Boundary / next

PROPOSED. Needs: real IAM from Wesley (`RATIFY-15-06`, C-BLOCK-04) replacing the header stub; a
non-author HCI review; and the remaining workspaces (bounded-scenario lab, recommender/AI assurance,
release/incident). This slice, with the public slice, gives the evaluated **W0/W1/W1-NA** staff
conditions their functioning `W1` build for Fahmi (C-BLOCK-06).
