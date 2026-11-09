# C-17 — Frozen evaluation conditions (P0/P1/P2, W0/W1/W1-NA)

**Owner (proposed):** Clarence builds the frozen conditions; **Fahmi owns** estimands, sampling, annotation and analysis (`RATIFY-14-07/08`).
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Resolves **C-BLOCK-06**; binds **CA-1 / C-BLOCK-15**. Basis: WP §13.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. Frozen
> instruments are handed to Fahmi; Clarence must not inspect locked outcomes and then change
> treatment (WP §13.4).

## 1. The guarantee this delivers (C-BLOCK-06)

Application effects must not be confounded with retrieval/ranking/content differences. So **within a
surface family, every condition resolves the identical terminal `DecisionEnvelope` per task** — only
the interface/interaction differs. `validate_conditions.py` proves this by projected-digest equality
across the family, and **detects a confound** (a condition pointed at a different scenario) as a
failure. Because the decision is shared, **CA-1's `L_reliance` referent is the same across
conditions** — a system cannot look "safer by showing less."

## 2. Public conditions (WP §13.1)

| Condition | Interface | Estimates |
|-----------|-----------|-----------|
| `P0` | incumbent-informed structured finder / list control (same backend) | comparator baseline — **not** direct Get Active/imin superiority unless a direct controlled comparison is run |
| `P1` | evidence-aware guided/list interface, identical terminal semantics | evidence-communication / interface effect vs P0 |
| `P2` | P1 + conversational clarification / query repair | combined conversational repair/clarification increment vs P1 |

`P0/P1/P2` are demonstrated in the public app via `?condition=` — the **same** candidates in the
**same certified order**; P0 is list-only, P1 adds evidence communication, P2 adds a conversational
affordance. **Identification honesty:** `P2 − P1` is not a same-envelope cosmetic effect if
conversation changes the interpreted query; any such change is recorded as a different task/decision,
never silently (WP §13.1).

## 3. Staff conditions (WP §13.2)

| Condition | Build |
|-----------|-------|
| `W0` | versioned static evidence report / credible generic-dashboard control over identical cases |
| `W1` | full staff assurance workbench |
| `W1-NA` | W1 without the optional natural-language staff assistant |

`W1` is the built staff app; `W1-NA` is W1 with the NL assistant capability off; `W0` is the static
control. The manifest checks `W1-NA = W1 − nl_assistant`.

## 4. Instrumentation (WP §13.3, C-BLOCK-07)

`event-schema.json` defines a privacy-minimised event (`condition_id`, `task_id`, ephemeral
`episode_id`, `envelope_digest`, route, state transitions, `duration_ms`, `retention_class`,
`purpose`). `additionalProperties:false` makes it **impossible to log raw utterances, exact location
or free text** — the validator confirms a `raw_utterance` field is rejected. Transient-by-default;
binds to governance (`RATIFY-14-11`) before any collection.

## 5. Tuning freeze & no-study fallback

**Freeze (§13.4):** treatment wording/layout/logic freezes before locked exposure; post-freeze
accessibility/security repairs are classified and, if they change semantics/flow, the affected
conditions are versioned and re-run. **No-study fallback (§13.5):** if ethics/recruitment/readiness
fails, retain deterministic conformance, accessibility/AT, semantic-replay / non-interference /
security tests; remove usability, actionability, organisational-effectiveness and lived-equity claims.

## 6. Handoff to Fahmi

Frozen artefacts: `condition-manifest.json` (the six conditions + task bindings + capability licence),
`event-schema.json` (telemetry contract), and the two running apps (`P1`, `W1`) with condition flags.
Fahmi owns the estimands (e.g. Δ over `A(q,S1b)−A(q,S0)`), sampling, adjudication and analysis; this
package supplies the confound-free, digest-shared conditions those estimands are computed over.
