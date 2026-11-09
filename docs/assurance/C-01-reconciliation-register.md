# C-01 — Reconciliation decision register (all C-BLOCKs)

> **GENERATED FILE** — edit `reconciliation-register.json`, then run `python validate_register.py`. Do not hand-edit this markdown.

> **AI-ASSISTED SCAFFOLD (WP §3).** Not authorship evidence. Clarence takes the team decisions himself and obtains review; institutional cells marked `PENDING` must not be backfilled from memory after results are seen.

**Status:** PROPOSED · **Version:** 0.1.0-PROPOSED · **15 blockers** (14 core, 1 stretch)

## Priority order

| # | Blocker | Tier | Status | Chosen option (or PENDING) |
|---|---------|------|--------|-----------------------------|
| 1 | `C-BLOCK-05` | core | DRAFTED | one staff-complete schema + fail-closed class-driven projection + exec… |
| 2 | `C-BLOCK-15` | core | DRAFTED | terminal DecisionEnvelope evidence state (identical across conditions … |
| 3 | `C-BLOCK-09` | core | DRAFTED | executable evidence-symmetry / semantic-replay / value-level non-inter… |
| 4 | `C-BLOCK-14` | core | DRAFTED | freeze selected-slate / supported-pool / map-list parity / display-ord… |
| 5 | `C-BLOCK-10` | core | PARTIAL | prohibit unverified factual-token streaming; release verified claim ch… |
| 6 | `C-BLOCK-08` | core | PARTIAL | ratify horizon + explicit typed outside-horizon UI state |
| 7 | `C-BLOCK-01` | core | PROPOSED | ratify accountable owner + component split (parser/orchestrator/claim-… |
| 8 | `C-BLOCK-02` | core | PROPOSED | PENDING TEAM: ratify Clarence as integration lead + named public/staff… |
| 9 | `C-BLOCK-03` | core | PROPOSED | PENDING: name eligible non-author reviewer; external route if internal… |
| 10 | `C-BLOCK-04` | core | PROPOSED | name each authority through Section 15 |
| 11 | `C-BLOCK-06` | core | PROPOSED | freeze P0/P1/P2 and W0/W1/W1-NA sharing controlled backends/cases |
| 12 | `C-BLOCK-07` | core | PROPOSED | freeze telemetry dictionary + data-flow map + transient-by-default + r… |
| 13 | `C-BLOCK-11` | core | PROPOSED | freeze manual/browser/device/AT/low-bandwidth and non-map/no-chat test… |
| 14 | `C-BLOCK-12` | core | PROPOSED | end-to-end compatible local/authorised-staging research system |
| 15 | `C-BLOCK-13` | stretch | PROPOSED | Clarence owns only application/action-card integration until wider res… |

## Full dispositions

### C-BLOCK-05 — What are the frozen machine contracts for ApplicationEnvelope, terminal DecisionEnvelope, public/staff projections and field-level disclosure classes?
*Tier:* **core** · *Priority:* 1 · *Status:* DRAFTED (contracts + passing invariants in packages/application-contracts/c-block-05)

- **Options considered:** prose-only Section 14 contract; separate hand-maintained public and staff schemas; one staff-complete schema + fail-closed class-driven projection + executable invariants
- **Chosen:** one staff-complete schema + fail-closed class-driven projection + executable invariants
- **Rationale:** Single source of truth with a derived public view makes evidence symmetry and value-level non-interference provable (CA-1); fail-closed projection makes WP 15.2 hold by construction; digests give semantic replay.
- **Affected contracts:** application-envelope.schema.json, decision-envelope.schema.json, disclosure-classes.json, C-08, C-10, C-17
- **Owner:** Clarence (integration lead)  ·  **Approver:** PENDING: Michael (evidence semantics) + Wesley (transport/version/auth) at the contract workshop
- **Date:** PENDING: give this the FIRST date (CA-3)  ·  **Decision-log ref:** PENDING: bind to canonical decision-log ID
- **Tests required:** schema validation all variants, INV-DISCLOSURE, INV-NONINTERFERENCE, INV-SYMMETRY, INV-REPLAY, INV-NO-UNVERIFIED, INV-NO-COLLAPSE, INV-COVERAGE, INV-SLATE-ORDER, stable example hashes
- **Fallback if unresolved:** Build nothing UI-shaped; deterministic template rendering only over the DecisionEnvelope until schemas freeze.

### C-BLOCK-15 — What is the referent of L_reliance, given that P0 and P1 differ precisely in what is displayed (CA-1)?
*Tier:* **core** · *Priority:* 2 · *Status:* DRAFTED (disposition in docs/applications/C-BLOCK-05.md; blocker not yet opened jointly)

- **Options considered:** displayed-evidence referent (status quo — inverts the construct); terminal DecisionEnvelope evidence state (identical across conditions by design)
- **Chosen:** terminal DecisionEnvelope evidence state (identical across conditions by design)
- **Rationale:** A system must not be able to score 'safer by showing less'. Binding to the fixed terminal decision, enforced by INV-NONINTERFERENCE, measures reliance against the same evidence regardless of interface condition.
- **Affected contracts:** decision-envelope.schema.json, C-17, Fahmi evaluation stream
- **Owner:** PENDING: single named owner shared with Fahmi (also register as F-BLOCK-09)  ·  **Approver:** PENDING: Clarence + Fahmi joint, at ratification
- **Date:** PENDING  ·  **Decision-log ref:** PENDING: open jointly as C-BLOCK-15 / F-BLOCK-09
- **Tests required:** INV-NONINTERFERENCE, paired P0/P1/P2 identical DecisionEnvelope digest fixture
- **Fallback if unresolved:** Do not report any reliance result; measure only against the terminal decision state or withhold the claim.

### C-BLOCK-09 — How do we prevent a public and staff implementation silently diverging?
*Tier:* **core** · *Priority:* 3 · *Status:* DRAFTED (gates executable in C-BLOCK-05 package)

- **Options considered:** manual review of parity; executable evidence-symmetry / semantic-replay / value-level non-interference gates in CI
- **Chosen:** executable evidence-symmetry / semantic-replay / value-level non-interference gates in CI
- **Rationale:** Parity that is not executable is aspirational (WP sec 8). The gates already run over fixtures in the C-BLOCK-05 package.
- **Affected contracts:** projection_and_invariants.py, C-10
- **Owner:** Clarence  ·  **Approver:** PENDING: Michael + Wesley
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** INV-SYMMETRY, INV-REPLAY, INV-NONINTERFERENCE, CI job on every PR
- **Fallback if unresolved:** Ship public surface only via deterministic templates over the projected DecisionEnvelope.

### C-BLOCK-14 — How do we stop a map, client sort or browse fallback bypassing model abstention or the certified order?
*Tier:* **core** · *Priority:* 4 · *Status:* DRAFTED (INV-SLATE-ORDER passing)

- **Options considered:** trust client rendering; freeze selected-slate / supported-pool / map-list parity / display-order receipt rules and test them
- **Chosen:** freeze selected-slate / supported-pool / map-list parity / display-order receipt rules and test them
- **Rationale:** Client sort/map/pagination must never change eligibility or certified order; enforced by INV-SLATE-ORDER and the immutable ordered candidate list in the DecisionEnvelope.
- **Affected contracts:** decision-envelope.schema.json, projection_and_invariants.py, C-05, C-10
- **Owner:** Clarence  ·  **Approver:** PENDING: Michael + Wesley
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** INV-SLATE-ORDER, map/list same-ID parity fixture, client-sort cannot re-rank fixture
- **Fallback if unresolved:** List view only; no map, no client-side sort.

### C-BLOCK-10 — How do we stop the chatbot streaming an unsupported sentence before verification?
*Tier:* **core** · *Priority:* 5 · *Status:* PARTIAL (contract field + invariant exist; rendering pipeline not built)

- **Options considered:** stream free model text then post-check; prohibit unverified factual-token streaming; release verified claim chunks or deterministic templates only
- **Chosen:** prohibit unverified factual-token streaming; release verified claim chunks or deterministic templates only
- **Rationale:** Verify-before-render (section-8.3 clause 3); the verifier sits downstream of the model and only verification==verified claims render (INV-NO-UNVERIFIED).
- **Affected contracts:** decision-envelope.schema.json (claims[].verification), C-08
- **Owner:** Clarence (rendering) + Michael (verifier)  ·  **Approver:** PENDING: Michael (Section 09)
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** INV-NO-UNVERIFIED, token-stream gating test, template-only fallback test
- **Fallback if unresolved:** Deterministic template rendering only; no LLM in the response path.

### C-BLOCK-08 — How is schedule horizon and outside-horizon behaviour handled so it is never read as a non-match?
*Tier:* **core** · *Priority:* 6 · *Status:* PARTIAL (contract carries the state; horizon value unratified)

- **Options considered:** treat outside-horizon as no-match (prohibited); ratify horizon + explicit typed outside-horizon UI state
- **Chosen:** ratify horizon + explicit typed outside-horizon UI state
- **Rationale:** Outside-horizon must fail to a typed state, never a false negative; the DecisionEnvelope's scope_qualifier and coverage_qualifier carry it.
- **Affected contracts:** decision-envelope.schema.json (scope_qualifier, coverage_qualifier), C-05
- **Owner:** Michael/Wesley (horizon evidence) + Clarence (presentation)  ·  **Approver:** PENDING: Michael
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** outside-horizon renders as typed state not bounded_non_match, INV-COVERAGE
- **Fallback if unresolved:** Show scope_indeterminate and withhold any non-match claim outside the ratified horizon.

### C-BLOCK-01 — Who is the accountable Section 08 (chatbot) owner, and what is the component-level split?
*Tier:* **core** · *Priority:* 7 · *Status:* PROPOSED (team decision)

- **Options considered:** leave implicit (prohibited — CA-4); ratify accountable owner + component split (parser/orchestrator/claim-contract/model-runtime/evaluation) bound to a real decision-log ID
- **Chosen:** ratify accountable owner + component split (parser/orchestrator/claim-contract/model-runtime/evaluation) bound to a real decision-log ID
- **Rationale:** Section 08 has no RATIFY-08-* register; the decision must bind to a real canonical ID before Phase A closes (CA-4). Clarence's defensible wording stays 'conversational-UX & application-integration owner' until then.
- **Affected contracts:** C-08, C-01 ownership/RACI
- **Owner:** PENDING TEAM (Clarence coordinates the conversational-UX component only)  ·  **Approver:** PENDING: team ratification
- **Date:** PENDING: before Phase A closes  ·  **Decision-log ref:** PENDING: create canonical decision-log ID (do NOT invent RATIFY-08-*)
- **Tests required:** ownership recorded in decision log, component owners named
- **Fallback if unresolved:** Clarence builds only the conversational-UX/presentation component; no claim to chatbot ownership.

### C-BLOCK-02 — Is Clarence integration lead for both applications, or are there separate public/staff product owners?
*Tier:* **core** · *Priority:* 8 · *Status:* PROPOSED (team decision)

- **Options considered:** Clarence owns both (Section 19 as written); Clarence integration lead + named public/staff product leads; explicitly amend the allocation
- **Chosen:** PENDING TEAM: ratify Clarence as integration lead + named public/staff product leads OR amend
- **Rationale:** Section 19 vs the crosswalk disagree; do not invent the answer in code (RATIFY-19-06 seen from Clarence's side).
- **Affected contracts:** C-01 ownership/RACI
- **Owner:** PENDING TEAM  ·  **Approver:** PENDING: RATIFY-19-06
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** allocation recorded
- **Fallback if unresolved:** Clarence proceeds as integration lead; product-lead gaps recorded as open.

### C-BLOCK-03 — Who is the eligible non-author HCI/accessibility reviewer of Clarence's applications (RATIFY-14-02)?
*Tier:* **core** · *Priority:* 9 · *Status:* PROPOSED (team decision)

- **Options considered:** Clarence reviews own work (prohibited — WP 2.6); name an internal eligible non-author reviewer; use an external accessibility reviewer if internal independence is inadequate
- **Chosen:** PENDING: name eligible non-author reviewer; external route if internal independence inadequate
- **Rationale:** Clarence cannot be RATIFY-14-02; accessibility conformance needs independent evidence (C-BLOCK-11).
- **Affected contracts:** C-11, C-12, C-04
- **Owner:** PENDING TEAM  ·  **Approver:** PENDING: RATIFY-14-02
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** reviewer scope/competence recorded
- **Fallback if unresolved:** Report technical accessibility inspection only; make no conformance claim.

### C-BLOCK-04 — Who holds the Section 15 operational authorities (service, data-governance, security, ethics-route, incident, partner, residual-risk)?
*Tier:* **core** · *Priority:* 10 · *Status:* PROPOSED (institutional)

- **Options considered:** leave unassigned (prohibited); name each authority through Section 15
- **Chosen:** name each authority through Section 15
- **Rationale:** Clarence coordinates but cannot issue these determinations (WP 2.4). An orphan authority blocks the affected maturity state.
- **Affected contracts:** C-15, C-16
- **Owner:** PENDING: Section 15 authorities  ·  **Approver:** PENDING: RATIFY-15-01..12
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** authority map has no orphan use/harm/control/reviewer
- **Fallback if unresolved:** Maturity stays research_demonstration; no public/pilot exposure.

### C-BLOCK-06 — How do we stop application effects being confounded with retrieval/ranking/content differences?
*Tier:* **core** · *Priority:* 11 · *Status:* PROPOSED

- **Options considered:** compare whole systems; freeze P0/P1/P2 and W0/W1/W1-NA sharing controlled backends/cases
- **Chosen:** freeze P0/P1/P2 and W0/W1/W1-NA sharing controlled backends/cases
- **Rationale:** Isolates the interface/conversation effect at matched backend semantics (WP 13.1); enables CA-1's shared referent. Fahmi owns the estimands and analysis; Clarence builds the controlled conditions.
- **Affected contracts:** C-17, Fahmi evaluation stream
- **Owner:** Clarence (builds) + Fahmi (estimands/analysis)  ·  **Approver:** PENDING: RATIFY-14-07
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** condition manifests share backend, identical DecisionEnvelope across P0/P1/P2 fixture
- **Fallback if unresolved:** No cross-condition effect claim; report per-condition descriptives only.

### C-BLOCK-07 — How do we stop exact origin, raw dialogue and preference memory becoming persistent personal data through telemetry?
*Tier:* **core** · *Priority:* 12 · *Status:* PROPOSED

- **Options considered:** log freely and redact later; freeze telemetry dictionary + data-flow map + transient-by-default + retention/deletion + hosted-model data path before collection
- **Chosen:** freeze telemetry dictionary + data-flow map + transient-by-default + retention/deletion + hosted-model data path before collection
- **Rationale:** Design transient-by-default from the first line of code; coarsened_origin only, no raw utterance/exact location in telemetry (WP 12.5, 13.3).
- **Affected contracts:** C-13, application-envelope.schema.json (coarsened_origin)
- **Owner:** Clarence (coordinates) + Wesley (implements) + governance authority (decides)  ·  **Approver:** PENDING: RATIFY-15-04 / governance
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** telemetry schema forbids raw utterance/exact location, retention/deletion exercise
- **Fallback if unresolved:** No telemetry collection; deterministic conformance evidence only.

### C-BLOCK-11 — How do we avoid mistaking WCAG scanning for accessibility validation?
*Tier:* **core** · *Priority:* 13 · *Status:* PROPOSED

- **Options considered:** automated scan only (prohibited as validation); freeze manual/browser/device/AT/low-bandwidth and non-map/no-chat test matrices
- **Chosen:** freeze manual/browser/device/AT/low-bandwidth and non-map/no-chat test matrices
- **Rationale:** One examiner-found failure falsifies a conformance claim; scoped, dated, self-evaluated matrices survive (WP 11).
- **Affected contracts:** C-11, C-12
- **Owner:** Clarence (builds) + non-author HCI reviewer (evaluates)  ·  **Approver:** PENDING: RATIFY-14-09 / C-BLOCK-03 reviewer
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** manual keyboard/focus, screen-reader matrix, zoom/reflow/contrast, no-map/no-chat route
- **Fallback if unresolved:** Claim 'evaluated toward WCAG 2.2 AA within the tested matrix' only.

### C-BLOCK-12 — What does 'functioning' mean, so it is not misread as public production deployment?
*Tier:* **core** · *Priority:* 14 · *Status:* PROPOSED

- **Options considered:** public internet deployment; end-to-end compatible local/authorised-staging research system
- **Chosen:** end-to-end compatible local/authorised-staging research system
- **Rationale:** Public internet deployment requires separate Section 15/16 maturity gates; do not call a staging build a public deployment (WP 12.9, 19.3).
- **Affected contracts:** C-12, C-16, release_maturity_class enum
- **Owner:** Clarence + Wesley  ·  **Approver:** PENDING: Section 15/16 authority
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** clean-room build/run from manifest, maturity label matches environment
- **Fallback if unresolved:** Keep maturity at research_demonstration.

### C-BLOCK-13 — Who owns and reviews the Section 18 partner pathway?
*Tier:* **stretch** · *Priority:* 15 · *Status:* PROPOSED

- **Options considered:** Clarence owns the whole partner pathway; Clarence owns only application/action-card integration until wider responsibility is ratified
- **Chosen:** Clarence owns only application/action-card integration until wider responsibility is ratified
- **Rationale:** Section 18 has no RATIFY-18-* register; bound scope until named (WP 2.5, C-BLOCK-13).
- **Affected contracts:** C-18
- **Owner:** PENDING TEAM (Clarence: action-card UI integration only)  ·  **Approver:** PENDING: Section 18 owner
- **Date:** PENDING  ·  **Decision-log ref:** PENDING
- **Tests required:** action-card state machine cannot skip approval
- **Fallback if unresolved:** No partner-pathway ownership claim; integration surface only.

