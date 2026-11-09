# C-13 — Privacy, telemetry & data-flow

**Owner (proposed):** Clarence **coordinates** the evidence · **Decides:** data-governance authority (`RATIFY-15-02/04`) — not Clarence (WP §2.4)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Basis: WP §12.4, §12.5, §13.3; C-BLOCK-07. Machine model: `packages/privacy/telemetry-dictionary.json`; validator: `validate_privacy.py`.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. Clarence
> maintains the evidence package; controller/processor and lawful-basis determinations are made by
> the named governance authority, never self-issued (WP §2.4).

## 1. Design commitment

**Transient-by-default from the first line of code** (C-BLOCK-07). The public core needs no account;
raw utterances, exact location and free text are **not fields** — the telemetry dictionary and the
event schema describe exactly the same fields, and `validate_privacy.py` fails if a forbidden concept
(`raw_utterance`, `exact_location`, `free_text`, `access_needs`, postcode, lat/lon, address) ever
becomes a field. Hashes of postcodes/access needs/staff ids are **not** treated as anonymous (WP §12.5).

## 2. Four information planes (WP §12.4)

| Plane | Contents |
|-------|----------|
| `restricted_source` | raw publisher/source evidence — never reachable by a public route |
| `public_service` | privacy-minimised public service surface |
| `staff_ops` | role-gated staff operations |
| `approved_research` | approved research data only |

No direct public route may reach the source archive, staff store or research store. **Any cross-plane
join requires a registered purpose, minimum fields, an authorised service, logging and an expiry.**

## 3. Data inventory (telemetry) — personal-data fields only

Of the 16 event fields, only two are personal-data and both are **transient**:

| Field | Why personal | Retention | Minimisation |
|-------|--------------|-----------|--------------|
| `episode_id` | correlates turns in a session | `transient` | pseudonymous/ephemeral; not a stable identifier; discarded with the session |
| `accessibility_mode` | special-category risk | `transient` | only if voluntarily and safely captured; never a disability identity |

Everything else (`condition_id`, `task_id`, `route`, state transitions, `duration_ms`, versions,
`envelope_digest`, codes) is operational metadata, no personal data. The full dictionary carries each
field's purpose, retention and minimisation.

## 4. Data-flow & trust boundaries

Public user → public_service (transient session state only) → **projected** `DecisionEnvelope`
(PUBLIC_SAFE only). Staff → staff_ops (role-gated) → staff projection. Research telemetry → only under
`approved_research` with an ethics route (C-15). The public issue/correction token carries
**references only** — no raw dialogue, no exact location (WP §9.4).

## 5. Model-provider data path

The base model is a pinned decision-log item; **no personal data leaves the service** in the current
design (transient state, no account). If a hosted API tier is chosen, its data path, region, retention
and training-opt-out must be verified and recorded **before** any personal-data transfer (`RATIFY-15-05`).
The conversational layer, when built, must render only verified tuples (C-BLOCK-10) and keep no chat
memory beyond the session.

## 6. Retention / deletion / rights

Retention classes: `transient` (default), `session`, `approved_research`, `operational_audit`.
Deletion/withdrawal: transient/session data expires with the session; approved-research data follows
the ethics-approved schedule with a verified deletion path. Data-subject correction/rights route via
the issue token; immutable audit archive is separated from erasable personal data.

## 7. DPIA screening (coordination, not a determination)

Screening indicators present: potential special-category signal (`accessibility_mode`), dialogue
logs, and (if hosted) a model data path. Screening therefore points to a **full DPIA required before
any human study or live telemetry collection**. Clarence prepares the DPIA evidence pack; the
governance authority screens and signs (`RATIFY-15-04`). Until then: **no telemetry collection** — the
no-study fallback (C-15/§13.5) keeps deterministic conformance, accessibility and replay evidence with
no participant claim.

## 8. Status / next
PROPOSED. Needs the governance controller/processor + lawful-basis determinations, the DPIA sign-off,
and the hosted-model data-path evidence if a hosted tier is chosen. The telemetry contract itself is
frozen and checked; collection stays off until those land.
