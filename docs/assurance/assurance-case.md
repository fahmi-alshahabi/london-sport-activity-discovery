# C-16 — Executable assurance case

> **GENERATED** — edit `assurance-case.json`, then run `python validate_assurance.py`.

> **AI-ASSISTED SCAFFOLD (WP §12.1).** Executable tests are run live below. Reviewer and authority gates are human and PENDING; an authorised person — not Clarence — records the maturity decision (WP §12.9).

**Status:** PROPOSED · **Maturity target:** research_demonstration · **15 claims**

## Linked test results (live)

| Test | Result | Command |
|------|--------|---------|
| `T-contracts` | ✅ pass | `python3 packages/application-contracts/c-block-05/projection_and_invariants.py` |
| `T-checker` | ✅ pass | `python3 packages/certificate-checker/test_certificate_checker.py` |
| `T-register` | ✅ pass | `python3 docs/assurance/validate_register.py` |
| `T-wording` | ✅ pass | `python3 packages/accessible-design-system/content/render_lint.py` |
| `T-ia` | ✅ pass | `python3 packages/public-ia/validate_ia.py` |
| `T-actioncard` | ✅ pass | `python3 packages/staff-ia/validate_action_cards.py` |
| `T-conditions` | ✅ pass | `python3 packages/evaluation/validate_conditions.py` |
| `T-publicslice` | ✅ pass | `python3 apps/public-discovery/test_slice.py` |
| `T-staffslice` | ✅ pass | `python3 apps/staff-assurance/test_staff.py` |
| `T-privacy` | ✅ pass | `python3 packages/privacy/validate_privacy.py` |
| `T-ethics` | ✅ pass | `python3 packages/ethics/validate_ethics.py` |
| `T-security` | ✅ pass | `python3 packages/security/validate_security.py` |
| `T-conversation` | ✅ pass | `python3 apps/public-discovery/test_conversation.py` |
| `T-reading` | ✅ pass | `python3 docs/assurance/validate_foundation_matrix.py` |

## Claims → controls → evidence → maturity

