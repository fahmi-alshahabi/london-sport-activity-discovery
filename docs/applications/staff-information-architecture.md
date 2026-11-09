# C-06 — Staff assurance information architecture

**Owner (proposed):** Clarence · **Review:** Wesley (integration/IAM) + partner route (Section 18)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Basis: WP §8 (staff application), §2.2 (chatbot boundary), Section 18.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. Real
> authentication/IAM/break-glass is Wesley's (Section 16, C-BLOCK-04); the app's role gate is a
> demonstration stub.

## 1. One system, two applications (WP §4.1)

The staff workbench is **evidence-symmetric** with the public app (same terminal decision, scope,
candidate order, vintage) but **authority-asymmetric** (staff may inspect receipts, why-not,
mechanisms, aggregates the public must never receive). Both are projections of one
`DecisionEnvelope`; the disclosure classes decide which fields each plane sees.

## 2. Mandatory workspaces (WP §8.1)

| Workspace | Decision it supports | Built in the slice? |
|-----------|----------------------|---------------------|
| Collection / vintage health | Is the corpus usable for the declared vintage? | Yes |
| Task answerability | Which queries are supported / bounded / indeterminate? | Partial (via scenarios) |
| Failure-chain explorer | Where did a public outcome become limited? | Yes |
| Receipt inspector / public-state replay | Can this public payload be reconstructed? | Yes (digest replay) |
| Bounded scenario laboratory | What could change under an explicit hypothetical? | Yes (bounds; no realised-gain) |
| Recommender / AI assurance | Is the system within its frozen risk/coverage envelope? | Yes (vintage/coverage; rates by Fahmi) |
| Equity-relevant audit | Which tasks/origins carry evidence burden? | Yes (contextual, not identity) |
| Public-state replay | What exactly did the public user receive? | Yes |
| Action / escalation | What governed next step is justified? | Yes (action-card workflow) |
| Release / incident control | What maturity/failure state applies? | Yes (maturity + kill/rollback stubs) |

## 3. Every staff panel binds (WP §8.2)

Universe; numerator/denominator; inclusion/exclusion; weights & effective sample size; interval/method;
snapshot/vintage; code/analysis/model/schema version; access role & purpose; permitted action;
permitted wording/limitations. The slice renders a **panel-provenance block** carrying these on every
workspace.

## 4. Staff prohibitions (WP §8.3)

No borough/publisher/staff league tables; no unexplained traffic-light scores; no individual staff
productivity monitoring; no mutable ad-hoc SQL as official evidence; no arbitrary model/tool
authority; no imputation presented as publisher data; no automatic publisher contact, escalation,
threshold change or action approval; no diagnosis of real provision from listing absence; no
cross-role access merely because a user is "staff"; no research telemetry silently repurposed.

## 5. Role / action matrix

Capabilities differ **per role** (enforced server-side); access is never granted "merely because the
user is staff" (WP §8.3). Without a known role every staff route returns 403.

| Role | Capabilities |
|------|--------------|
| `analyst` | view, triage, draft |
| `assurance` | view, triage, draft, review, approve |
| `authoriser` | view, send |

Each action-card transition requires a matching capability: `draft` to draft a card;
`review`/`approve` (assurance) to move it through independent review and approval; `send`
(authoriser) to dispatch — so **no single role can draft, approve and send the same card**. The
`/action-card/perform` route enforces this (403 when the role lacks the capability). Person-level
independence (reviewer ≠ author), real roles, purpose-binding and break-glass remain Wesley's IAM
decision (`RATIFY-15-06`, Section 16); this is a demonstration matrix. Actions never bypass the
action-card gates (§7).

## 6. Optional staff conversational surface (WP §8.4) — gated, not built

If added later, it may only map a question to a versioned metric/query registry, request
clarification, explain a registered metric with full denominator/vintage/uncertainty, and draft an
action card labelled `DRAFT`. It may not generate SQL, alter a threshold/release state, infer missing
values, approve/send an action, or contact a publisher. Until metric/scenario/action classes are
frozen and seeded-error tested, it stays deterministic navigation only.

## 7. Action-card workflow (WP §8.5)

Machine-checked in `packages/staff-ia/action-card-state-machine.json`
(`observed → investigated → drafted → independently_reviewed → approved_for_route →
sent_by_authorised_role → monitored → closed_or_withdrawn`, plus hold/rejected/withdrawn/
returned-for-more-evidence). `validate_action_cards.py` proves no transition skips independent review
or approval, sending requires an authorised role, and a public correction token can only create an
`observed` investigation candidate (never mutate evidence or contact a publisher).