### CL-1 — Public and staff surfaces never disagree on the retained decision, and restricted staff values cannot change public output.
*Permitted wording:* evidence-symmetric but authority-asymmetric applications with value-level non-interference
- **Affected / harm:** public users and London Sport staff — leaked staff information, or public/staff disagreement that misleads a decision
- **Controls:** K-noninterference (Clarence)
- **Evidence (tests):** T-contracts ✅, T-staffslice ✅, T-publicslice ✅
- **Reviewer:** evidence semantics + transport — conditions
- **Authority:** public_safe_demonstration gate — pending
- **Residual risk:** person-level review of projections outstanding
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-2 — Missing or unknown evidence is never rendered as a negative fact.
*Permitted wording:* unknown is rendered as 'not published', never as 'no' or 'free'
- **Affected / harm:** public users — user misled into believing an activity is unavailable/free when the data is simply silent
- **Controls:** K-nocollapse (Clarence)
- **Evidence (tests):** T-wording ✅, T-contracts ✅, T-publicslice ✅
- **Reviewer:** content / HCI — pending
- **Authority:** content sign-off — pending
- **Residual risk:** wording to be corrected in Clarence's own words + reviewed
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-3 — No unsupported factual token reaches a user.
*Permitted wording:* verify-before-render; only verified claims are rendered
- **Affected / harm:** public users — a fluent but unsupported statement is believed
- **Controls:** K-verify (Clarence + Michael)
- **Evidence (tests):** T-contracts ✅, T-checker ✅
- **Reviewer:** evidence semantics (Section 09) — conditions
- **Authority:** Section 09 vocabulary ratification — pending
- **Residual risk:** conversational renderer not yet built
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-4 — The interface preserves the certified slate and order; client controls cannot bypass abstention.
*Permitted wording:* map/list/sort preserve the certified slate and order
- **Affected / harm:** public users — a re-ordered or padded list presents a non-certified result as certified
- **Controls:** K-order (Clarence)
- **Evidence (tests):** T-contracts ✅, T-ia ✅, T-publicslice ✅
- **Reviewer:** HCI / evaluation parity — pending
- **Authority:** public_safe_demonstration gate — pending
- **Residual risk:** none known within tested routes
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-5 — Restricted staff information cannot leak to the public plane; staff access is role-gated.
*Permitted wording:* one-way disclosure; role-appropriate presentation
- **Affected / harm:** publishers, staff, public users — receipts/lineage/aggregates or research identity exposed publicly
- **Controls:** K-disclosure (Clarence + Wesley)
- **Evidence (tests):** T-contracts ✅, T-staffslice ✅, T-publicslice ✅
- **Reviewer:** security / IAM — conditions
- **Authority:** security review + RATIFY-15-06 — pending
- **Residual risk:** real IAM/break-glass is Wesley's; role gate here is a stub
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-6 — Forged, stale, swapped or illegally escalated evidence is rejected by an independent checker.
*Permitted wording:* limited technical independence certificate checker
- **Affected / harm:** public users, London Sport — a wrong production decision is trusted
- **Controls:** K-checker (Clarence)
- **Evidence (tests):** T-checker ✅
- **Reviewer:** non-author code review + Section 09 contract — conditions
- **Authority:** RATIFY-09-04 — pending
- **Residual risk:** production/reference/checker discrepancy register empty until production emits certificates
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-7 — Application effects are not confounded with retrieval, ranking or content differences.
*Permitted wording:* shared-backend P0/P1/P2 and W0/W1/W1-NA conditions
- **Affected / harm:** the evaluation / research claim — an interface effect is falsely attributed, invalidating a headline result
- **Controls:** K-conditions (Clarence (build); Fahmi (estimands))
- **Evidence (tests):** T-conditions ✅
- **Reviewer:** evaluation design (Fahmi) — done
- **Authority:** RATIFY-14-07/08 + ethics route — pending
- **Residual risk:** RATIFY-14-07/08 withheld by Fahmi. M-6 CLOSED (Fahmi verified 2026-08-23 at commit 21c788b: envelope_digest required, event-schema v0.2.0-PROPOSED). M-2 OPEN and is the sole remaining blocker (shared terminal referent must be produced and verified by the evidence engine). Ethics via no-study fallback.
- **Maturity verdict:** BLOCKED  — blocked on: authority decision pending

### CL-8 — Governed actions cannot skip independent review or approval, and sending requires an authorised role.
*Permitted wording:* action-card workflow with separated review/approval/send
- **Affected / harm:** publishers, London Sport — an unreviewed or unauthorised action is sent to a publisher
- **Controls:** K-actioncard (Clarence)
- **Evidence (tests):** T-actioncard ✅, T-staffslice ✅
- **Reviewer:** Section 18 partner route — pending
- **Authority:** Section 18 owner — pending
- **Residual risk:** person-level independence (reviewer != author) needs real IAM
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-9 — All pre-code reconciliation blockers are dispositioned with owner, tests and fallback.
*Permitted wording:* reconciliation register per WP §3
- **Affected / harm:** the team / examiner — a release-blocking ambiguity is hidden beneath an implementation choice
- **Controls:** K-register (Clarence)
- **Evidence (tests):** T-register ✅
- **Reviewer:** team ratification — pending
- **Authority:** team ratification (RATIFY-19-04) — pending
- **Residual risk:** institutional cells remain PENDING until ratified
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-10 — The applications are evaluated toward WCAG 2.2 AA within a stated, tested matrix (not a blanket conformance claim).
*Permitted wording:* evaluated toward WCAG 2.2 AA within the tested matrix
- **Affected / harm:** disabled users — an accessibility barrier prevents a tested route for material users
- **Controls:** K-a11y (Clarence)
- **Evidence (tests):** T-publicslice ✅, T-staffslice ✅
- **Reviewer:** non-author HCI/accessibility reviewer (C-BLOCK-03) — pending
- **Authority:** RATIFY-14-02 + accessibility statement — pending
- **Residual risk:** manual keyboard/screen-reader/AT/contrast testing OUTSTANDING; automated subset is one input only
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-11 — Telemetry is transient-by-default and cannot carry raw utterances, exact location or free text.
*Permitted wording:* privacy-minimised, transient-by-default telemetry
- **Affected / harm:** public users and staff — creation of persistent personal data through ordinary telemetry
- **Controls:** K-telemetry (Clarence (coord) + Wesley + governance)
- **Evidence (tests):** T-privacy ✅
- **Reviewer:** data governance / DPIA — pending
- **Authority:** RATIFY-15-02/04 (governance) — pending
- **Residual risk:** controller/processor + lawful basis + DPIA sign-off outstanding; no collection until then
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-12 — Every human-facing activity is ethically gated with a fallback, and no human-effect claim is made without approval.
*Permitted wording:* ethics activity matrix with a no-study fallback
- **Affected / harm:** participants and the public — human-participant data used without approval, or an over-claim about lived effect
- **Controls:** K-ethics (Clarence (coord))
- **Evidence (tests):** T-ethics ✅
- **Reviewer:** Bristol PGT ethics route — pending
- **Authority:** RATIFY-15-03 (PGT ethics) — pending
- **Residual risk:** ethics determination outstanding; operating under the no-study fallback
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-13 — Application-facing security controls neutralise injection and unsafe output, and no secret is committed.
*Permitted wording:* application-facing security controls with a threat register
- **Affected / harm:** public users, staff, publishers — formula/HTML/URL injection, receipt forgery, or a committed secret
- **Controls:** K-security (Clarence (app) + Wesley (infra))
- **Evidence (tests):** T-security ✅, T-checker ✅
- **Reviewer:** security / assurance reviewer — pending
- **Authority:** RATIFY-15-07 (security) — pending
- **Residual risk:** infra controls (rate limits, headers, egress, SBOM, deletion) are Wesley's and planned; injection battery pending the conversational layer
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

### CL-14 — The conversational route interprets and communicates but never decides truth: it converges on the same certified decision as guided search, confirms high-consequence constraints, renders only verified claims, and degrades safely.
*Permitted wording:* evidence-contract conversation; chat and non-chat converge on compatible terminal semantics
- **Affected / harm:** public users — a chatbot asserts an unsupported fact or diverges from the certified decision
- **Controls:** K-conversation (Clarence (UX) + Michael (verifier))
- **Evidence (tests):** T-conversation ✅, T-contracts ✅
- **Reviewer:** Section 08 owner + evidence semantics — done
- **Authority:** Section 08 ownership + RATIFY-09-05 — pending
- **Residual risk:** LLM parse/verbalise not yet integrated; Section 08 accountable owner unresolved (C-BLOCK-01)
- **Maturity verdict:** BLOCKED  — blocked on: authority decision pending

### CL-15 — Every load-bearing source is attested to K7 — personally read, bound to a verified version-of-record DOI, with Clarence's own verdict — before it carries a claim.
*Permitted wording:* K7 per-claim primary-source attestation (WP §18.3, CA-5)
- **Affected / harm:** the academic claim and the examiner — a load-bearing citation is asserted from a theme or surname cluster without the primary source being read and version-verified
- **Controls:** K-k7 (Clarence)
- **Evidence (tests):** T-reading ✅
- **Reviewer:** non-author check that attested records match the primary sources — pending
- **Authority:** K7 attestation complete + Clarence's §26 acceptance record — pending
- **Residual risk:** attestation incomplete — reading is Clarence's ongoing task; reading-log.md reports the live n/28 count and --strict makes full attestation a hard gate
- **Maturity verdict:** BLOCKED  — blocked on: non-author review pending; authority decision pending

